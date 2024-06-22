"""Parser base class service."""

from abc import ABC, abstractmethod


class Parser(ABC):
    """Parser base class.

    This class is responsible for parsing the file content.

    Methods:
        parse: Parse the file content.
    """

    @abstractmethod
    def parse(self, content: bytes) -> str:
        """Parse the file content.

        Arguments:
            content: The content of the file to parse.

        Returns:
            The parsed content.
        """
