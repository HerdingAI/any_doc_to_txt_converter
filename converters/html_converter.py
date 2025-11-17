"""
HTML to text converter.
"""
from bs4 import BeautifulSoup
from .base import BaseConverter


class HTMLConverter(BaseConverter):
    """Converter for HTML documents."""

    def convert(self, input_path: str, output_path: str) -> bool:
        """
        Convert HTML to text.

        Args:
            input_path: Path to HTML file
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
            self.logger.error(f"Error converting HTML {input_path}: {str(e)}")
            return False

    def _extract_text(self, input_path: str) -> str:
        """
        Extract text from HTML.

        Args:
            input_path: Path to HTML file

        Returns:
            Extracted text
        """
        with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, 'lxml')

        # Remove script and style elements
        for script in soup(["script", "style", "meta", "link"]):
            script.decompose()

        text_parts = []

        if self.preserve_structure:
            # Process elements with structure preservation
            for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'div', 'span', 'td', 'th']):
                text = element.get_text().strip()
                if not text:
                    continue

                tag_name = element.name

                # Handle headings
                if tag_name.startswith('h'):
                    level = int(tag_name[1])
                    text_parts.append(f"\n{'#' * level} {text}\n")
                # Handle list items
                elif tag_name == 'li':
                    text_parts.append(f"• {text}\n")
                # Handle table cells
                elif tag_name in ['td', 'th']:
                    text_parts.append(f"{text} | ")
                # Handle paragraphs and divs
                elif tag_name in ['p', 'div']:
                    text_parts.append(f"{text}\n\n")
                else:
                    text_parts.append(f"{text}\n")
        else:
            # Simple text extraction
            text = soup.get_text(separator='\n', strip=True)
            text_parts.append(text)

        # Clean up multiple newlines
        result = ''.join(text_parts)
        # Replace multiple newlines with maximum of 2
        while '\n\n\n' in result:
            result = result.replace('\n\n\n', '\n\n')

        return result.strip()

    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        """Get supported file extensions."""
        return ['.html', '.htm']
