from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from prometheus_fastapi_instrumentator import Instrumentator

from microservices.libs.utils.middleware import TraceIdMiddleware
from microservices.shard_service.api.v1.router import router as router_v1
from microservices.shard_service.dependencies import storage_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    await storage_service.start()
    await storage_service.register_self()
    yield
    await storage_service.stop()


app = FastAPI(
    title="Shard Service",
    description="A single node (replica) for storing a subset of data.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(TraceIdMiddleware)

Instrumentator().instrument(app).expose(app)

app.include_router(router_v1, prefix="/api")


@app.get("/", tags=["Health"])
async def health_check():
    return Response(status_code=200, content="OK")
