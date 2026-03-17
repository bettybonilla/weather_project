from fastapi import Request, Response
from fastapi.responses import JSONResponse


async def check_handler(request: Request) -> Response:
    content_type = request.headers.get("Content-Type")
    if content_type and "application/json" in content_type:
        return JSONResponse({"status": "ok"})

    return Response()
