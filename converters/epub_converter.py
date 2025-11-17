"""
EPUB to text converter.
"""
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from .base import BaseConverter


class EPUBConverter(BaseConverter):
    """Converter for EPUB documents."""

    def convert(self, input_path: str, output_path: str) -> bool:
        """
        Convert EPUB to text.

        Args:
            input_path: Path to EPUB file
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
            self.logger.error(f"Error converting EPUB {input_path}: {str(e)}")
            return False

    def _extract_text(self, input_path: str) -> str:
        """
        Extract text from EPUB.

        Args:
            input_path: Path to EPUB file

        Returns:
            Extracted text
        """
        book = epub.read_epub(input_path)
        text_parts = []

        # Get all document items (chapters)
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                try:
                    # Get HTML content
                    content = item.get_content()
                    soup = BeautifulSoup(content, 'html.parser')

                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()

                    if self.preserve_structure:
                        # Add chapter separator
                        text_parts.append(f"\n{'='*60}\n")

                        # Try to get chapter title
                        title = soup.find(['h1', 'h2', 'h3'])
                        if title:
                            text_parts.append(f"{title.get_text().strip()}\n")
                            text_parts.append(f"{'='*60}\n\n")

                        # Extract structured text
                        for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']):
                            text = element.get_text().strip()
                            if text:
                                if element.name.startswith('h'):
                                    level = int(element.name[1])
                                    text_parts.append(f"\n{'#' * level} {text}\n\n")
                                else:
                                    text_parts.append(f"{text}\n\n")
                    else:
                        # Simple text extraction
                        text = soup.get_text(separator='\n', strip=True)
                        text_parts.append(text + "\n\n")

                except Exception as e:
                    self.logger.warning(f"Error processing EPUB item: {str(e)}")
                    continue

        return ''.join(text_parts).strip()

    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        """Get supported file extensions."""
        return ['.epub']
