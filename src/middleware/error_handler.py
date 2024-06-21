"""Error handler middleware."""

from typing import Type

from fastapi import status
from fastapi.responses import ORJSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.core import (
    ConflictError,
    InvalidInputError,
    NotFoundError,
    UnprocessableEntityError,
)

custom_errors: dict[Type[Exception], int] = {
    ConflictError: status.HTTP_409_CONFLICT,
    InvalidInputError: status.HTTP_400_BAD_REQUEST,
    NotFoundError: status.HTTP_404_NOT_FOUND,
    UnprocessableEntityError: status.HTTP_422_UNPROCESSABLE_ENTITY,
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
