"""
Memory monitoring for the document converter.
"""
import psutil
from typing import Optional
import logging


class MemoryMonitor:
    """Monitor system memory usage."""

    def __init__(self, max_memory_gb: float):
        """
        Initialize memory monitor.

        Args:
            max_memory_gb: Maximum allowed memory usage in GB
        """
        self.max_memory_bytes = max_memory_gb * 1024 * 1024 * 1024
        self.logger = logging.getLogger('doc_converter')

    def get_current_usage(self) -> float:
        """
        Get current memory usage in bytes.

        Returns:
            Current memory usage in bytes
        """
        process = psutil.Process()
        return process.memory_info().rss

    def get_current_usage_gb(self) -> float:
        """
        Get current memory usage in GB.

        Returns:
            Current memory usage in GB
        """
        return self.get_current_usage() / (1024 * 1024 * 1024)

    def is_memory_available(self, required_bytes: Optional[float] = None) -> bool:
        """
        Check if memory is available for processing.

        Args:
            required_bytes: Additional memory required (optional)

        Returns:
            True if memory is available, False otherwise
        """
        current = self.get_current_usage()
        required = required_bytes or 0

        if current + required > self.max_memory_bytes:
            self.logger.warning(
                f"Memory limit approaching: {current / (1024**3):.2f}GB / "
                f"{self.max_memory_bytes / (1024**3):.2f}GB"
            )
            return False

        return True

    def get_system_memory_info(self) -> dict:
        """
        Get system memory information.

        Returns:
            Dictionary with memory stats
        """
        vm = psutil.virtual_memory()
        process = psutil.Process()
        process_mem = process.memory_info().rss

        return {
            'total_gb': vm.total / (1024**3),
            'available_gb': vm.available / (1024**3),
            'used_gb': vm.used / (1024**3),
            'percent': vm.percent,
            'process_gb': process_mem / (1024**3)
        }

    def log_memory_status(self):
        """Log current memory status."""
        info = self.get_system_memory_info()
        self.logger.info(
            f"Memory Status - Process: {info['process_gb']:.2f}GB, "
            f"System: {info['used_gb']:.2f}GB / {info['total_gb']:.2f}GB "
            f"({info['percent']:.1f}%)"
        )
