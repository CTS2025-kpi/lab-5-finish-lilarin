import json
import logging
import random
from typing import Any, Dict, List
from urllib.parse import urljoin

import httpx
from fastapi import HTTPException, Request, Response
from prometheus_client import Gauge

from microservices.libs.schemas.router import RecordResponse, TableDefinition
from microservices.libs.services.hashing import ConsistentHashingRing
from microservices.libs.utils.logger import trace_id_var


class CoordinatorService:
    def __init__(self, hashing_ring: ConsistentHashingRing, logger: logging.Logger):
        self.hashing_ring = hashing_ring
        self.logger = logger
        self._table_definitions: Dict[str, TableDefinition] = {}
        self._shard_topology: Dict[str, Dict[str, Any]] = {}
        Gauge('router_active_shards_total', 'Number of active shard groups').set(len(self._shard_topology))

    def get_topology_status(self) -> Dict[str, Any]:
        return {
            "shards_count": len(self._shard_topology),
            "tables_count": len(self._table_definitions),
            "topology": self._shard_topology,
            "tables": [t.table_name for t in self._table_definitions.values()]
        }

    async def register_shard_node(self, group_id: str, shard_url: str, is_leader: bool):
        if group_id not in self._shard_topology:
            self._shard_topology[group_id] = {"leader": None, "followers": []}
            await self.hashing_ring.add_group(group_id)

        if is_leader:
            old_leader = self._shard_topology[group_id]["leader"]
            if old_leader and old_leader != shard_url:
                self.logger.warning(f"Replacing leader for {group_id}: {old_leader} -> {shard_url}")
            self._shard_topology[group_id]["leader"] = shard_url
            if shard_url in self._shard_topology[group_id]["followers"]:
                self._shard_topology[group_id]["followers"].remove(shard_url)
        else:
            if shard_url not in self._shard_topology[group_id]["followers"]:
                self._shard_topology[group_id]["followers"].append(shard_url)
            if self._shard_topology[group_id]["leader"] == shard_url:
                self._shard_topology[group_id]["leader"] = None

        self.logger.info(f"Registered node {shard_url} for group {group_id} (Leader: {is_leader})")

    def register_table(self, table: TableDefinition) -> None:
        if table.table_name in self._table_definitions:
            raise HTTPException(status_code=409, detail="Table already exists")
        self._table_definitions[table.table_name] = table
        self.logger.info(f"Registered table '{table.table_name}' with primary key '{table.primary_key}'")

    def get_all_tables(self) -> List[TableDefinition]:
        return list(self._table_definitions.values())

    def delete_table(self, table_name: str) -> None:
        if table_name not in self._table_definitions:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
        del self._table_definitions[table_name]
        self.logger.info(f"Deleted table definition for '{table_name}'")

    async def create_record_on_shard(self, table_name: str, value: Dict[str, Any]) -> RecordResponse:
        table_definition = self._get_table_definition(table_name)
        primary_key_field = table_definition.primary_key
        primary_key_value = value.get(primary_key_field)

        if not primary_key_value:
            raise HTTPException(status_code=400, detail=f"Primary key '{primary_key_field}' is missing")

        shard_url = self._get_target_node(table_name, primary_key_value, write_op=True)

        path = f"api/v1/records/{table_name}/{primary_key_value}"
        url_to_forward = urljoin(shard_url, path)
        self.logger.info(f"Forwarding WRITE (Create) to Leader: {url_to_forward}")

        headers = {"X-Trace-ID": trace_id_var.get()}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url=url_to_forward,
                    json={"value": value},
                    headers=headers,
                    timeout=10.0
                )
                response.raise_for_status()
                response_data = response.json()
                return RecordResponse(
                    table_name=table_name,
                    primary_key=str(primary_key_value),
                    value=response_data.get("value")
                )
            except httpx.HTTPStatusError as e:
                self._handle_shard_error(e, shard_url)
            except httpx.RequestError as e:
                self._handle_connection_error(e, shard_url)

    async def forward_request_to_shard(self, table_name: str, primary_key_value: str, request: Request):
        is_write = request.method in ["DELETE", "POST", "PUT", "PATCH"]

        shard_url = self._get_target_node(table_name, primary_key_value, write_op=is_write)

        path = f"api/v1/records/{table_name}/{primary_key_value}"
        url_to_forward = urljoin(shard_url, path)
        self.logger.info(f"Forwarding {request.method} to {'Leader' if is_write else 'Replica'}: {url_to_forward}")

        headers = dict(request.headers)
        headers.pop("host", None)
        headers["X-Trace-ID"] = trace_id_var.get()

        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method=request.method, url=url_to_forward, headers=headers,
                    params=request.query_params, content=await request.body() or None, timeout=10.0
                )
                response.raise_for_status()

                if request.method in ["HEAD", "DELETE"]:
                    return Response(status_code=response.status_code)

                response_data = response.json()
                return RecordResponse(
                    table_name=table_name,
                    primary_key=primary_key_value,
                    value=response_data.get("value")
                )
            except httpx.HTTPStatusError as e:
                self._handle_shard_error(e, shard_url)
            except httpx.RequestError as e:
                self._handle_connection_error(e, shard_url)

    def _get_target_node(self, table_name: str, primary_key_value: Any, write_op: bool) -> str:
        group_id = self.hashing_ring.get_group_for_key(f"{table_name}::{primary_key_value}")
        if not group_id:
            raise HTTPException(status_code=503, detail="No available shard groups")

        group_info = self._shard_topology.get(group_id)
        if not group_info:
            raise HTTPException(status_code=503, detail=f"Topology info missing for group {group_id}")

        if write_op:
            leader = group_info.get("leader")
            if not leader:
                raise HTTPException(status_code=503, detail=f"No leader available for group {group_id}")
            return leader
        else:
            candidates = []
            if group_info.get("leader"):
                candidates.append(group_info["leader"])
            candidates.extend(group_info.get("followers", []))

            if not candidates:
                raise HTTPException(status_code=503, detail=f"No active nodes for group {group_id}")

            return random.choice(candidates)

    def _get_table_definition(self, table_name: str) -> TableDefinition:
        table_definition = self._table_definitions.get(table_name)
        if not table_definition:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' is not registered")
        return table_definition

    def _handle_shard_error(self, exc: httpx.HTTPStatusError, shard_url: str):
        try:
            error_detail = exc.response.json().get("detail", exc.response.text)
        except json.JSONDecodeError:
            error_detail = exc.response.text or f"Shard returned status {exc.response.status_code}"
        self.logger.error(f"Error from shard '{shard_url}': {exc.response.status_code} - {error_detail}")
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)

    def _handle_connection_error(self, exc: httpx.RequestError, shard_url: str):
        self.logger.error(f"Cannot connect to shard '{shard_url}': {exc}")
        raise HTTPException(status_code=503, detail=f"Shard '{shard_url}' is unavailable.")
