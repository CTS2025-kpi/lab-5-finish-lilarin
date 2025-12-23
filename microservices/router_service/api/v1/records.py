from fastapi import APIRouter, Request, Depends

from microservices.libs.schemas.router import RecordResponse, CreateRecordRequest
from microservices.libs.services.coordinator import CoordinatorService
from microservices.router_service.dependencies import get_coordinator_service

router = APIRouter()


@router.post("", response_model=RecordResponse, status_code=201, summary="Create a record")
async def create_record(
        record: CreateRecordRequest,
        service: CoordinatorService = Depends(get_coordinator_service)
):
    return await service.create_record_on_shard(record.table_name, record.value)


@router.get("/{table_name}/{primary_key}", response_model=RecordResponse, summary="Read a record")
async def read_record(
        table_name: str,
        primary_key: str,
        request: Request,
        service: CoordinatorService = Depends(get_coordinator_service)
):
    return await service.forward_request_to_shard(table_name, primary_key, request)


@router.delete("/{table_name}/{primary_key}", summary="Delete a record")
async def delete_record(
        table_name: str,
        primary_key: str,
        request: Request,
        service: CoordinatorService = Depends(get_coordinator_service)
):
    return await service.forward_request_to_shard(table_name, primary_key, request)


@router.head("/{table_name}/{primary_key}", summary="Check if a record exists")
async def exists_record(
        table_name: str,
        primary_key: str,
        request: Request,
        service: CoordinatorService = Depends(get_coordinator_service)
):
    return await service.forward_request_to_shard(table_name, primary_key, request)