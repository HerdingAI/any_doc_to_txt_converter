"""
Batch processor for parallel document conversion.
"""
import os
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Tuple
from tqdm import tqdm

from converters.factory import ConverterFactory
from core.memory_monitor import MemoryMonitor


class ConversionResult:
    """Result of a document conversion."""

    def __init__(self, input_path: str, output_path: str, success: bool, error: str = None):
        self.input_path = input_path
        self.output_path = output_path
        self.success = success
        self.error = error

    def __repr__(self) -> str:
        status = "SUCCESS" if self.success else "FAILED"
        return f"ConversionResult({self.input_path} -> {status})"


class BatchProcessor:
    """Process multiple documents in parallel."""

    def __init__(
        self,
        input_folder: str,
        output_folder: str,
        batch_size: int = 10,
        max_memory_gb: float = 10,
        preserve_structure: bool = True,
        skip_on_error: bool = True,
        overwrite_existing: bool = False
    ):
        """
        Initialize batch processor.

        Args:
            input_folder: Path to input folder
            output_folder: Path to output folder
            batch_size: Number of documents to process in parallel
            max_memory_gb: Maximum memory usage in GB
            preserve_structure: Whether to preserve document structure
            skip_on_error: Whether to skip failed conversions
            overwrite_existing: Whether to overwrite existing output files
        """
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder)
        self.batch_size = min(batch_size, 10)  # Cap at 10
        self.preserve_structure = preserve_structure
        self.skip_on_error = skip_on_error
        self.overwrite_existing = overwrite_existing

        self.memory_monitor = MemoryMonitor(max_memory_gb)
        self.logger = logging.getLogger('doc_converter')

        # Create output folder if it doesn't exist
        self.output_folder.mkdir(parents=True, exist_ok=True)

    def discover_documents(self) -> List[Tuple[str, str]]:
        """
        Discover all supported documents in input folder.

        Returns:
            List of (input_path, output_path) tuples
        """
        documents = []

        if not self.input_folder.exists():
            self.logger.error(f"Input folder does not exist: {self.input_folder}")
            return documents

        # Walk through all files in input folder
        for root, dirs, files in os.walk(self.input_folder):
            for filename in files:
                input_path = Path(root) / filename

                # Check if format is supported
                if not ConverterFactory.is_supported(str(input_path)):
                    continue

                # Generate output path
                relative_path = input_path.relative_to(self.input_folder)
                output_path = self.output_folder / relative_path.with_suffix('.txt')

                # Skip if output exists and not overwriting
                if output_path.exists() and not self.overwrite_existing:
                    self.logger.info(f"Skipping existing file: {output_path}")
                    continue

                documents.append((str(input_path), str(output_path)))

        self.logger.info(f"Discovered {len(documents)} documents to convert")
        return documents

    def _convert_single(self, input_path: str, output_path: str) -> ConversionResult:
        """
        Convert a single document.

        Args:
            input_path: Path to input document
            output_path: Path to output text file

        Returns:
            ConversionResult
        """
        try:
            # Get appropriate converter
            converter = ConverterFactory.get_converter(
                input_path,
                preserve_structure=self.preserve_structure
            )

            if not converter:
                error = f"No converter found for {input_path}"
                self.logger.error(error)
                return ConversionResult(input_path, output_path, False, error)

            # Create output directory if needed
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            # Convert document
            success, error = converter.safe_convert(input_path, output_path)

            if success:
                self.logger.info(f"Successfully converted: {input_path}")
                return ConversionResult(input_path, output_path, True)
            else:
                self.logger.error(f"Failed to convert {input_path}: {error}")
                return ConversionResult(input_path, output_path, False, error)

        except Exception as e:
            error = f"{type(e).__name__}: {str(e)}"
            self.logger.error(f"Exception converting {input_path}: {error}")
            return ConversionResult(input_path, output_path, False, error)

    def process_batch(self, documents: List[Tuple[str, str]]) -> List[ConversionResult]:
        """
        Process a batch of documents in parallel.

        Args:
            documents: List of (input_path, output_path) tuples

        Returns:
            List of ConversionResults
        """
        results = []

        if not documents:
            return results

        # Log memory status before processing
        self.memory_monitor.log_memory_status()

        # Process documents in parallel with progress bar
        with ThreadPoolExecutor(max_workers=self.batch_size) as executor:
            # Submit all tasks
            future_to_doc = {
                executor.submit(self._convert_single, inp, out): (inp, out)
                for inp, out in documents
            }

            # Process completed tasks with progress bar
            with tqdm(total=len(documents), desc="Converting documents", unit="doc") as pbar:
                for future in as_completed(future_to_doc):
                    result = future.result()
                    results.append(result)
                    pbar.update(1)

                    # Update progress bar description with status
                    success_count = sum(1 for r in results if r.success)
                    failed_count = len(results) - success_count
                    pbar.set_postfix({
                        'Success': success_count,
                        'Failed': failed_count
                    })

        # Log memory status after processing
        self.memory_monitor.log_memory_status()

        return results

    def process_all(self) -> Dict[str, List[ConversionResult]]:
        """
        Process all documents in input folder.

        Returns:
            Dictionary with 'successful' and 'failed' lists
        """
        # Discover all documents
        documents = self.discover_documents()

        if not documents:
            self.logger.warning("No documents found to convert")
            return {'successful': [], 'failed': []}

        # Process all documents
        all_results = self.process_batch(documents)

        # Separate successful and failed conversions
        successful = [r for r in all_results if r.success]
        failed = [r for r in all_results if not r.success]

        return {
            'successful': successful,
            'failed': failed
        }

    def generate_report(self, results: Dict[str, List[ConversionResult]]) -> str:
        """
        Generate a summary report.

        Args:
            results: Dictionary with 'successful' and 'failed' lists

        Returns:
            Report as string
        """
        successful = results['successful']
        failed = results['failed']
        total = len(successful) + len(failed)

        report_lines = [
            "\n" + "="*60,
            "CONVERSION REPORT",
            "="*60,
            f"Total documents: {total}",
            f"Successful: {len(successful)}",
            f"Failed: {len(failed)}",
            f"Success rate: {len(successful)/total*100:.1f}%" if total > 0 else "N/A",
            "="*60,
        ]

        if failed:
            report_lines.append("\nFailed conversions:")
            for result in failed:
                report_lines.append(f"  ✗ {result.input_path}")
                if result.error:
                    report_lines.append(f"    Error: {result.error}")

        if successful:
            report_lines.append(f"\nSuccessfully converted {len(successful)} documents")

        report_lines.append("="*60 + "\n")

        return "\n".join(report_lines)
