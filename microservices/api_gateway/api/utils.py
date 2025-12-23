import json
from typing import Optional, Union
from urllib.parse import urljoin

import httpx
from fastapi import Request
from fastapi.responses import JSONResponse, Response

from microservices.api_gateway.config import logger
from microservices.libs.schemas.common import ResponseWrapper
from microservices.libs.utils.logger import trace_id_var


async def forward_request(
        base_url: str, path: Optional[str], request: Request
) -> Union[JSONResponse, Response]:
    if not base_url.endswith('/'):
        base_url += '/'

    url_to_forward = urljoin(base_url, path) if path is not None else base_url

    headers = dict(request.headers)
    headers.pop("host", None)
    headers["X-Trace-ID"] = trace_id_var.get()

    body = await request.body()
    params = request.query_params

    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=url_to_forward,
                headers=headers,
                params=params,
                content=body,
                timeout=120.0,
            )
            response.raise_for_status()

            if request.method == "HEAD":
                return Response(status_code=response.status_code)

            final_status_code = response.status_code

            try:
                response_data = response.json()
                wrapped_response = ResponseWrapper(data=response_data, success=True)
            except json.decoder.JSONDecodeError:
                wrapped_response = ResponseWrapper(success=True)
                final_status_code = 200

            return JSONResponse(
                content=wrapped_response.model_dump(),
                status_code=final_status_code
            )
        except httpx.HTTPStatusError as e:
            try:
                error_details = e.response.json()
                error_message = error_details.get("detail", e.response.text)
            except json.JSONDecodeError:
                error_message = e.response.text

            wrapped_response = ResponseWrapper(success=False, error=error_message)
            return JSONResponse(
                content=wrapped_response.model_dump(),
                status_code=e.response.status_code,
            )
        except httpx.RequestError as e:
            logger.error(f"Request failed for {url_to_forward}: {e}", exc_info=True)
            wrapped_response = ResponseWrapper(
                success=False, error=f"Service unavailable: {base_url}"
            )
            return JSONResponse(
                content=wrapped_response.model_dump(),
                status_code=503
            )
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for {url_to_forward}: {e}", exc_info=True)
            wrapped_response = ResponseWrapper(
                success=False, error="Invalid response format from upstream service"
            )
            return JSONResponse(
                content=wrapped_response.model_dump(), status_code=502
            )
