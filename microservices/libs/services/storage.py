import asyncio
import json
import logging
import time
import uuid
from typing import Any, Dict, Optional

import httpx
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from fastapi import HTTPException
from prometheus_client import Gauge

from microservices.libs.schemas.shard import ReplicationMessage


class StorageService:
    def __init__(
            self,
            router_service_url: str,
            advertised_url: str,
            group_id: str,
            is_leader: bool,
            kafka_broker_url: str,
            kafka_topic: str,
            logger: logging.Logger
    ):
        self.router_service_url = router_service_url
        self.advertised_url = advertised_url
        self.group_id = group_id
        self.is_leader = is_leader
        self.kafka_broker_url = kafka_broker_url
        self.kafka_topic = kafka_topic
        self.logger = logger
        self._data_store: Dict[str, Dict[str, Dict[str, Any]]] = {}

        self.producer: Optional[AIOKafkaProducer] = None
        self.consumer: Optional[AIOKafkaConsumer] = None
        self._consumer_task: Optional[asyncio.Task] = None

    async def start(self):
        if self.is_leader:
            self.producer = AIOKafkaProducer(bootstrap_servers=self.kafka_broker_url)
            await self.producer.start()
            self.logger.info(f"Leader started. Writing to topic: {self.kafka_topic}")
        else:
            unique_group = f"shard-{self.group_id}-{uuid.uuid4()}"
            self.consumer = AIOKafkaConsumer(
                self.kafka_topic,
                bootstrap_servers=self.kafka_broker_url,
                group_id=unique_group,
                auto_offset_reset="earliest"
            )
            await self.consumer.start()
            self._consumer_task = asyncio.create_task(self._replication_loop())
            self.logger.info(f"Follower started. Listening on topic: {self.kafka_topic}")

    async def stop(self):
        if self.producer:
            await self.producer.stop()
        if self.consumer:
            await self.consumer.stop()
        if self._consumer_task:
            self._consumer_task.cancel()
            try:
                await self._consumer_task
            except asyncio.CancelledError:
                pass

    async def _replication_loop(self):
        try:
            async for msg in self.consumer:
                try:
                    data = json.loads(msg.value.decode("utf-8"))
                    message = ReplicationMessage(**data)
                    self._apply_update(message)
                except Exception as e:
                    self.logger.error(f"Failed to process replication message: {e}")
        except asyncio.CancelledError:
            pass

    def _apply_update(self, msg: ReplicationMessage):
        if msg.table_name not in self._data_store:
            self._data_store[msg.table_name] = {}

        existing_record = self._data_store[msg.table_name].get(msg.primary_key)

        if existing_record:
            if msg.timestamp <= existing_record["timestamp"]:
                self.logger.info(f"[LWW] Ignoring stale update for {msg.table_name}/{msg.primary_key}")
                return

        if msg.operation == "create":
            self._data_store[msg.table_name][msg.primary_key] = {
                "value": msg.value.get("value"),
                "timestamp": msg.timestamp
            }
            self.logger.info(f"[REPLICA] Applied CREATE {msg.table_name}/{msg.primary_key}")
        elif msg.operation == "delete":
            if msg.primary_key in self._data_store[msg.table_name]:
                del self._data_store[msg.table_name][msg.primary_key]
                self.logger.info(f"[REPLICA] Applied DELETE {msg.table_name}/{msg.primary_key}")

        lag = (time.time_ns() - msg.timestamp) / 1e9
        Gauge('shard_replication_lag_seconds', 'Lag between leader and follower').set(lag + 10)

    async def create_record(self, table_name: str, primary_key: str, value: Any) -> Any:
        if not self.is_leader:
            raise HTTPException(
                status_code=400,
                detail="Write operations allowed only on Leader"
            )

        if table_name not in self._data_store:
            self._data_store[table_name] = {}

        # if primary_key in self._data_store[table_name]:
        #     raise HTTPException(
        #         status_code=409,
        #         detail=f"Record with key '{primary_key}' already exists in table '{table_name}'"
        #     )

        timestamp = time.time_ns()

        self._data_store[table_name][primary_key] = {
            "value": value,
            "timestamp": timestamp
        }

        msg = ReplicationMessage(
            operation="create",
            table_name=table_name,
            primary_key=primary_key,
            value={"value": value},
            timestamp=timestamp
        )
        await self.producer.send_and_wait(self.kafka_topic, json.dumps(msg.model_dump()).encode("utf-8"))

        self.logger.info(f"Created record '{primary_key}' in table '{table_name}'")
        return value

    def read_record(self, table_name: str, primary_key: str) -> Any:
        if table_name not in self._data_store or primary_key not in self._data_store[table_name]:
            raise HTTPException(
                status_code=404,
                detail=f"Record '{primary_key}' not found in table '{table_name}'"
            )
        return self._data_store[table_name][primary_key]["value"]

    async def delete_record(self, table_name: str, primary_key: str):
        if not self.is_leader:
            raise HTTPException(
                status_code=400,
                detail="Write operations allowed only on Leader"
            )

        if table_name not in self._data_store or primary_key not in self._data_store[table_name]:
            raise HTTPException(
                status_code=404,
                detail=f"Record '{primary_key}' not found in table '{table_name}'"
            )

        timestamp = time.time_ns()
        del self._data_store[table_name][primary_key]

        msg = ReplicationMessage(
            operation="delete",
            table_name=table_name,
            primary_key=primary_key,
            timestamp=timestamp
        )
        await self.producer.send_and_wait(self.kafka_topic, json.dumps(msg.model_dump()).encode("utf-8"))

        self.logger.info(f"Deleted record '{primary_key}' from table '{table_name}'")

    def exists_record(self, table_name: str, primary_key: str) -> bool:
        if table_name not in self._data_store:
            return False
        return primary_key in self._data_store[table_name]

    async def register_self(self):
        payload = {
            "shard_url": self.advertised_url,
            "group_id": self.group_id,
            "is_leader": self.is_leader
        }
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{self.router_service_url}/_internal/register_shard",
                    json=payload,
                    timeout=5
                )
            self.logger.info(
                f"Successfully registered at router: {self.router_service_url} as {'Leader' if self.is_leader else 'Follower'}")
        except httpx.RequestError:
            self.logger.error("Could not register at router after all attempts")
