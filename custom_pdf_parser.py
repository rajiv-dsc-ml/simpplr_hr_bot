import os
from typing import AsyncIterator, Iterator
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import pytesseract
import re

class CustomDocumentLoader(BaseLoader):
    """A document loader that reads PDF files using pytesseract."""

    def __init__(self, file_path: str) -> None:
        """Initialize the loader with a file path.

        Args:
            file_path: The path to the PDF file to load.
        """
        self.file_path = file_path

    def lazy_load(self) -> Iterator[Document]:
        """A lazy loader that reads a PDF file page by page using pytesseract."""
        # Convert PDF to images
        pages = convert_from_path(self.file_path)

        for page_number, page in enumerate(pages):
            # Extract text from each image
            page_content = pytesseract.image_to_string(page)
            yield Document(
                page_content=page_content,
                metadata={"page_number": page_number, "source": self.file_path},
            )

    def lazy_load_remove_pattern(self, heading3_pattern = r'\n\n\d{1,2}\.\d{1,2}' , heading2_pattern = r'\n\n\d{1,2}\.') -> Iterator[Document]:
        """An async lazy loader that reads a PDF file page by page using pytesseract."""
        # Convert PDF to images
        pages = convert_from_path(self.file_path)

        for page_number, page in enumerate(pages):
            # Extract text from each image
            page_content = pytesseract.image_to_string(page)
            # there is only one title for each pdf file that is found at the start of the first page.
            if page_number == 0 :
              page_content = '# ' + page_content
            # \n\n\d\.\d[\w\s-]+:\n
            if re.search(r'Introduction' , page_content):
              page_content = re.sub(r'\n.*Introduction', '\n## Introduction', page_content)

            if re.search(r'Conclusion' , page_content):
              page_content = re.sub(r'\n.*Conclusion', '\n## Conclusion', page_content)

            if heading3_pattern == r'\n\n\d\.\d([\w\s-]+):\n' :
              page_content = re.sub(heading3_pattern , r'\n\n###\1\n',page_content )
              page_content = re.sub(heading2_pattern , r'\n\n##\1\n' ,page_content)
            else :
              page_content = re.sub(heading3_pattern , '\n\n###',page_content )
              page_content = re.sub(heading2_pattern , '\n\n##' ,page_content)

            yield Document(
                page_content=page_content,
                metadata={"page_number": page_number, "source": self.file_path},
            )
