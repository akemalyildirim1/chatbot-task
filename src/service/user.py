"""User service module."""

from pydantic import InstanceOf, validate_call
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import ConflictError
from src.models.user import User
from src.schemas.user import UserCreateSchema

from .service import Service


class UserService(Service):
    """User operations.

    Methods:
        create_user: Create a new user.
    """

    @validate_call
    async def create_user(
        self, user: UserCreateSchema, session: InstanceOf[AsyncSession]
    ) -> None:
        """Create a new user.

        Arguments:
            user: User data to create.
            session: Database session.

        Returns:
            None.

        Raises:
            ConflictError: If the user already exists.
        """
        new_user: User = User(**user.model_dump())
        session.add(new_user)
        try:
            await session.flush()
        except IntegrityError as e:
            raise ConflictError("User") from e
