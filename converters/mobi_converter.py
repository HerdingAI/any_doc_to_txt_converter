"""
MOBI to text converter.
"""
import mobi
import tempfile
import os
from bs4 import BeautifulSoup
from .base import BaseConverter


class MOBIConverter(BaseConverter):
    """Converter for MOBI documents."""

    def convert(self, input_path: str, output_path: str) -> bool:
        """
        Convert MOBI to text.

        Args:
            input_path: Path to MOBI file
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
            self.logger.error(f"Error converting MOBI {input_path}: {str(e)}")
            return False

    def _extract_text(self, input_path: str) -> str:
        """
        Extract text from MOBI.

        Args:
            input_path: Path to MOBI file

        Returns:
            Extracted text
        """
        # Create a temporary directory for extraction
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Extract MOBI content
                tempdir, filepath = mobi.extract(input_path)

                # The extracted HTML file path
                html_file = filepath

                if not os.path.exists(html_file):
                    self.logger.error(f"Failed to extract MOBI content from {input_path}")
                    return ""

                # Read and parse HTML
                with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                    html_content = f.read()

                soup = BeautifulSoup(html_content, 'html.parser')

                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()

                text_parts = []

                if self.preserve_structure:
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
                    text_parts.append(text)

                return ''.join(text_parts).strip()

            except Exception as e:
                self.logger.error(f"Error extracting MOBI content: {str(e)}")
                # Fallback: try direct text extraction
                try:
                    with open(input_path, 'rb') as f:
                        content = f.read()
                        # Very basic text extraction as fallback
                        text = content.decode('utf-8', errors='ignore')
                        return text
                except:
                    return ""

    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        """Get supported file extensions."""
        return ['.mobi']
