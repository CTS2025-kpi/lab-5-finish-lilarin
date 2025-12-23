from microservices.libs.services.coordinator import CoordinatorService
from microservices.libs.services.hashing import ConsistentHashingRing
from microservices.router_service.config import logger

hashing_ring = ConsistentHashingRing(logger=logger)
coordinator_service = CoordinatorService(hashing_ring=hashing_ring, logger=logger)


def get_coordinator_service() -> CoordinatorService:
    return coordinator_service


def get_hashing_ring() -> ConsistentHashingRing:
    return hashing_ring
