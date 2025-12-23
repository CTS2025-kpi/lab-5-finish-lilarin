import asyncio
import json
import logging
from typing import Dict, List, Any, Optional

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from fastapi import HTTPException

from microservices.libs.schemas.filter import UpdateRecord


class FilterService:
    def __init__(self, kafka_broker_url: str, logger: logging.Logger):
        self.kafka_broker_url = kafka_broker_url
        self.logger = logger
        self._updated_items: Dict[str, List[Dict[str, Any]]] = {}
        self.kafka_consumer: Optional[AIOKafkaConsumer] = None
        self.kafka_producer: Optional[AIOKafkaProducer] = None
        self._consumer_task: Optional[asyncio.Task] = None

    async def start_consumer(self):
        self.kafka_consumer = AIOKafkaConsumer(
            "collection-updates",
            bootstrap_servers=self.kafka_broker_url,
            group_id="filter_group",
            auto_offset_reset="earliest",
        )
        self.kafka_producer = AIOKafkaProducer(
            bootstrap_servers=self.kafka_broker_url
        )

        self.logger.info("Starting Kafka consumer and producer...")
        await self.kafka_consumer.start()
        await self.kafka_producer.start()

        self._consumer_task = asyncio.create_task(self.consume_updates())
        self.logger.info("Kafka consumer and producer started.")

    async def stop_consumer(self):
        self.logger.info("Stopping Kafka components...")
        if self._consumer_task:
            self._consumer_task.cancel()
            try:
                await self._consumer_task
            except asyncio.CancelledError:
                pass

        if self.kafka_consumer:
            await self.kafka_consumer.stop()
        if self.kafka_producer:
            await self.kafka_producer.stop()

        self.logger.info("Kafka components stopped.")

    async def consume_updates(self):
        try:
            async for msg in self.kafka_consumer:
                try:
                    data = json.loads(msg.value.decode("utf-8"))
                    item_id = data.get("item_id")
                    tag = data.get("tag")

                    if tag == "error":
                        raise ValueError("Simulated failure: Invalid tag 'error'")

                    if item_id:
                        self.logger.info(f"Received update for item {item_id}: {data}")
                        if item_id not in self._updated_items:
                            self._updated_items[item_id] = []
                        self._updated_items[item_id].append(data)

                except ValueError as ve:
                    self.logger.error(f"Business logic error: {ve}")
                    await self._send_compensation(data, str(ve))

                except Exception as e:
                    self.logger.error(f"An error occurred in consumer: {e}")

        except asyncio.CancelledError:
            self.logger.info("Consumer task was cancelled.")

    async def _send_compensation(self, original_data: Dict[str, Any], reason: str):
        if not self.kafka_producer:
            self.logger.error("Producer not initialized, cannot send compensation.")
            return

        compensation_msg = {
            "item_id": original_data.get("item_id"),
            "tag": original_data.get("tag"),
            "action": "TAG_ADD_FAILED",
            "reason": reason
        }

        try:
            await self.kafka_producer.send_and_wait(
                "collection-compensations",
                json.dumps(compensation_msg).encode("utf-8")
            )
            self.logger.info(f"Sent compensation event: {compensation_msg}")
        except Exception as e:
            self.logger.error(f"Failed to send compensation event: {e}")

    def get_updates_for_item(self, item_id: str) -> List[UpdateRecord]:
        if item_id not in self._updated_items:
            raise HTTPException(status_code=404, detail=f"No updates found for item {item_id}")

        return [UpdateRecord(action=rec.get("action", "unknown"), details=rec) for rec in self._updated_items[item_id]]
