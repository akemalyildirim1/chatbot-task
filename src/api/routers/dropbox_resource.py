"""Dropbox router module."""

from typing import Annotated

from api.deps import SessionDep, UserTeamsIdDependency
from fastapi import APIRouter, Depends, Path, Query
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel

from src.schemas.dropbox import DropboxFileMetadata
from src.service.dropbox_resource import DropboxResourceService

dropbox_resource_router = APIRouter(
    prefix="/dropbox/resource",
    tags=["dropbox-resource"],
)

dropbox_resource_service: DropboxResourceService = DropboxResourceService()


class ResourceQueryParams(BaseModel):
    """Query parameters for resource operations."""

    resource_id: str = Query(default="", description="Resource ID.")


class ResourcePathParams(BaseModel):
    """Path parameters for resource operations."""

    resource_id: str = Path(description="Resource ID.")


@dropbox_resource_router.get(
    "/",
    summary="List the resources of selected resource.",
)
async def list_resources(
    session: SessionDep,
    user_teams_id_dependency: Annotated[UserTeamsIdDependency, Depends()],
    resource_query_params: Annotated[ResourceQueryParams, Depends()],
):
    """List the resources of selected resource."""
    result = await dropbox_resource_service.get_resources_of_given_resource(
        user_teams_id=user_teams_id_dependency.teams_id,
        session=session,
        path=resource_query_params.resource_id,
    )
    return ORJSONResponse(content=result)


@dropbox_resource_router.get(
    "/{resource_id}/children/",
    summary="Get children resources list.",
    response_model=list[str],
)
async def get_children(
    session: SessionDep,
    user_teams_id_dependency: Annotated[UserTeamsIdDependency, Depends()],
    resource_path_params: Annotated[ResourcePathParams, Depends()],
):
    """Get children resources list."""
    result = await dropbox_resource_service.get_children_resources(
        user_teams_id=user_teams_id_dependency.teams_id,
        session=session,
        resource_id=resource_path_params.resource_id,
    )

    return ORJSONResponse(content=result)


@dropbox_resource_router.get(
    "/{resource_id}/",
    summary="Get the metadata of selected resource.",
    response_model=DropboxFileMetadata,
)
async def get_resource_info(
    session: SessionDep,
    user_teams_id_dependency: Annotated[UserTeamsIdDependency, Depends()],
    resource_path_params: Annotated[ResourcePathParams, Depends()],
):
    """Get the metadata of the selected resource."""
    result = await dropbox_resource_service.get_metadata_of_resource(
        user_teams_id=user_teams_id_dependency.teams_id,
        session=session,
        resource_id=resource_path_params.resource_id,
    )
    return ORJSONResponse(content=result)
