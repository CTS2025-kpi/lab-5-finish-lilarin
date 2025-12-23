from fastapi import APIRouter, Request, Body, Depends

from microservices.api_gateway.api.utils import forward_request
from microservices.api_gateway.auth import verify_admin
from microservices.api_gateway.config import config
from microservices.libs.schemas.router import TableDefinition, CreateRecordRequest

router = APIRouter()


@router.post("/tables", summary="Register a table definition")
async def proxy_register_table(request: Request, body: TableDefinition = Body(...)):
    return await forward_request(config.router_service_url, "tables", request)


@router.get("/tables", summary="List all table definitions")
async def proxy_list_tables(request: Request):
    return await forward_request(config.router_service_url, "tables", request)


@router.delete(
    "/tables/{table_name}",
    dependencies=[Depends(verify_admin)],
    summary="Delete a table definition"
)
async def proxy_delete_table(table_name: str, request: Request):
    path = f"tables/{table_name}"
    return await forward_request(config.router_service_url, path, request)


@router.post("/records", summary="Create a record")
async def proxy_create_record(request: Request, body: CreateRecordRequest = Body(...)):
    return await forward_request(config.router_service_url, "records", request)


@router.get("/records/{table_name}/{primary_key}", summary="Read a record")
async def proxy_read_record(table_name: str, primary_key: str, request: Request):
    path = f"records/{table_name}/{primary_key}"
    return await forward_request(config.router_service_url, path, request)


@router.delete("/records/{table_name}/{primary_key}", summary="Delete a record")
async def proxy_delete_record(table_name: str, primary_key: str, request: Request):
    path = f"records/{table_name}/{primary_key}"
    return await forward_request(config.router_service_url, path, request)


@router.head("/records/{table_name}/{primary_key}", summary="Check if a record exists")
async def proxy_exists_record(table_name: str, primary_key: str, request: Request):
    path = f"records/{table_name}/{primary_key}"
    return await forward_request(config.router_service_url, path, request)
