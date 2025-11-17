"""
Configuration management for the document converter.
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, List


class Config:
    """Configuration manager for the document converter."""

    def __init__(self, config_path: str = None):
        """
        Initialize configuration.

        Args:
            config_path: Path to custom config file. If None, uses default.
        """
        self.config_data = self._load_config(config_path)
        self._validate_config()

    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """
        Load configuration from YAML file.

        Args:
            config_path: Path to config file

        Returns:
            Configuration dictionary
        """
        # Load default config
        default_config_path = Path(__file__).parent / "default_config.yaml"
        with open(default_config_path, 'r') as f:
            config = yaml.safe_load(f)

        # Override with custom config if provided
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                custom_config = yaml.safe_load(f)
                config.update(custom_config)

        return config

    def _validate_config(self):
        """Validate configuration values."""
        # Validate batch size
        if self.batch_size < 1 or self.batch_size > 50:
            raise ValueError("batch_size must be between 1 and 50")

        # Validate memory limit
        if self.max_memory_gb < 1:
            raise ValueError("max_memory_gb must be at least 1")

        # Create directories if they don't exist
        os.makedirs(self.input_folder, exist_ok=True)
        os.makedirs(self.output_folder, exist_ok=True)
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

    @property
    def input_folder(self) -> str:
        """Get input folder path."""
        return self.config_data.get('input_folder', './input')

    @property
    def output_folder(self) -> str:
        """Get output folder path."""
        return self.config_data.get('output_folder', './output')

    @property
    def batch_size(self) -> int:
        """Get batch size for parallel processing."""
        return self.config_data.get('batch_size', 10)

    @property
    def max_memory_gb(self) -> float:
        """Get maximum memory usage in GB."""
        return self.config_data.get('max_memory_gb', 10)

    @property
    def log_level(self) -> str:
        """Get logging level."""
        return self.config_data.get('log_level', 'INFO')

    @property
    def log_file(self) -> str:
        """Get log file path."""
        return self.config_data.get('log_file', './logs/converter.log')

    @property
    def supported_formats(self) -> List[str]:
        """Get list of supported file formats."""
        return self.config_data.get('supported_formats', [
            'pdf', 'docx', 'xlsx', 'pptx', 'html', 'htm',
            'md', 'markdown', 'epub', 'mobi'
        ])

    @property
    def preserve_structure(self) -> bool:
        """Get whether to preserve document structure."""
        return self.config_data.get('preserve_structure', True)

    @property
    def skip_on_error(self) -> bool:
        """Get whether to skip failed conversions."""
        return self.config_data.get('skip_on_error', True)

    @property
    def overwrite_existing(self) -> bool:
        """Get whether to overwrite existing output files."""
        return self.config_data.get('overwrite_existing', False)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value
        """
        return self.config_data.get(key, default)

    def __repr__(self) -> str:
        """String representation of config."""
        return f"Config(input={self.input_folder}, output={self.output_folder}, batch_size={self.batch_size})"
