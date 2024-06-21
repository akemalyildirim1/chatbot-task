"""Shared functions for services."""

from typing import Any

from aiohttp import ClientSession
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import NotFoundError
from src.models import User


class HttpResponse(BaseModel):
    """Model for HTTP response.

    Attributes:
        data: The response data.
        status: The response status.
        ok: The response status.
    """

    data: dict[str, Any]
    status: int
    ok: bool


async def send_http_request(
    url: str,
    method: str = "get",
    headers: dict[str, str] | None = None,
    body: Any | None = None,
) -> HttpResponse:  # pragma: no cover
    """Send request to the specified url.

    Arguments:
        url: URL to send request.
        method: Method of the request.
        headers: Headers of the request.
        body: Body of the request.

    Returns:
        The dictionary that includes the response and the status.
    """
    raw_request_func_params: dict[str, str] = {
        "method": method,
        "url": url,
    }

    request_func_params: dict[str, str] = (
        {**raw_request_func_params, "data": body} if body else raw_request_func_params
    )

    async with ClientSession(
        headers=headers if headers else None
    ) as session, session.request(**request_func_params) as response:
        response_json: dict[str, Any] = await response.json()
        return HttpResponse(
            data=response_json,
            status=response.status,
            ok=response.ok,
        )


async def get_user_id_from_teams_id(teams_id: str, session: AsyncSession) -> int:
    """Get the user id from the microsoft teams id.

    Arguments:
        teams_id: The teams id of the user.
        session: The database session.

    Returns:
        The user id.

    Raises:
        NotFoundError: If the user is not found.
    """
    user = (await session.execute(select(User).filter_by(teams_id=teams_id))).fetchone()
    if not user:
        raise NotFoundError("User")

    return user[0].id
