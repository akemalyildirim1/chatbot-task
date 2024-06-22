"""Query pydantic schema."""

from pydantic import BaseModel


class Query(BaseModel):
    """Query schema.

    Attributes:
        content: The content of the query.
        name: The name of the resource.
        path: The path of the resource.
    """

    content: list[str]
    name: str
    path: str
