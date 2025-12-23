import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from prometheus_fastapi_instrumentator import Instrumentator

from microservices.collections_service.api.v1.router import router as router_v1
from microservices.collections_service.dependencies import collections_service
from microservices.libs.utils.middleware import TraceIdMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    await collections_service.initialize_kafka_producer()
    await collections_service.initialize_kafka_consumer()

    outbox_task = asyncio.create_task(collections_service.run_outbox_processor())
    compensation_task = asyncio.create_task(collections_service.run_compensation_listener())

    yield
    outbox_task.cancel()
    compensation_task.cancel()
    await asyncio.gather(outbox_task, compensation_task, return_exceptions=True)
    await collections_service.stop_kafka_components()


app = FastAPI(
    title="Collections Service",
    description="Microservice for managing user collections and items.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(TraceIdMiddleware)

Instrumentator().instrument(app).expose(app)

app.include_router(router_v1, prefix="/api")


@app.get("/", tags=["Health"])
async def health_check():
    return Response(status_code=200, content="OK")
