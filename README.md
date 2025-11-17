# Document to Text Converter

A robust, high-performance Python system for converting various document formats to plain text. Supports batch processing with parallel execution, memory monitoring, and structure preservation.

## Features

- **Multiple Format Support**: PDF, DOCX, XLSX, PPTX, HTML, Markdown, EPUB, MOBI
- **Parallel Processing**: Process up to 10 documents simultaneously
- **Memory-Safe**: Built-in memory monitoring (configurable limit)
- **Structure Preservation**: Maintains headings, paragraphs, tables
- **Error Resilient**: Continues processing even if individual files fail
- **Progress Tracking**: Real-time progress bar with status updates
- **Flexible Configuration**: YAML-based config with CLI overrides
- **Comprehensive Logging**: Detailed logs for debugging and monitoring

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/HerdingAI/any_doc_to_txt_converter.git
cd any_doc_to_txt_converter
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

1. Place your documents in the `input` folder
2. Run the converter:
```bash
python main.py
```
3. Find converted text files in the `output` folder

## Usage

### Basic Usage

```bash
# Use default configuration
python main.py

# Use custom config file
python main.py --config my_config.yaml

# Override settings via command line
python main.py --input ./docs --output ./text --batch-size 5
```

### Command-Line Options

```
--config PATH           Path to configuration file (default: config.yaml)
--input PATH           Input folder containing documents
--output PATH          Output folder for text files
--batch-size N         Number of documents to process in parallel (1-10)
--max-memory N         Maximum memory usage in GB
--no-structure         Disable structure preservation
--overwrite            Overwrite existing output files
--log-level LEVEL      Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
--list-formats         List supported file formats and exit
```

### Examples

```bash
# Convert documents with custom folders
python main.py --input ~/Documents --output ~/TextFiles

# Process with smaller batch size (good for large files)
python main.py --batch-size 3

# Overwrite existing output files
python main.py --overwrite

# Disable structure preservation for plain text
python main.py --no-structure

# List supported formats
python main.py --list-formats
```

## Configuration

The system uses a YAML configuration file (`config.yaml`). Here's a sample configuration:

```yaml
# Input and Output Directories
input_folder: ./input
output_folder: ./output

# Processing Configuration
batch_size: 10              # Maximum parallel documents (1-10)
max_memory_gb: 10           # Maximum RAM usage in GB

# Logging Configuration
log_level: INFO
log_file: ./logs/converter.log

# Processing Options
preserve_structure: true    # Preserve document structure
skip_on_error: true         # Continue on failures
overwrite_existing: false   # Overwrite existing files
```

## Supported Formats

| Format | Extensions | Features |
|--------|-----------|----------|
| PDF | `.pdf` | Text extraction with page markers |
| Word | `.docx` | Headings, paragraphs, tables |
| Excel | `.xlsx` | All sheets, cell formatting |
| PowerPoint | `.pptx` | Slide content, tables |
| HTML | `.html`, `.htm` | Structured content, headings |
| Markdown | `.md`, `.markdown` | Structure preservation |
| EPUB | `.epub` | Chapter markers, structured text |
| MOBI | `.mobi` | E-book content extraction |

## Structure Preservation

When `preserve_structure: true` is enabled:

- **Headings**: Marked with `#` symbols (Markdown-style)
- **Tables**: Preserved with `|` separators
- **Pages**: PDF pages separated with markers
- **Slides**: PowerPoint slides numbered
- **Sheets**: Excel sheets labeled

Example output with structure:
```
# Chapter 1: Introduction

This is a paragraph of text.

## Section 1.1

[TABLE]
Header 1 | Header 2 | Header 3
Value 1  | Value 2  | Value 3
[/TABLE]
```

## Performance

- **Batch Processing**: Up to 10 documents in parallel
- **Memory Monitoring**: Tracks RAM usage to prevent crashes
- **Optimized Libraries**: Uses efficient parsing libraries
- **Error Handling**: Skips problematic files without stopping

### Recommended Settings

| Document Size | Batch Size | Max Memory |
|--------------|------------|------------|
| Small (<1MB) | 10 | 2GB |
| Medium (1-10MB) | 5 | 5GB |
| Large (>10MB) | 3 | 10GB |

## Logging

Logs are written to `./logs/converter.log` by default.

Log levels:
- **DEBUG**: Detailed processing information
- **INFO**: General progress and status
- **WARNING**: Non-critical issues
- **ERROR**: Failed conversions
- **CRITICAL**: System failures

View logs:
```bash
tail -f logs/converter.log
```

## Error Handling

The system is designed to be resilient:

1. **Invalid Files**: Skipped with error logged
2. **Unsupported Formats**: Ignored during discovery
3. **Conversion Failures**: Logged, processing continues
4. **Memory Limits**: Monitored and reported

Failed conversions are listed in the final report:
```
Failed conversions:
  ✗ ./input/corrupted.pdf
    Error: Invalid PDF structure
```

## Project Structure

```
any_doc_to_txt_converter/
├── config/                 # Configuration management
│   ├── settings.py
│   └── default_config.yaml
├── converters/            # Format-specific converters
│   ├── base.py
│   ├── pdf_converter.py
│   ├── docx_converter.py
│   ├── xlsx_converter.py
│   ├── pptx_converter.py
│   ├── html_converter.py
│   ├── markdown_converter.py
│   ├── epub_converter.py
│   ├── mobi_converter.py
│   └── factory.py
├── core/                  # Core processing engine
│   ├── batch_processor.py
│   ├── memory_monitor.py
│   └── logger.py
├── main.py               # CLI entry point
├── config.yaml           # User configuration
└── requirements.txt      # Dependencies
```

## Troubleshooting

### Issue: Out of Memory

**Solution**: Reduce `batch_size` or increase `max_memory_gb`
```bash
python main.py --batch-size 3 --max-memory 15
```

### Issue: Conversion Failures

**Solution**: Check logs for details
```bash
cat logs/converter.log | grep ERROR
```

### Issue: Missing Dependencies

**Solution**: Reinstall requirements
```bash
pip install -r requirements.txt --upgrade
```

### Issue: Unsupported Format

**Solution**: Check supported formats
```bash
python main.py --list-formats
```

## Development

### Adding a New Converter

1. Create converter class in `converters/`
2. Inherit from `BaseConverter`
3. Implement `convert()` and `_extract_text()` methods
4. Register in `ConverterFactory.CONVERTER_MAP`

Example:
```python
from converters.base import BaseConverter

class MyConverter(BaseConverter):
    def convert(self, input_path: str, output_path: str) -> bool:
        text = self._extract_text(input_path)
        return self._write_output(text, output_path)

    def _extract_text(self, input_path: str) -> str:
        # Your extraction logic
        return extracted_text

    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        return ['.myformat']
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/HerdingAI/any_doc_to_txt_converter/issues

## Changelog

### Version 1.0.0
- Initial release
- Support for 8 document formats
- Parallel batch processing
- Memory monitoring
- Structure preservation
- CLI interface
- YAML configuration

## Acknowledgments

Built with:
- pdfplumber - PDF text extraction
- python-docx - Word document processing
- openpyxl - Excel spreadsheet handling
- python-pptx - PowerPoint processing
- BeautifulSoup - HTML/XML parsing
- ebooklib - EPUB processing
- mobi - MOBI e-book handling
