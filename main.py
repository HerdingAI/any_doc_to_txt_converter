#!/usr/bin/env python3
"""
Document to Text Converter - Main Entry Point

Converts various document formats to plain text with structure preservation.
Supports: PDF, DOCX, XLSX, PPTX, HTML, Markdown, EPUB, MOBI
"""
import argparse
import sys
from pathlib import Path

from config.settings import Config
from core.logger import Logger
from core.batch_processor import BatchProcessor
from converters.factory import ConverterFactory


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Convert documents to text format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use default config file (config.yaml)
  python main.py

  # Use custom config file
  python main.py --config my_config.yaml

  # Override config with command-line arguments
  python main.py --input ./docs --output ./text --batch-size 5

  # Show supported formats
  python main.py --list-formats

Supported formats: PDF, DOCX, XLSX, PPTX, HTML, Markdown, EPUB, MOBI
        """
    )

    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )

    parser.add_argument(
        '--input',
        type=str,
        help='Input folder containing documents (overrides config)'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='Output folder for text files (overrides config)'
    )

    parser.add_argument(
        '--batch-size',
        type=int,
        help='Number of documents to process in parallel (1-10, overrides config)'
    )

    parser.add_argument(
        '--max-memory',
        type=float,
        help='Maximum memory usage in GB (overrides config)'
    )

    parser.add_argument(
        '--no-structure',
        action='store_true',
        help='Disable structure preservation'
    )

    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite existing output files'
    )

    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Logging level (overrides config)'
    )

    parser.add_argument(
        '--list-formats',
        action='store_true',
        help='List supported file formats and exit'
    )

    return parser.parse_args()


def list_supported_formats():
    """Print supported file formats."""
    print("\n" + "="*60)
    print("SUPPORTED FILE FORMATS")
    print("="*60)

    formats = {
        'PDF Documents': ['.pdf'],
        'Microsoft Office': ['.docx', '.xlsx', '.pptx'],
        'Web Documents': ['.html', '.htm'],
        'Markdown': ['.md', '.markdown'],
        'E-books': ['.epub', '.mobi']
    }

    for category, extensions in formats.items():
        print(f"\n{category}:")
        for ext in extensions:
            print(f"  • {ext}")

    print("\n" + "="*60 + "\n")


def main():
    """Main entry point."""
    args = parse_arguments()

    # Handle --list-formats
    if args.list_formats:
        list_supported_formats()
        return 0

    try:
        # Load configuration
        config_path = args.config if Path(args.config).exists() else None
        config = Config(config_path)

        # Override config with command-line arguments
        if args.input:
            config.config_data['input_folder'] = args.input
        if args.output:
            config.config_data['output_folder'] = args.output
        if args.batch_size:
            config.config_data['batch_size'] = args.batch_size
        if args.max_memory:
            config.config_data['max_memory_gb'] = args.max_memory
        if args.log_level:
            config.config_data['log_level'] = args.log_level
        if args.no_structure:
            config.config_data['preserve_structure'] = False
        if args.overwrite:
            config.config_data['overwrite_existing'] = True

        # Set up logging
        logger = Logger.setup(config.log_file, config.log_level)

        # Print banner
        print("\n" + "="*60)
        print("DOCUMENT TO TEXT CONVERTER")
        print("="*60)
        print(f"Input folder:  {config.input_folder}")
        print(f"Output folder: {config.output_folder}")
        print(f"Batch size:    {config.batch_size}")
        print(f"Max memory:    {config.max_memory_gb} GB")
        print(f"Preserve structure: {config.preserve_structure}")
        print("="*60 + "\n")

        logger.info("Starting document conversion process")
        logger.info(f"Configuration: {config}")

        # Create batch processor
        processor = BatchProcessor(
            input_folder=config.input_folder,
            output_folder=config.output_folder,
            batch_size=config.batch_size,
            max_memory_gb=config.max_memory_gb,
            preserve_structure=config.preserve_structure,
            skip_on_error=config.skip_on_error,
            overwrite_existing=config.overwrite_existing
        )

        # Process all documents
        results = processor.process_all()

        # Generate and print report
        report = processor.generate_report(results)
        print(report)
        logger.info("Conversion process completed")

        # Write report to log
        logger.info(report)

        # Return exit code based on results
        if results['failed'] and not config.skip_on_error:
            return 1
        return 0

    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user")
        return 130

    except Exception as e:
        print(f"\nERROR: {str(e)}", file=sys.stderr)
        if 'logger' in locals():
            logger.error(f"Fatal error: {str(e)}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
