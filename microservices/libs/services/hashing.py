import asyncio
import logging
from typing import Optional

import uhashring


class ConsistentHashingRing:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.ring = uhashring.HashRing(nodes={})
        self._lock = asyncio.Lock()

    async def add_group(self, group_id: str):
        async with self._lock:
            if group_id not in self.ring.get_nodes():
                self.ring.add_node(group_id)
                self.logger.info(
                    f"Added shard group '{group_id}' to the ring. "
                    f"Current groups: {list(self.ring.get_nodes())}"
                )

    async def remove_group(self, group_id: str):
        async with self._lock:
            if group_id in self.ring.get_nodes():
                self.ring.remove_node(group_id)
                self.logger.info(f"Removed shard group '{group_id}' from the ring")

    def get_group_for_key(self, key: str) -> Optional[str]:
        if not self.ring.get_nodes():
            self.logger.error("Hashing ring has no active shard groups")
            return None
        return self.ring.get_node(key)
