"""Document parsing utilities for various file formats."""
import logging
from pathlib import Path
from typing import Optional
import fitz  # PyMuPDF
from docx import Document

logger = logging.getLogger(__name__)


class DocumentParser:
    """Parse various document formats to extract text."""

    @staticmethod
    def parse_txt(file_path: str) -> str:
        """Parse plain text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info(f"Parsed TXT file: {file_path}")
            return content.strip()
        except Exception as e:
            logger.error(f"Error parsing TXT file {file_path}: {e}")
            return ""

    @staticmethod
    def parse_pdf(file_path: str) -> str:
        """Parse PDF file using PyMuPDF."""
        doc = None
        try:
            doc = fitz.open(file_path)
            text_parts = []
            num_pages = len(doc)

            for page_num in range(num_pages):
                page = doc[page_num]
                # Try standard text extraction first
                text = page.get_text()
                if text and text.strip():
                    text_parts.append(text)
                else:
                    # Try extracting text with different parameters for scanned PDFs
                    text = page.get_text("text", sort=True)
                    if text and text.strip():
                        text_parts.append(text)

            content = "\n\n".join(text_parts)
            logger.info(f"Parsed PDF file: {file_path} ({num_pages} pages, {len(content)} chars)")

            if not content.strip():
                logger.warning(f"PDF file {file_path} appears to have no extractable text (may be scanned/image-based)")

            return content.strip()
        except Exception as e:
            logger.error(f"Error parsing PDF file {file_path}: {e}", exc_info=True)
            return ""
        finally:
            if doc:
                doc.close()

    @staticmethod
    def parse_docx(file_path: str) -> str:
        """Parse DOCX file using python-docx."""
        try:
            doc = Document(file_path)
            text_parts = []

            for paragraph in doc.paragraphs:
                if paragraph.text:
                    text_parts.append(paragraph.text)

            content = "\n".join(text_parts)
            logger.info(f"Parsed DOCX file: {file_path}")
            return content.strip()
        except Exception as e:
            logger.error(f"Error parsing DOCX file {file_path}: {e}")
            return ""

    @classmethod
    def parse_file(cls, file_path: str) -> Optional[str]:
        """Parse file based on extension."""
        path = Path(file_path)

        if not path.exists():
            logger.error(f"File not found: {file_path}")
            return None

        extension = path.suffix.lower()

        if extension == '.txt':
            return cls.parse_txt(file_path)
        elif extension == '.pdf':
            return cls.parse_pdf(file_path)
        elif extension == '.docx':
            return cls.parse_docx(file_path)
        else:
            logger.warning(f"Unsupported file format: {extension}")
            return None


# Global document parser instance
document_parser = DocumentParser()
