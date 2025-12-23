from authlib.jose import jwt
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from microservices.api_gateway.config import config

security = HTTPBearer(scheme_name="Supabase JWT")


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            config.jwt_secret
        )
        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


def verify_admin(payload: dict = Depends(verify_token)) -> dict:
    email = payload.get("email", "")
    if "admin" in email:
        return payload
    raise HTTPException(status_code=403, detail="Admin scope required")
