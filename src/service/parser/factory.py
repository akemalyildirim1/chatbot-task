"""Factory for creating parser objects."""

from functools import lru_cache
from typing import Type

from .parser import Parser
from .pdf_parser import PDFParser

file_extension_to_parser: dict[str, Type[Parser]] = {
    "pdf": PDFParser,
}


class ParserFactory:
    """Parser factory class.

    This class is responsible for creating parser objects.

    Methods:
        create_parser: Create a parser object.
    """

    @staticmethod
    @lru_cache(maxsize=1)
    def create_parser(file_extension: str) -> Parser:
        """Create a parser object.

        Arguments:
            file_extension: The extension of the file.

        Returns:
            A parser object.
        """
        try:
            return file_extension_to_parser[file_extension]()
        except KeyError as error:
            raise ValueError("Unsupported file extension") from error
