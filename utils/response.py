from typing import Any

from fastapi.responses import JSONResponse


def api_response(
    *,
    message: str,
    data: Any = None,
    status_code: int = 200,
) -> JSONResponse:
    """Uniform JSON body: ``status`` (HTTP code), ``message``, ``data``."""
    return JSONResponse(
        status_code=status_code,
        content={
            "status": status_code,
            "message": message,
            "data": data,
        },
    )
