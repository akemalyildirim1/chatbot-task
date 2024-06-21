"""Shared functions for services."""

from typing import Any

from aiohttp import ClientSession
from pydantic import BaseModel, InstanceOf
from schemas.dropbox import DropboxAuthToken
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as psql_insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import NotFoundError
from src.models import DropboxToken, User


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
        if not response.ok:
            return HttpResponse(
                data={},
                status=response.status,
                ok=False,
            )
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


async def add_tokens_to_db(
    user_id: int,
    tokens: DropboxAuthToken,
    session: InstanceOf[AsyncSession],
) -> None:
    """Insert or override the access and refresh tokens to the database.

    Arguments:
        user_id: The user id.
        tokens: The access and refresh tokens.
        session: The database session.

    Returns:
        None.

    Raises:
        NotFoundError: If the user is not found.
    """
    try:
        await session.execute(
            psql_insert(DropboxToken)
            .values(
                user_id=user_id,
                access_token=tokens.access_token,
                refresh_token=tokens.refresh_token,
                expires_at=tokens.expires_at,
            )
            .on_conflict_do_update(
                index_elements=["user_id"],
                set_=dict(
                    access_token=tokens.access_token,
                    refresh_token=tokens.refresh_token,
                    expires_at=tokens.expires_at,
                ),
            )
        )
    except IntegrityError as error:
        raise NotFoundError("User") from error
