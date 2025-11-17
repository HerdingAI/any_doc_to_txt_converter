"""
Markdown to text converter.
"""
import markdown
from bs4 import BeautifulSoup
from .base import BaseConverter


class MarkdownConverter(BaseConverter):
    """Converter for Markdown documents."""

    def convert(self, input_path: str, output_path: str) -> bool:
        """
        Convert Markdown to text.

        Args:
            input_path: Path to Markdown file
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
            self.logger.error(f"Error converting Markdown {input_path}: {str(e)}")
            return False

    def _extract_text(self, input_path: str) -> str:
        """
        Extract text from Markdown.

        Args:
            input_path: Path to Markdown file

        Returns:
            Extracted text
        """
        with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
            md_content = f.read()

        if self.preserve_structure:
            # Keep markdown as-is (it's already text with structure)
            return md_content.strip()
        else:
            # Convert to HTML then extract plain text
            html = markdown.markdown(md_content)
            soup = BeautifulSoup(html, 'html.parser')
            return soup.get_text(separator='\n', strip=True)

    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        """Get supported file extensions."""
        return ['.md', '.markdown']
