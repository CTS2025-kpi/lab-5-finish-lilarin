from fastapi import FastAPI, Response
from prometheus_fastapi_instrumentator import Instrumentator

from api.v1.router import router as router_v1
from microservices.libs.utils.middleware import TraceIdMiddleware

app = FastAPI(
    title="Router Service (Coordinator)",
    description="Manages data sharding across multiple nodes."
)

app.add_middleware(TraceIdMiddleware)

Instrumentator().instrument(app).expose(app)

app.include_router(router_v1, prefix="/api")


@app.get("/", tags=["Health"])
async def health_check():
    return Response(status_code=200, content="OK")
