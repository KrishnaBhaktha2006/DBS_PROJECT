"""
app/utils/responses.py
──────────────────────
Consistent JSON response envelopes used throughout the API.
"""

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def success(data=None, message: str = "OK", status_code: int = 200) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder({"success": True, "message": message, "data": data}),
    )


def error(message: str, status_code: int = 400, detail=None) -> JSONResponse:
    body = {"success": False, "message": message}
    if detail:
        body["detail"] = detail
    return JSONResponse(status_code=status_code, content=jsonable_encoder(body))
