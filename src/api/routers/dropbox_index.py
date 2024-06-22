"""Dropbox index router module."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.service.dropbox.resource_index import ResourceIndexService

from ..deps import ResourcePathParams, SessionDep, UserTeamsIdDependency

dropbox_index_router = APIRouter(
    prefix="/dropbox/index",
    tags=["dropbox-index"],
)

resource_index_service: ResourceIndexService = ResourceIndexService()


@dropbox_index_router.post("/{resource_id}/", status_code=status.HTTP_201_CREATED)
async def index_resources(
    session: SessionDep,
    user_teams_id_dependency: Annotated[UserTeamsIdDependency, Depends()],
    resource_path_params: Annotated[ResourcePathParams, Depends()],
) -> None:
    """Index resources for a user."""
    await resource_index_service.index_resource(
        user_teams_id=user_teams_id_dependency.teams_id,
        session=session,
        resource_id=resource_path_params.resource_id,
    )
