"""
VTT (WebVTT) to text converter.
"""
import re
from .base import BaseConverter


class VTTConverter(BaseConverter):
    """Converter for VTT (Web Video Text Tracks) transcript files."""

    def convert(self, input_path: str, output_path: str) -> bool:
        """
        Convert VTT to text.

        Args:
            input_path: Path to VTT file
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
            self.logger.error(f"Error converting VTT {input_path}: {str(e)}")
            return False

    def _extract_text(self, input_path: str) -> str:
        """
        Extract text from VTT file.

        Args:
            input_path: Path to VTT file

        Returns:
            Extracted text
        """
        with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        text_parts = []

        # Split into cue blocks
        lines = content.split('\n')

        # Remove WEBVTT header and metadata
        in_cue = False
        timestamp_pattern = re.compile(r'^\d{2}:\d{2}:\d{2}\.\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}\.\d{3}')
        cue_id_pattern = re.compile(r'^\d+$')

        current_timestamp = None
        current_text = []

        for line in lines:
            line = line.strip()

            # Skip WEBVTT header and NOTE sections
            if line.startswith('WEBVTT') or line.startswith('NOTE'):
                continue

            # Check if this is a timestamp line
            if timestamp_pattern.match(line):
                # If we have accumulated text, save it
                if current_text and self.preserve_structure:
                    if current_timestamp:
                        text_parts.append(f"[{current_timestamp}]\n")
                    text_parts.append(' '.join(current_text))
                    text_parts.append('\n\n')
                    current_text = []
                elif current_text:
                    text_parts.append(' '.join(current_text))
                    text_parts.append('\n')
                    current_text = []

                current_timestamp = line if self.preserve_structure else None
                in_cue = True
                continue

            # Skip cue identifiers (numbers)
            if cue_id_pattern.match(line):
                continue

            # Skip empty lines
            if not line:
                continue

            # This is subtitle text - remove VTT formatting tags
            clean_line = self._remove_vtt_tags(line)
            if clean_line:
                current_text.append(clean_line)

        # Add final accumulated text
        if current_text:
            if self.preserve_structure and current_timestamp:
                text_parts.append(f"[{current_timestamp}]\n")
            text_parts.append(' '.join(current_text))
            text_parts.append('\n')

        return ''.join(text_parts).strip()

    def _remove_vtt_tags(self, text: str) -> str:
        """
        Remove VTT formatting tags from text.

        Args:
            text: Text with potential VTT tags

        Returns:
            Clean text
        """
        # Remove <v Speaker> tags
        text = re.sub(r'<v\s+[^>]+>', '', text)
        text = re.sub(r'</v>', '', text)

        # Remove <c> class tags
        text = re.sub(r'<c\.[^>]+>', '', text)
        text = re.sub(r'<c>', '', text)
        text = re.sub(r'</c>', '', text)

        # Remove other common tags like <i>, <b>, <u>
        text = re.sub(r'</?[ibu]>', '', text)

        # Remove timestamp tags
        text = re.sub(r'<\d{2}:\d{2}:\d{2}\.\d{3}>', '', text)

        return text.strip()

    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        """Get supported file extensions."""
        return ['.vtt']
