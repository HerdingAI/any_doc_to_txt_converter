"""
Base converter class for document conversion.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
import logging


class BaseConverter(ABC):
    """Abstract base class for document converters."""

    def __init__(self, preserve_structure: bool = True):
        """
        Initialize converter.

        Args:
            preserve_structure: Whether to preserve document structure
        """
        self.preserve_structure = preserve_structure
        self.logger = logging.getLogger('doc_converter')

    @abstractmethod
    def convert(self, input_path: str, output_path: str) -> bool:
        """
        Convert document to text.

        Args:
            input_path: Path to input document
            output_path: Path to output text file

        Returns:
            True if conversion successful, False otherwise
        """
        pass

    @abstractmethod
    def _extract_text(self, input_path: str) -> str:
        """
        Extract text from document.

        Args:
            input_path: Path to input document

        Returns:
            Extracted text content
        """
        pass

    def _validate_input(self, input_path: str) -> bool:
        """
        Validate input file exists.

        Args:
            input_path: Path to input file

        Returns:
            True if valid, False otherwise
        """
        path = Path(input_path)
        if not path.exists():
            self.logger.error(f"Input file does not exist: {input_path}")
            return False

        if not path.is_file():
            self.logger.error(f"Input path is not a file: {input_path}")
            return False

        return True

    def _write_output(self, text: str, output_path: str) -> bool:
        """
        Write text to output file.

        Args:
            text: Text content to write
            output_path: Path to output file

        Returns:
            True if successful, False otherwise
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)

            self.logger.debug(f"Successfully wrote output to: {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to write output to {output_path}: {str(e)}")
            return False

    def safe_convert(self, input_path: str, output_path: str) -> tuple[bool, Optional[str]]:
        """
        Safely convert document with error handling.

        Args:
            input_path: Path to input document
            output_path: Path to output text file

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            if not self._validate_input(input_path):
                return False, "Invalid input file"

            success = self.convert(input_path, output_path)
            if success:
                return True, None
            else:
                return False, "Conversion failed"

        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            self.logger.error(f"Error converting {input_path}: {error_msg}")
            return False, error_msg

    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        """
        Get list of supported file extensions.

        Returns:
            List of supported extensions
        """
        return []

    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(preserve_structure={self.preserve_structure})"
