import asyncio
import json
import logging

import httpx
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from fastapi import HTTPException
from microservices.libs.schemas.collections import AddTagRequest


class CollectionsService:
    def __init__(self, kafka_broker_url: str, tags_service_url: str, logger: logging.Logger):
        self.kafka_broker_url = kafka_broker_url
        self.tags_service_url = tags_service_url
        self.logger = logger
        self._fake_items_db = {
            "123": {"name": "My First Movie", "tags": ["classic", "drama"]},
            "456": {"name": "Another Movie", "tags": []}
        }
        self._outbox = []
        self.kafka_producer: AIOKafkaProducer | None = None
        self.kafka_consumer: AIOKafkaConsumer | None = None

    async def initialize_kafka_producer(self):
        try:
            self.kafka_producer = AIOKafkaProducer(
                bootstrap_servers=self.kafka_broker_url
            )
            await self.kafka_producer.start()
            self.logger.info("Kafka producer started successfully.")
        except Exception as e:
            self.logger.error(f"Failed to start Kafka producer: {e}")
            self.kafka_producer = None

    async def initialize_kafka_consumer(self):
        try:
            self.kafka_consumer = AIOKafkaConsumer(
                "collection-compensations",
                bootstrap_servers=self.kafka_broker_url,
                group_id="collections_saga_group",
                auto_offset_reset="earliest"
            )
            await self.kafka_consumer.start()
            self.logger.info("Kafka consumer started successfully.")
        except Exception as e:
            self.logger.error(f"Failed to start Kafka consumer: {e}")
            self.kafka_consumer = None

    async def stop_kafka_components(self):
        if self.kafka_producer:
            await self.kafka_producer.stop()
            self.logger.info("Kafka producer stopped.")
        if self.kafka_consumer:
            await self.kafka_consumer.stop()
            self.logger.info("Kafka consumer stopped.")

    def get_item_tags(self, item_id: int) -> list[str]:
        item_id_str = str(item_id)
        if item_id_str not in self._fake_items_db:
            raise HTTPException(status_code=404, detail="Item not found")
        return self._fake_items_db[item_id_str].get("tags", [])

    async def add_tag_to_item(self, item_id: int, payload: AddTagRequest) -> str:
        item_id_str = str(item_id)
        if item_id_str not in self._fake_items_db:
            raise HTTPException(status_code=404, detail="Item not found")

        new_tag = payload.tag_name
        if new_tag in self._fake_items_db[item_id_str]["tags"]:
            raise HTTPException(
                status_code=409,
                detail=f"Tag '{new_tag}' already exists on item {item_id_str}."
            )

        await self._validate_tag_with_service(new_tag)

        self._fake_items_db[item_id_str]["tags"].append(new_tag)

        outbox_entry = {
            "item_id": item_id_str,
            "action": "tag_added",
            "tag": new_tag,
            "status": "PENDING"
        }
        self._outbox.append(outbox_entry)
        self.logger.info(f"Added message to Outbox: {outbox_entry}")

        return new_tag

    async def run_outbox_processor(self):
        self.logger.info("Starting Outbox processor...")
        while True:
            try:
                if self.kafka_producer:
                    pending = [msg for msg in self._outbox if msg["status"] == "PENDING"]
                    for msg in pending:
                        kafka_message = {
                            "item_id": msg["item_id"],
                            "action": msg["action"],
                            "tag": msg["tag"]
                        }
                        try:
                            await self.kafka_producer.send_and_wait(
                                "collection-updates",
                                json.dumps(kafka_message).encode('utf-8')
                            )
                            self.logger.info(f"Outbox Relay sent: {kafka_message}")
                            self._outbox.remove(msg)
                        except Exception as e:
                            self.logger.error(f"Failed to send Outbox message: {e}")

                await asyncio.sleep(2)
            except asyncio.CancelledError:
                self.logger.info("Outbox processor cancelled.")
                break
            except Exception as e:
                self.logger.error(f"Error in Outbox processor: {e}")
                await asyncio.sleep(5)

    async def run_compensation_listener(self):
        self.logger.info("Starting Compensation listener...")
        if not self.kafka_consumer:
            self.logger.warning("Kafka consumer not initialized. Compensation listener exiting.")
            return

        try:
            async for msg in self.kafka_consumer:
                try:
                    data = json.loads(msg.value.decode('utf-8'))
                    self.logger.info(f"Received compensation request: {data}")

                    if data.get("action") == "TAG_ADD_FAILED":
                        await self._compensate_add_tag(data)

                except Exception as e:
                    self.logger.error(f"Error processing compensation message: {e}")
        except asyncio.CancelledError:
            self.logger.info("Compensation listener cancelled.")
        except Exception as e:
            self.logger.error(f"Critical error in Compensation listener: {e}")

    async def _compensate_add_tag(self, data: dict):
        item_id = data.get("item_id")
        tag_to_remove = data.get("tag")

        if not item_id or not tag_to_remove:
            return

        item = self._fake_items_db.get(item_id)
        if item and tag_to_remove in item["tags"]:
            item["tags"].remove(tag_to_remove)
            self.logger.warning(
                f"[SAGA] Compensating transaction executed: Removed tag '{tag_to_remove}' from item {item_id}")
        else:
            self.logger.info(f"[SAGA] Tag '{tag_to_remove}' not found on item {item_id}, skipping rollback.")

    async def _validate_tag_with_service(self, tag_name: str):
        tag_data = {"tag_name": tag_name}
        tags_url = self.tags_service_url

        async with httpx.AsyncClient() as client:
            try:
                post_url = tags_url if tags_url.endswith('/') else f"{tags_url}/"
                response = await client.post(post_url, json=tag_data, timeout=5.0)
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                try:
                    error_detail = e.response.json().get('detail', 'Bad Request')
                except Exception:
                    error_detail = e.response.text or "Unknown error"
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"Tag validation failed: {error_detail}"
                )
            except httpx.RequestError:
                raise HTTPException(
                    status_code=503,
                    detail="The Tags Service is currently unavailable."
                )
