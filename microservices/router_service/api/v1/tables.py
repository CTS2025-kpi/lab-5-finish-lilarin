from typing import List

from fastapi import APIRouter, Depends

from microservices.libs.schemas.router import TableDefinition
from microservices.libs.services.coordinator import CoordinatorService
from microservices.router_service.dependencies import get_coordinator_service

router = APIRouter()


@router.post("", status_code=201, summary="Register a table definition")
def register_table(
        table: TableDefinition,
        service: CoordinatorService = Depends(get_coordinator_service)
):
    return service.register_table(table)


@router.get("", response_model=List[TableDefinition], summary="List all table definitions")
def list_tables(service: CoordinatorService = Depends(get_coordinator_service)):
    return service.get_all_tables()


@router.delete("/{table_name}", summary="Delete a table definition")
def delete_table(
        table_name: str,
        service: CoordinatorService = Depends(get_coordinator_service)
):
    return service.delete_table(table_name)
