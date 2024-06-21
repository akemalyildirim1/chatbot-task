"""User router module."""

from fastapi import APIRouter, status

from src.schemas.user import UserCreateSchema
from src.service.user import UserService

from ..deps import SessionDep

user_router = APIRouter(
    prefix="/user",
    tags=["user"],
)

user_service: UserService = UserService()


@user_router.post(
    "/",
    summary="Create a new user.",
    status_code=status.HTTP_201_CREATED,
)
async def add_user(
    user: UserCreateSchema,
    session: SessionDep,
):
    """Create a new user."""
    await user_service.create_user(
        user=user,
        session=session,
    )
