"""
SRT (SubRip) to text converter.
"""
import re
from .base import BaseConverter


class SRTConverter(BaseConverter):
    """Converter for SRT (SubRip) subtitle files."""

    def convert(self, input_path: str, output_path: str) -> bool:
        """
        Convert SRT to text.

        Args:
            input_path: Path to SRT file
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
            self.logger.error(f"Error converting SRT {input_path}: {str(e)}")
            return False

    def _extract_text(self, input_path: str) -> str:
        """
        Extract text from SRT file.

        Args:
            input_path: Path to SRT file

        Returns:
            Extracted text
        """
        with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        text_parts = []

        # SRT format:
        # 1
        # 00:00:00,000 --> 00:00:02,000
        # Subtitle text here
        # Can span multiple lines
        #
        # 2
        # 00:00:02,000 --> 00:00:04,000
        # Next subtitle

        # Split into subtitle blocks
        blocks = re.split(r'\n\s*\n', content.strip())

        for block in blocks:
            if not block.strip():
                continue

            lines = block.strip().split('\n')

            if len(lines) < 2:
                continue

            # First line is the subtitle number
            # Second line is the timestamp
            # Rest are the subtitle text

            subtitle_num = lines[0].strip()
            timestamp_pattern = re.compile(r'\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}')

            timestamp_line = None
            text_start_idx = 1

            # Find the timestamp line (usually line 1, but could be line 0 if no number)
            for i, line in enumerate(lines):
                if timestamp_pattern.search(line):
                    timestamp_line = line.strip()
                    text_start_idx = i + 1
                    break

            if text_start_idx >= len(lines):
                continue

            # Get subtitle text (everything after timestamp)
            subtitle_text = ' '.join(lines[text_start_idx:])

            # Remove HTML/formatting tags
            subtitle_text = self._remove_html_tags(subtitle_text)

            if subtitle_text.strip():
                if self.preserve_structure and timestamp_line:
                    text_parts.append(f"[{timestamp_line}]\n")

                text_parts.append(subtitle_text.strip())
                text_parts.append('\n\n')

        return ''.join(text_parts).strip()

    def _remove_html_tags(self, text: str) -> str:
        """
        Remove HTML tags from subtitle text.

        Args:
            text: Text with potential HTML tags

        Returns:
            Clean text
        """
        # Remove common HTML tags used in SRT files
        text = re.sub(r'</?[ibu]>', '', text)
        text = re.sub(r'</?font[^>]*>', '', text)
        text = re.sub(r'<br\s*/?>', ' ', text)
        text = re.sub(r'<[^>]+>', '', text)

        return text.strip()

    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        """Get supported file extensions."""
        return ['.srt']
