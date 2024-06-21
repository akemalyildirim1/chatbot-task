"""Dropbox router module."""

from typing import Annotated

from api.deps import SessionDep
from fastapi import APIRouter, Depends, Query, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse, RedirectResponse
from pydantic import BaseModel, Field

from src.core import UnprocessableEntityError
from src.schemas.dropbox import DropboxAuthToken
from src.service.dropbox_login import DropboxLoginService

dropbox_router = APIRouter(
    prefix="/dropbox/login",
    tags=["dropbox-login"],
)

dropbox_login_service: DropboxLoginService = DropboxLoginService()


class UserTeamsIdDependency(BaseModel):
    """User teams id dependency."""

    teams_id: str = Field(
        Query(
            description="User's microsoft team id.",
        )
    )


@dropbox_router.get(
    "/",
    summary="Login to dropbox.",
    response_class=RedirectResponse,
)
async def login(user_teams_id_dependency: Annotated[UserTeamsIdDependency, Depends()]):
    """Redirect users to the Dropbox login page."""
    result = dropbox_login_service.generate_authorization_url(
        user_teams_id=user_teams_id_dependency.teams_id
    )
    return RedirectResponse(result)


@dropbox_router.get(
    "/callback/",
    summary="Dropbox login callback.",
    response_model=DropboxAuthToken,
)
async def callback(request: Request, session: SessionDep):
    """Callback for the Dropbox login."""
    code: str = request.query_params.get("code")
    user_teams_id: str = request.query_params.get("state")
    if not code or not user_teams_id:
        raise UnprocessableEntityError("Code" if not code else "User teams id")

    result = await dropbox_login_service.generate_tokens_from_code(
        code=code, user_teams_id=user_teams_id, session=session
    )

    return ORJSONResponse(content=jsonable_encoder(result))
