from fastapi import FastAPI, Response

from api.v1.router import router as router_v1
from microservices.libs.utils.middleware import TraceIdMiddleware

app = FastAPI(
    title="Tags Service",
    description="A microservice for managing tags",
    version="1.0.0"
)

app.add_middleware(TraceIdMiddleware)

app.include_router(router_v1, prefix="/api")


@app.get("/", tags=["Health"])
async def health_check():
    return Response(status_code=200)
