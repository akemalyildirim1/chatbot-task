"""Shared exceptions."""


class InvalidInputError(ValueError):
    """Raised when an input is invalid."""

    def __init__(self, input_name: str):
        """Initialize the exception."""
        super().__init__(f"Invalid {input_name}!")


class NotFoundError(ValueError):
    """Raised when an item is not found in a collection."""

    def __init__(self, item_name: str):
        """Initialize the exception."""
        super().__init__(f"{item_name.title()} not found!")


class ConflictError(ValueError):
    """Raised when an item already exists in a collection."""

    def __init__(self, item_name: str):
        """Initialize the exception."""
        super().__init__(f"{item_name.title()} already exists!")


class UnprocessableEntityError(ValueError):
    """Raised when an item is unprocessable."""

    def __init__(self, item_name: str):
        """Initialize the exception."""
        super().__init__(f"{item_name.title()} is unprocessable!")
