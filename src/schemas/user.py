"""User schemas."""

from pydantic import AwareDatetime, BaseModel, ConfigDict


class UserBaseSchema(BaseModel):
    """User base schema.

    Attributes:
        teams_id: The ID of the user's microsoft
            team account.
        name: The name of the user.
    """

    teams_id: str
    name: str


class UserCreateSchema(UserBaseSchema):
    """User create schema."""


class UserSchema(UserBaseSchema):
    """User schema.

    Attributes:
        id: The ID of the user.
        created_at: The date and time the user was created.
        updated_at: The date and time the user was last updated.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: AwareDatetime
    updated_at: AwareDatetime
