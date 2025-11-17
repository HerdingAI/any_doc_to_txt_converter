"""
Converter factory for creating appropriate converters based on file type.
"""
from pathlib import Path
from typing import Optional
from .base import BaseConverter
from .pdf_converter import PDFConverter
from .docx_converter import DOCXConverter
from .xlsx_converter import XLSXConverter
from .pptx_converter import PPTXConverter
from .html_converter import HTMLConverter
from .markdown_converter import MarkdownConverter
from .epub_converter import EPUBConverter
from .mobi_converter import MOBIConverter


class ConverterFactory:
    """Factory for creating document converters."""

    # Map file extensions to converter classes
    CONVERTER_MAP = {
        '.pdf': PDFConverter,
        '.docx': DOCXConverter,
        '.xlsx': XLSXConverter,
        '.pptx': PPTXConverter,
        '.html': HTMLConverter,
        '.htm': HTMLConverter,
        '.md': MarkdownConverter,
        '.markdown': MarkdownConverter,
        '.epub': EPUBConverter,
        '.mobi': MOBIConverter,
    }

    @classmethod
    def get_converter(cls, file_path: str, preserve_structure: bool = True) -> Optional[BaseConverter]:
        """
        Get appropriate converter for file type.

        Args:
            file_path: Path to file
            preserve_structure: Whether to preserve document structure

        Returns:
            Converter instance or None if format not supported
        """
        extension = Path(file_path).suffix.lower()

        converter_class = cls.CONVERTER_MAP.get(extension)
        if converter_class:
            return converter_class(preserve_structure=preserve_structure)

        return None

    @classmethod
    def is_supported(cls, file_path: str) -> bool:
        """
        Check if file format is supported.

        Args:
            file_path: Path to file

        Returns:
            True if supported, False otherwise
        """
        extension = Path(file_path).suffix.lower()
        return extension in cls.CONVERTER_MAP

    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        """
        Get list of all supported file extensions.

        Returns:
            List of supported extensions
        """
        return list(cls.CONVERTER_MAP.keys())
