"""HTTP middleware: наскрізний request_id у логах і заголовку відповіді."""
from fastapi import FastAPI, Request

from fridgy.core.request_context import (
    HEADER_NAME,
    request_id_var,
    resolve_request_id,
)


def register_request_id_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        request_id = resolve_request_id(request.headers.get(HEADER_NAME))
        token = request_id_var.set(request_id)
        try:
            response = await call_next(request)
        finally:
            request_id_var.reset(token)

        response.headers[HEADER_NAME] = request_id
        return response
