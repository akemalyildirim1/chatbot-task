"""Shared exceptions."""


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
