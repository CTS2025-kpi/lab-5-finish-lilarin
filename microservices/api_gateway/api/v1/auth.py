import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from microservices.api_gateway.config import config

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login", summary="Get Access Token via Email/Password")
async def login(payload: LoginRequest):
    auth_url = f"{config.supabase_url}/auth/v1/token?grant_type=password"

    headers = {
        "apikey": config.supabase_key,
        "Content-Type": "application/json"
    }

    body = {
        "email": payload.email,
        "password": payload.password
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(auth_url, json=body, headers=headers)

            if response.status_code != 200:
                error_data = response.json()
                raise HTTPException(
                    status_code=response.status_code,
                    detail=error_data.get("error_description", "Login failed")
                )

            data = response.json()
            return {
                "access_token": data["access_token"],
                "token_type": "bearer",
                "user": {
                    "email": data["user"]["email"],
                    "id": data["user"]["id"]
                }
            }

        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Failed to connect to Auth provider: {e}")
