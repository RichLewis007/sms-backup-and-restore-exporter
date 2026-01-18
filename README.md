![app-store-listing-image](https://images-na.ssl-images-amazon.com/images/I/71VnjnwSr4L.png)

# SMS Backup & Restore Extractor

> Extract media files, call logs, and contact media from SMS Backup & Restore backup archives

[![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](CHANGELOG.md)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Supported Formats](#-supported-formats)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage Guide](#-usage-guide)
- [Examples](#-examples)
- [Output Format](#-output-format)
- [Troubleshooting](#-troubleshooting)
- [Development](#-development)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)

---

## 🎯 Overview

The [SMS Backup & Restore](https://play.google.com/store/apps/details?id=com.riteshsahu.SMSBackupRestore&hl=en_US) app (official name: `com.riteshsahu.SMSBackupRestore`) allows you to backup your entire SMS history, call logs, and contacts from Android devices. While the app provides an [online viewer](https://www.synctech.com.au/sms-backup-restore/view-backup/) for viewing backups, **extracting the actual data** from these backups can be challenging.

**This tool solves that problem** by providing a powerful, command-line utility to extract:
- 📸 **Media files** from MMS messages (images, videos, audio, PDFs)
- 📞 **Call logs** as structured CSV files
- 👤 **Contact media** from VCF/vCard files (photos, sounds, logos, keys)

---

## ✨ Features

- 🔄 **Automatic Deduplication** - Call logs are automatically deduplicated by timestamp
- 📁 **Flexible Input** - Accepts directories or individual files
- 🛣️ **Smart Path Handling** - Supports relative paths, `~` expansion, and absolute paths
- 🎨 **Selective Extraction** - Choose which media types to extract (images, videos, audio, PDFs)
- 📊 **CSV Export** - Call logs exported as clean, structured CSV files
- 🔍 **vCard Support** - Handles vCard versions 2.1, 3.0, and 4.0
- ⚡ **Fast & Efficient** - Built with modern Python tooling (`uv`, `lxml`)
- 🧪 **Well Tested** - Comprehensive test suite included

---

## 📦 Supported Formats

### SMS/MMS Media
- **Images**: GIF, JPG, JPEG, PNG, HEIC, HEIF, BMP, WebP, AVIF, TIFF
- **Videos**: MP4, AVI, MPEG, 3GPP, OGG, WebM, QuickTime, WMV, FLV
- **Audio**: WAV, AMR, MP4, M4A, OGG, WebM, MPEG, FLAC, 3GPP
- **Documents**: PDF

### Call Logs
- Call types: Incoming, Outgoing, Missed, Voicemail, Rejected, Blocked, Answered Externally
- Automatic deduplication
- Human-readable duration formatting

### vCard/VCF Media
- **PHOTO** - Contact photos
- **SOUND** - Contact sounds/ringtones
- **LOGO** - Organization logos
- **KEY** - Cryptographic keys
- Supports Base64-encoded data and URL-based media

---

## 💻 Installation

### Prerequisites

- **Python 3.8+** (tested on Python 3.14.2)
- **[uv](https://github.com/astral-sh/uv)** - Modern Python package installer (recommended)
- **OR** pip (traditional Python package manager)

### Method 1: Using uv (Recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/RichLewis007/SMS-backup-and-restore-extractor.git
cd SMS-backup-and-restore-extractor

# Install dependencies and the package
uv sync
```

### Method 2: Using pip

```bash
# Clone the repository
git clone https://github.com/RichLewis007/SMS-backup-and-restore-extractor.git
cd SMS-backup-and-restore-extractor

# Install in editable mode
pip install -e .
```

---

## 🚀 Quick Start

1. **Get your backup files** from SMS Backup & Restore:
   - SMS backups: `sms-*.xml` files
   - Call logs: `calls-*.xml` files
   - Contacts: `*.vcf` files

2. **Extract MMS media**:
   ```bash
   uv run backup-extractor -t sms -i ~/backups -o ~/extracted_media
   ```

3. **Generate call log**:
   ```bash
   uv run backup-extractor -t calls -i ~/backups -o ~/call_logs
   ```

4. **Extract contact media**:
   ```bash
   uv run backup-extractor -t vcf -i ~/backups -o ~/contact_media
   ```

---

## 📖 Usage Guide

### Basic Command Syntax

```bash
uv run backup-extractor [-h] -t BACKUP_TYPE -i INPUT_DIR -o OUTPUT_DIR [OPTIONS]
```

### Command-Line Options

| Option | Description |
|--------|-------------|
| `-h, --help` | Show help message and exit |
| `-t, --backup-type` | Type of extraction: `sms`, `calls`, or `vcf` |
| `-i, --input-dir` | Directory containing XML or VCF files (can also be a single file) |
| `-o, --output-dir` | Directory where extracted files will be saved |
| `--no-images` | Don't extract image files (SMS only) |
| `--no-videos` | Don't extract video files (SMS only) |
| `--no-audio` | Don't extract audio files (SMS only) |
| `--no-pdfs` | Don't extract PDF files (SMS only) |

### Input Path Formats

The tool accepts various path formats for maximum flexibility:

```bash
# Relative directory
-i ./local/

# Relative file (uses parent directory automatically)
-i ./local/sms.xml

# Home directory expansion
-i ~/backups/

# Absolute path
-i /Users/username/Documents/backups

# Current directory
-i .
```

> **Note:** If you specify a file path, the program will automatically use its parent directory.

### Output Directory

The output directory will be **automatically created** if it doesn't exist. You don't need to create it beforehand.

---

## 📝 Examples

### Extract All MMS Media

Extract all images, videos, audio, and PDFs from SMS backups:

```bash
uv run backup-extractor -t sms -i ~/backups -o ~/extracted_media
```

### Extract Only Videos

Extract only video files, excluding images, audio, and PDFs:

```bash
uv run backup-extractor -t sms -i ~/backups -o ~/videos \
  --no-images --no-audio --no-pdfs
```

### Extract Images and PDFs Only

```bash
uv run backup-extractor -t sms -i ~/backups -o ~/media \
  --no-videos --no-audio
```

### Generate Call Log CSV

Create a deduplicated call log from all call backup files:

```bash
uv run backup-extractor -t calls -i ~/backups -o ~/call_logs
```

The output will be a file named `call_log.csv` in the output directory.

### Extract Contact Media from VCF

Extract photos, sounds, logos, and keys from contact backup files:

```bash
uv run backup-extractor -t vcf -i ~/backups -o ~/contact_media
```

### Using a Single File as Input

The tool automatically detects if you provide a file instead of a directory:

```bash
uv run backup-extractor -t sms -i ~/backups/sms-20231219.xml -o ~/output
# Note: Will use ~/backups/ as the input directory
```

### Alternative Execution Methods

If you installed with `pip install -e .`:

```bash
# Direct command (no 'uv run' needed)
backup-extractor -t sms -i ~/backups -o ~/output
```

Or run as a Python module:

```bash
# Using Python directly
python -m src.backup_extractor -t sms -i ~/backups -o ~/output

# Using uv with Python module
uv run python -m src.backup_extractor -t sms -i ~/backups -o ~/output
```

---

## 📊 Output Format

### SMS/MMS Media Files

- **Filename preservation**: If the original MMS message included a filename, it will be used
- **Auto-naming**: If no filename exists, a random 10-character filename will be generated
- **Duplicate handling**: Duplicate files are automatically removed
- **Empty file removal**: Empty files are automatically removed
- **File safety**: Long filenames are automatically shortened to prevent filesystem issues

### Call Log CSV Format

The `call_log.csv` file contains the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| `Call Date (timestamp)` | Unix timestamp in milliseconds | `1451965221740` |
| `Call date` | Human-readable date | `"Jan 4, 2016 7:40:21 PM"` |
| `Call type` | Type of call | `Incoming`, `Outgoing`, `Missed`, etc. |
| `Caller name` | Contact name | `John Doe` |
| `Caller #` | Phone number | `+1234567890` |
| `Call duration (s)` | Duration in seconds | `65` |
| `Call duration` | Human-readable duration | `"1 minute, 5 seconds"` |
| `Call Id #` | Unique call identifier | `0` |

**Example CSV output:**

```csv
Call Date (timestamp),Call date,Call type,Caller name,Caller #,Call duration (s),Call duration,Call Id #
1451965221740,"Jan 4, 2016 7:40:21 PM",Incoming,Dad,+18183457890,65,"1 minute, 5 seconds",0
1452020364934,"Jan 5, 2016 10:59:24 AM",Missed,(Unknown),+11234560987,N/A,N/A,1
1452107940226,"Jan 6, 2016 11:19:00 AM",Incoming,Michael Jordan,+11234567890,194,"3 minutes, 14 seconds",2
```

### vCard/VCF Media Files

- **Filename format**: `{ContactName}.{extension}` (e.g., `John Doe.jpg`)
- **Fallback naming**: If no contact name is available, a random 10-character filename is used
- **Supported media**: Photos, sounds, logos, and cryptographic keys
- **Format support**: Base64-encoded data and URL-based media downloads

---

## 🔧 Troubleshooting

### Common Issues

#### "Input directory does not exist"

**Problem:** The specified input directory doesn't exist.

**Solution:** Check that the path is correct and use `-i` with an existing directory:
```bash
# Verify the directory exists
ls ~/backups

# Use the correct path
uv run backup-extractor -t sms -i ~/backups -o ~/output
```

#### "No calls found to write to call log"

**Problem:** No matching XML files found in the input directory.

**Solution:** 
- Ensure your call backup files start with `calls` and have `.xml` extension
- Check that files are in the correct directory
- Verify file naming: `calls-20231219.xml`, `calls.xml`, etc.

#### "FileNotFoundError" or path-related errors

**Problem:** Path format issues.

**Solution:** Try using absolute paths or ensure relative paths are correct:
```bash
# Use absolute path
uv run backup-extractor -t sms -i /full/path/to/backups -o /full/path/to/output

# Or navigate to the directory first
cd ~/backups
uv run backup-extractor -t sms -i . -o ../output
```

#### Python version issues

**Problem:** Incompatible Python version.

**Solution:** Ensure you're using Python 3.8 or higher:
```bash
python3 --version  # Should show 3.8 or higher
```

#### Missing dependencies

**Problem:** Import errors or missing packages.

**Solution:** Reinstall dependencies:
```bash
# Using uv
uv sync

# Using pip
pip install -r requirements.txt
```

### Getting Help

If you encounter issues:

1. **Check the error message** - It often contains helpful information
2. **Verify your file format** - Ensure your backup files match expected formats
3. **Include backup date** - If reporting an issue, include when your backup was generated
4. **Check file permissions** - Ensure you have read access to input files and write access to output directory

---

## 🧪 Development

### Running Tests

The project includes a comprehensive test suite:

```bash
# Run all tests
uv run pytest tests/

# Run with verbose output
uv run pytest tests/ -v

# Run with coverage report
uv run pytest tests/ --cov=src --cov-report=html
```

### Project Structure

```
SMS-backup-and-restore-extractor/
├── src/                          # Source code
│   ├── backup_extractor.py      # Main entry point
│   ├── mms_media_extractor.py   # MMS media extraction
│   ├── call_log_generator.py    # Call log CSV generation
│   ├── contacts_vcard_extractor.py  # VCF/vCard parsing
│   ├── vcf_field_parser.py      # VCF field parsing utilities
│   └── vcard_multimedia_helper.py   # vCard media handling
├── tests/                        # Test suite
├── pyproject.toml               # Project configuration
├── requirements.txt             # Python dependencies
├── LICENSE.md                   # MIT License
└── README.md                    # This file
```

### Contributing

We welcome contributions! Please see our [Contributing Guidelines](#-contributing) below.

---

## 🤝 Contributing

Contributions are welcome and appreciated! Here's how you can help:

### Reporting Issues

When reporting bugs or requesting features, please include:

- **Description** of the issue or feature request
- **Steps to reproduce** (for bugs)
- **Backup file date** when the backup was generated (for compatibility issues)
- **Python version** and system information
- **Error messages** or relevant output

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and add tests if applicable
4. **Run the test suite**: `uv run pytest tests/`
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to the branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Code Style

- Follow PEP 8 Python style guidelines
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE.md](LICENSE.md) file for details.

---

## 🙏 Acknowledgments

- Original project by [raleighlittles](https://github.com/raleighlittles)
- Built with [SMS Backup & Restore](https://play.google.com/store/apps/details?id=com.riteshsahu.SMSBackupRestore) backup format
- Powered by modern Python tooling: [uv](https://github.com/astral-sh/uv), [lxml](https://lxml.de/), [pytest](https://pytest.org/)

---

## 📚 Additional Resources

- [SMS Backup & Restore App](https://play.google.com/store/apps/details?id=com.riteshsahu.SMSBackupRestore) - Official Android app
- [Online Backup Viewer](https://www.synctech.com.au/sms-backup-restore/view-backup/) - View backups online
- [vCard Specification](https://en.wikipedia.org/wiki/VCard) - Learn more about vCard format
- [CHANGELOG.md](CHANGELOG.md) - View version history and changes

---

## ⚠️ Limitations

- **No date information** for images in MMS backups - the backup format doesn't preserve image creation dates
- **EXIF data loss** - EXIF metadata is lost when images are stored in backups
- **Schema changes** - The backup app's schema may have changed since 2016; please report compatibility issues with your backup date

---

## 🗺️ Roadmap

Future enhancements planned:

- [ ] Refactor vCard/VCF parser for better maintainability
- [ ] Add ability to convert SMS messages to CSV format
- [ ] Improve error messages and user feedback
- [ ] Add support for additional media formats
- [ ] Create GUI version of the tool

---

**Version 2.0.0** - Modernized and enhanced for 2026 🚀

For questions, issues, or contributions, please visit the [GitHub repository](https://github.com/RichLewis007/SMS-backup-and-restore-extractor).
