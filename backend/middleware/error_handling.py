from fastapi import Request, status
from fastapi.responses import JSONResponse
from schemas.chat import GlobalError, ErrorDetail

async def global_error_handler(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        # In a real app, you'd have more sophisticated logging and error handling
        error_detail = ErrorDetail(code="UNHANDLED_EXCEPTION", message=str(e))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=GlobalError(detail=error_detail).dict(),
        )
