from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from prometheus_fastapi_instrumentator import Instrumentator

from microservices.filter_service.api.v1.router import router as router_v1
from microservices.filter_service.dependencies import filter_service
from microservices.libs.utils.middleware import TraceIdMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    await filter_service.start_consumer()
    yield
    await filter_service.stop_consumer()


app = FastAPI(
    title="Filter Service",
    description="Consumes events and provides filtered views.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(TraceIdMiddleware)

Instrumentator().instrument(app).expose(app)

app.include_router(router_v1, prefix="/api")


@app.get("/", tags=["Health"])
async def health_check():
    return Response(status_code=200, content="OK")
