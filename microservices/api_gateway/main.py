from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from api.v1.router import router as router_v1
from microservices.libs.utils.middleware import TraceIdMiddleware

app = FastAPI(
    title="API Gateway",
    description="The single entry point for all microservices.",
    version="1.0.0"
)

app.add_middleware(TraceIdMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://cad.kpi.ua", "http://localhost:30007"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app)

app.include_router(router_v1, prefix="/api")


@app.get("/", tags=["Health"])
async def index():
    return Response(status_code=200)
