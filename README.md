![SMS Backup & Restore Exporter Banner](images/sms-backup-and-restore-banner.png)

# SMS Backup & Restore Exporter

> Export media files, call logs, and contact media from SMS Backup & Restore backup archives

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-2.2.0-blue.svg)](CHANGELOG.md)

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

The [SMS Backup & Restore](https://play.google.com/store/apps/details?id=com.riteshsahu.SMSBackupRestore&hl=en_US) app allows you to backup your entire SMS history, call logs, and contacts from Android devices. While the app provides an [online viewer](https://www.synctech.com.au/sms-backup-restore/view-backup/) for viewing backups, **exporting the actual data** from these backups can be challenging.

**This tool solves that problem** by providing a powerful, command-line utility to export data from SMS Backup & Restore archives. It can extract:

> **Note:** This application is based upon the original v1 concept and code from [@raleighlittles](https://github.com/raleighlittles) ([original repository](https://github.com/raleighlittles/SMS-backup-and-restore-extractor)) and has been greatly expanded and improved upon, with time and attention spend on code quality and tests. This version 2.0 represents a complete modernization with enhanced functionality and new features, better error handling, comprehensive testing, and modern Python tooling.

**Features include:**
- 📸 **Media files** from MMS messages (images, videos, audio, PDFs)
- 💬 **SMS/MMS text messages** exported to CSV files
- 📞 **Call logs** as structured CSV files with enhanced metadata
- 👤 **Contact media** from VCF/vCard files (photos, sounds, logos, keys)

---

## ✨ Features

- 🔄 **Automatic Deduplication** - Call logs are automatically deduplicated by timestamp
- 📁 **Flexible Input** - Accepts directories or individual files
- 🛣️ **Smart Path Handling** - Supports relative paths, `~` expansion, and absolute paths
- 🎨 **Selective Extraction** - Choose which media types to extract (images, videos, audio, PDFs)
- 📊 **CSV Export** - Call logs and SMS messages exported as clean, structured CSV files
- 🔍 **vCard Support** - Handles vCard versions 2.1, 3.0, and 4.0 with comprehensive field parsing
- ⚡ **Fast & Efficient** - Built with modern Python tooling (`uv`, `lxml`) using memory-efficient streaming parsers
- 📝 **Text Message Export** - Extract all SMS text messages and MMS text bodies to CSV
- 📱 **Enhanced Metadata** - Call logs include read status, SIM slot, and call features
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
git clone https://github.com/RichLewis007/sms-backup-and-restore-exporter.git
cd sms-backup-and-restore-exporter

# Install dependencies and the package
uv sync
```

### Method 2: Using pip

```bash
# Clone the repository
git clone https://github.com/RichLewis007/sms-backup-and-restore-exporter.git
cd sms-backup-and-restore-exporter

# Install in editable mode
pip install -e .
```

---

## 🚀 Quick Start

1. **Get your backup files** from the Android app "SMS Backup & Restore":
   - SMS backups: `sms-*.xml` files
   - Call logs: `calls-*.xml` files
   - Contacts: `*.vcf` files

2. **Extract MMS media from SMS backup XML files**:
   ```bash
   uv run xml-backup-exporter -t sms-mms-media -i ~/backups -o ~/extracted_media
   ```

3. **Extract SMS/MMS text messages**:
   ```bash
   uv run xml-backup-exporter -t sms-mms-text -i ~/backups -o ~/messages
   ```

4. **Generate call log**:
   ```bash
   uv run xml-backup-exporter -t calls -i ~/backups -o ~/call_logs
   ```

5. **Extract contact media**:
   ```bash
   uv run xml-backup-exporter -t vcf -i ~/backups -o ~/contact_media
   ```

---

## 📖 Usage Guide

### Basic Command Syntax

```bash
uv run xml-backup-exporter [-h] -t BACKUP_TYPE -i INPUT_DIR -o OUTPUT_DIR [OPTIONS]
```

### Command-Line Options

| Option | Description |
|--------|-------------|
| `-h, --help` | Show help message and exit |
| `-t, --backup-type` | Type of extraction: `sms-mms-media`, `sms-mms-text`, `calls`, or `vcf` |
| `-i, --input-dir` | Directory containing XML or VCF files (all matching files processed), or a single XML/VCF file (only that file processed) |
| `-o, --output-dir` | Directory where extracted files will be saved |
| `--no-images` | Don't extract image files from MMS messages (for `sms-mms-media` only) |
| `--no-videos` | Don't extract video files from MMS messages (for `sms-mms-media` only) |
| `--no-audio` | Don't extract audio files from MMS messages (for `sms-mms-media` only) |
| `--no-pdfs` | Don't extract PDF files from MMS messages (for `sms-mms-media` only) |

### Input Path Formats

The tool accepts various path formats for maximum flexibility:

```bash
# Relative directory
-i ./local/

# Relative file (processes only that file)
-i ./local/sms.xml

# Home directory expansion
-i ~/backups/

# Absolute path
-i /Users/username/Documents/backups

# Current directory
-i .
```

> **Note:** If you specify a file path, only that file will be processed. If you specify a directory, all matching XML/VCF files in that directory will be processed.

### Output Directory

The output directory will be **automatically created** if it doesn't exist. You don't need to create it beforehand.

---

## 📝 Examples

<details>
<summary><b>Click to expand examples</b></summary>

### Extract All MMS Media

Extract all MMS media attachments (images, videos, audio, and PDFs) from SMS backup XML files:

```bash
uv run xml-backup-exporter -t sms-mms-media -i ~/backups -o ~/extracted_media
```

### Extract Only Videos

Extract only video files from MMS messages, excluding images, audio, and PDFs:

```bash
uv run xml-backup-exporter -t sms-mms-media -i ~/backups -o ~/videos \
  --no-images --no-audio --no-pdfs
```

### Extract Images and PDFs Only

```bash
uv run xml-backup-exporter -t sms-mms-media -i ~/backups -o ~/media \
  --no-videos --no-audio
```

### Generate Call Log CSV

Create a deduplicated call log from all call backup files:

```bash
uv run xml-backup-exporter -t calls -i ~/backups -o ~/call_logs
```

The output will be a file named `call_log.csv` in the output directory.

### Extract SMS/MMS Text Messages

Extract all SMS text messages and MMS text bodies to a CSV file:

```bash
uv run xml-backup-exporter -t sms-mms-text -i ~/backups -o ~/messages
```

The output will be a file named `sms_messages.csv` in the output directory.

### Extract Contact Media from VCF

Extract photos, sounds, logos, and keys from contact backup files:

```bash
uv run xml-backup-exporter -t vcf -i ~/backups -o ~/contact_media
```

### Using a Single File as Input

The tool can process a single file instead of all files in a directory:

```bash
uv run xml-backup-exporter -t sms-mms-media -i ~/backups/sms-20231219.xml -o ~/output
# Note: Will process only sms-20231219.xml, not all files in the directory
```

### Alternative Execution Methods

If you installed with `pip install -e .`:

```bash
# Direct command (no 'uv run' needed)
xml-backup-exporter -t sms-mms-media -i ~/backups -o ~/output
```

Or run as a Python module:

```bash
# Using Python directly
python -m src.xml_backup_exporter -t sms-mms-media -i ~/backups -o ~/output

# Using uv with Python module
uv run python -m src.xml_backup_exporter -t sms-mms-media -i ~/backups -o ~/output
```

</details>

---

## 📊 Output Format

<details>
<summary><b>Click to expand output format details</b></summary>

### SMS/MMS Media Files

**Note:** The `sms-mms-media` export type extracts media attachments from MMS messages contained in SMS backup XML files. Regular SMS messages don't contain media attachments, so only MMS message media is extracted.

- **Filename preservation**: If the original MMS message included a filename, it will be used
- **Auto-naming**: If no filename exists, a random 10-character filename will be generated
- **Duplicate handling**: Duplicate files are automatically removed
- **Empty file removal**: Empty files are automatically removed
- **File safety**: Long filenames are automatically shortened to prevent filesystem issues

### SMS/MMS Text Messages CSV Format

The `sms_messages.csv` file contains the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| `Message Type` | Message type | `SMS` or `MMS` |
| `Date (timestamp)` | Unix timestamp in milliseconds | `1511043340171` |
| `Date` | Human-readable date | `"Nov 18, 2017 5:15:40 PM"` |
| `Address` | Phone number or address | `+15137392992` |
| `Contact Name` | Contact name | `John Doe` |
| `Type` | Message direction | `1` (incoming) or `2` (outgoing) |
| `Body` | Message text content | `"Hello, how are you?"` |
| `Read` | Read status | `1` (read) or `0` (unread) |
| `Status` | Message status | `0` (normal) |
| `Locked` | Locked status | `0` (unlocked) or `1` (locked) |
| `SIM ID` | SIM slot identifier | `1`, `2`, etc. |
| `Message ID` | Unique message identifier | `0` |

**Example CSV output:**

```csv
Message Type,Date (timestamp),Date,Address,Contact Name,Type,Body,Read,Status,Locked,SIM ID,Message ID
SMS,1511043340171,"Nov 18, 2017 5:15:40 PM",+15137392992,Julie Herrmann,1,"Hi",1,0,0,-1,0
SMS,1511044592590,"Nov 18, 2017 5:36:32 PM",+15137392992,Julie Herrmann,2,"I'm testing my new pixel 2 phone",1,0,0,-1,1
MMS,1737247128163,"Jan 18, 2025 7:38:48 PM",+15132650018,Heather Lewis,132,"Thank you!",1,null,0,1,2
```

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
| `Read status` | Read status (when available) | `1` (read) or `N/A` |
| `SIM slot` | SIM slot identifier (dual SIM) | `1`, `2`, or `N/A` |
| `Features` | Additional call features | `presentation:1` or `N/A` |
| `Call Id #` | Unique call identifier | `0` |

**Example CSV output:**

```csv
Call Date (timestamp),Call date,Call type,Caller name,Caller #,Call duration (s),Call duration,Read status,SIM slot,Features,Call Id #
1451965221740,"Jan 4, 2016 7:40:21 PM",Incoming,Dad,+18183457890,65,"1 minute, 5 seconds",1,1,N/A,0
1452020364934,"Jan 5, 2016 10:59:24 AM",Missed,(Unknown),+11234560987,N/A,N/A,1,1,N/A,1
1452107940226,"Jan 6, 2016 11:19:00 AM",Incoming,Michael Jordan,+11234567890,194,"3 minutes, 14 seconds",1,1,N/A,2
```

### vCard/VCF Media Files

- **Filename format**: `{ContactName}.{extension}` (e.g., `John Doe.jpg`)
- **Fallback naming**: If no contact name is available, a random 10-character filename is used
- **Supported media**: Photos, sounds, logos, and cryptographic keys
- **Format support**: Base64-encoded data and URL-based media downloads
- **Field parsing**: Comprehensive field support including:
  - Basic fields: Names, addresses, phone numbers, emails, URLs, notes
  - Dates: Birthday (BDAY), anniversary (ANNIVERSARY)
  - Contact info: Organization, title, role, gender
  - Multimedia: Photos, sounds, logos, keys
  - Advanced: Geographic coordinates, instant messenger handles, categories

</details>

---

## 🔧 Troubleshooting

<details>
<summary><b>Click to expand troubleshooting guide</b></summary>

### Common Issues

#### "Input directory does not exist"

**Problem:** The specified input directory doesn't exist.

**Solution:** Check that the path is correct and use `-i` with an existing directory:
```bash
# Verify the directory exists
ls ~/backups

# Use the correct path
uv run xml-backup-exporter -t sms-mms-media -i ~/backups -o ~/output
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
uv run xml-backup-exporter -t sms-mms-media -i /full/path/to/backups -o /full/path/to/output

# Or navigate to the directory first
cd ~/backups
uv run xml-backup-exporter -t sms-mms-media -i . -o ../output
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

</details>

---

## 🧪 Development

<details>
<summary><b>Click to expand development information</b></summary>

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
sms-backup-and-restore-exporter/
├── src/                          # Source code
│   ├── xml_backup_exporter.py   # Main entry point
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

</details>

---

## 🤝 Contributing

<details>
<summary><b>Click to expand contributing guidelines</b></summary>

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

</details>

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE.md](LICENSE.md) file for details.

### Disclaimer

Although the authors have endeavored to create a quality utility and test the code thoroughly, they cannot be held responsible for any damages, data loss, or issues that may arise from the use of this software. This software is provided "as is" without warranty of any kind, express or implied, as detailed in the MIT License. Users are encouraged to test the software with non-critical data first and maintain backups of their original files.

---

## 🙏 Acknowledgments

**Credits:**
- Original idea and v1 code: Raleigh Littles - GitHub: [@raleighlittles](https://github.com/raleighlittles)
- Updated and upgraded v2 app: Rich Lewis - GitHub: [@RichLewis007](https://github.com/RichLewis007)

This application is based upon the original code from [@raleighlittles](https://github.com/raleighlittles) and has been greatly expanded and improved upon with modern Python tooling, comprehensive testing, enhanced error handling, and improved documentation.

**Original v1 Source:**
The original v1 source code can be found at [https://github.com/raleighlittles/SMS-backup-and-restore-extractor](https://github.com/raleighlittles/SMS-backup-and-restore-extractor). Original contributors to the v1 repository include:
- Raleigh Littles - [@raleighlittles](https://github.com/raleighlittles)
- ImperialCodeMonkey - [@barretto94](https://github.com/barretto94)
- [@king44444](https://github.com/king44444)

**Supporting the Original Author:**
If you appreciate the original work that this project is based on, please consider supporting the original author:
- PayPal: [paypal.me/raleighlittles](https://paypal.me/raleighlittles)
- Buy Me a Coffee: [https://www.buymeacoffee.com/raleighlittles](https://www.buymeacoffee.com/raleighlittles)

**Additional Thanks:**
- Built with [SMS Backup & Restore](https://play.google.com/store/apps/details?id=com.riteshsahu.SMSBackupRestore&hl=en_US) backup format
- Powered by modern Python tooling: [uv](https://github.com/astral-sh/uv), [lxml](https://lxml.de/), [pytest](https://pytest.org/)

---

<details>
<summary><b>📚 Additional Resources</b></summary>

- [SMS Backup & Restore App](https://play.google.com/store/apps/details?id=com.riteshsahu.SMSBackupRestore&hl=en_US) - Official Android app
- [Online Backup Viewer](https://www.synctech.com.au/sms-backup-restore/view-backup/) - View backups online
- [vCard Specification](https://en.wikipedia.org/wiki/VCard) - Learn more about vCard format
- [CHANGELOG.md](CHANGELOG.md) - View version history and changes

</details>

---

<details>
<summary><b>⚠️ Limitations</b></summary>

- **No date information** for images in MMS backups - the backup format doesn't preserve image creation dates
- **EXIF data loss** - EXIF metadata is lost when images are stored in backups
- **Schema changes** - The backup app's schema may have changed since 2016; please report compatibility issues with your backup date

</details>

---

<details>
<summary><b>🗺️ Roadmap</b></summary>

Future enhancements planned:

- [x] Add ability to convert SMS messages to CSV format
- [ ] Improve error messages and user feedback
- [ ] Add support for additional media formats
- [ ] Create GUI version of the tool

</details>

---

**Version 2.2.0** - Type-safe and well-formatted codebase with comprehensive quality checks 🚀

For questions, issues, or contributions, please visit the [GitHub repository](https://github.com/RichLewis007/sms-backup-and-restore-exporter).
