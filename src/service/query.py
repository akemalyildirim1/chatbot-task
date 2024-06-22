"""Query service module."""

from pydantic import InstanceOf, validate_call
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.query import Query

from .service import Service
from .utils import get_user_id_from_teams_id


class QueryService(Service):
    """Query operations."""

    @validate_call
    async def query(
        self, user_teams_id: str, query: str, session: InstanceOf[AsyncSession]
    ) -> str:
        """Query the resources of a user.

        Arguments:
            user_teams_id: The teams id of the user.
            query: The query to search.
            session: Database session.
        """
        user_id: int = await get_user_id_from_teams_id(
            teams_id=user_teams_id, session=session
        )

        query_result: dict[str, Query] = self.vector_db.query(
            collection_name=f"user_{user_id}", query=query
        )

        if not query_result:
            return "No results found."

        result: str = "Here are the results of your query:\n"
        for value in query_result.values():
            result = f"FROM: {value.path}\n"
            for v in value.content:
                result += f"{v}\n"

        return result
