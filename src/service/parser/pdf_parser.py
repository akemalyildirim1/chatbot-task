"""PDF parser module."""

from io import BytesIO

from PyPDF2 import PdfReader

from .parser import Parser


class PDFParser(Parser):
    """PDF parser class.

    This class is responsible for parsing the PDF file content.

    Methods:
        parse: Parse the PDF file content.
    """

    def parse(self, content: bytes) -> str:
        """Parse the PDF file content.

        Arguments:
            content: The content of the PDF file.

        Returns:
            The parsed content.
        """
        bytes_data = BytesIO(content)
        text = ""
        reader = PdfReader(bytes_data)
        for num in range(len(reader.pages)):
            page = reader.pages[num]
            page_text = page.extract_text()
            text += page_text
        return text
