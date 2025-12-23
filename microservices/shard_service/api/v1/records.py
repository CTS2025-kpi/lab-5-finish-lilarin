from fastapi import APIRouter, Path, Response, status, Depends

from microservices.libs.schemas.shard import RecordData, RecordResponse
from microservices.libs.services.storage import StorageService
from microservices.shard_service.dependencies import get_storage_service

router = APIRouter()


@router.post("/{table_name}/{primary_key}", response_model=RecordResponse, status_code=status.HTTP_201_CREATED)
async def create_record(
        table_name: str,
        primary_key: str,
        data: RecordData,
        service: StorageService = Depends(get_storage_service)
):
    stored_value = await service.create_record(table_name, primary_key, data.value)
    return RecordResponse(table_name=table_name, primary_key=primary_key, value=stored_value)


@router.get("/{table_name}/{primary_key}", response_model=RecordResponse)
async def read_record(
        table_name: str = Path(...),
        primary_key: str = Path(...),
        service: StorageService = Depends(get_storage_service)
):
    value = service.read_record(table_name, primary_key)
    return RecordResponse(table_name=table_name, primary_key=primary_key, value=value)


@router.delete("/{table_name}/{primary_key}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_record(
        table_name: str = Path(...),
        primary_key: str = Path(...),
        service: StorageService = Depends(get_storage_service)
):
    await service.delete_record(table_name, primary_key)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.head("/{table_name}/{primary_key}")
async def exists_record(
        table_name: str = Path(...),
        primary_key: str = Path(...),
        service: StorageService = Depends(get_storage_service)
):
    if service.exists_record(table_name, primary_key):
        return Response(status_code=status.HTTP_200_OK)
    return Response(status_code=status.HTTP_404_NOT_FOUND)
