"""Query router module."""

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from src.service.query import QueryService

from ..deps import SessionDep, UserTeamsIdDependency

query_router = APIRouter(
    prefix="/query",
    tags=["query"],
)

query_service: QueryService = QueryService()


@query_router.post(
    "/",
    summary="Query the resources of a user.",
    # status_code=status.HTTP_200_OK,
)
async def query_resources(
    query: str,
    session: SessionDep,
    user_teams_id_dependency: Annotated[UserTeamsIdDependency, Depends()],
):
    """Query the resources of a user."""
    result = await query_service.query(
        query=query,
        session=session,
        user_teams_id=user_teams_id_dependency.teams_id,
    )

    return ORJSONResponse(content=result)
