"""Query router module."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel, Field

from src.service.query import QueryService

from ..deps import SessionDep, UserTeamsIdDependency

query_router = APIRouter(
    prefix="/query",
    tags=["query"],
)

query_service: QueryService = QueryService()


class QueryRequest(BaseModel):
    """Query request class.

    Attributes:
        query: The query to search.
    """

    query: str = Field(
        Query(
            description="The query to search.",
        )
    )


@query_router.get(
    "/",
    summary="Query the resources of a user.",
)
async def query_resources(
    query: Annotated[QueryRequest, Depends()],
    session: SessionDep,
    user_teams_id_dependency: Annotated[UserTeamsIdDependency, Depends()],
):
    """Query the resources of a user."""
    result = await query_service.query(
        query=query.query,
        session=session,
        user_teams_id=user_teams_id_dependency.teams_id,
    )

    return ORJSONResponse(content=result)
