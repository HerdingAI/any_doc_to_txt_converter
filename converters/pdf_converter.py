"""
PDF to text converter.
"""
from PyPDF2 import PdfReader
from .base import BaseConverter


class PDFConverter(BaseConverter):
    """Converter for PDF documents."""

    def convert(self, input_path: str, output_path: str) -> bool:
        """
        Convert PDF to text.

        Args:
            input_path: Path to PDF file
            output_path: Path to output text file

        Returns:
            True if successful, False otherwise
        """
        try:
            text = self._extract_text(input_path)
            if text:
                return self._write_output(text, output_path)
            return False
        except Exception as e:
            self.logger.error(f"Error converting PDF {input_path}: {str(e)}")
            return False

    def _extract_text(self, input_path: str) -> str:
        """
        Extract text from PDF.

        Args:
            input_path: Path to PDF file

        Returns:
            Extracted text
        """
        text_parts = []

        reader = PdfReader(input_path)

        for page_num, page in enumerate(reader.pages, 1):
            try:
                page_text = page.extract_text()

                if page_text:
                    if self.preserve_structure:
                        # Add page separator
                        text_parts.append(f"\n{'='*60}\n")
                        text_parts.append(f"Page {page_num}\n")
                        text_parts.append(f"{'='*60}\n\n")

                    text_parts.append(page_text)
                    text_parts.append("\n\n")

            except Exception as e:
                self.logger.warning(f"Error extracting text from page {page_num}: {str(e)}")
                continue

        return ''.join(text_parts).strip()

    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        """Get supported file extensions."""
        return ['.pdf']
