"""Error handler middleware."""

from typing import Type

from fastapi import status
from fastapi.responses import ORJSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.core import ConflictError, NotFoundError

custom_errors: dict[Type[Exception], int] = {
    ConflictError: status.HTTP_409_CONFLICT,
    NotFoundError: status.HTTP_404_NOT_FOUND,
}


class GenericErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Generic error handler middleware."""

    async def dispatch(self, request, call_next):
        """Dispatch the request."""
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            return ORJSONResponse(
                status_code=custom_errors.get(
                    type(e), status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                content={"detail": str(e)},
            )
