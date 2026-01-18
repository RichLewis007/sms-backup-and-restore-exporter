# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **BREAKING**: Renamed command from `backup-extractor` to `xml-backup-exporter`
- **BREAKING**: Renamed main module from `backup_extractor.py` to `xml_backup_exporter.py`
- Updated README with detailed description acknowledging original work by @raleighlittles
- Added credits throughout source code and documentation

### Added
- Comprehensive module-level docstrings for all source files
- Detailed function documentation with Args, Returns, and Examples
- Improved inline comments explaining complex logic
- Package-level documentation in `__init__.py` with version information

### Changed
- **Refactored vCard/VCF parser** for improved maintainability and code quality
  - Replaced long if/elif chain with dispatch dictionary pattern
  - Improved error handling (replaced `sys.exit()` with proper exceptions)
  - Removed debug print statements, kept essential status messages
  - Better code organization with helper functions and clear separation of concerns
  - Enhanced type hints and documentation
  - Improved variable naming and code style
- Enhanced documentation across all source files:
  - Added module docstrings explaining purpose and functionality
  - Improved function docstrings with detailed parameter descriptions
  - Added usage examples in docstrings where helpful
  - Better code comments for maintainability

### Fixed
- Fixed potential index errors in multiline multimedia parsing
- Better error messages for malformed VCF files

## [2.0.0] - 2024-12-19

### Added
- Modern `pyproject.toml` configuration for uv and pip package management
- `.gitignore` file with comprehensive Python project exclusions
- Entry point script `xml-backup-exporter` for easy command-line usage
- Improved error handling with clear messages for missing directories
- Support for `uv` tooling as the primary package manager
- Dependency groups configuration using modern `[dependency-groups]` format
- `__init__.py` file in `src/` for proper package structure
- Path normalization to handle various input formats (`./local/`, `../parent/`, `~/backups/`, relative/absolute paths)
- Support for specifying input as either a directory or a single file (automatically uses parent directory if a file is provided)

### Changed
- **BREAKING**: Moved all Python code to `src/` directory following modern Python project structure (src-layout)
- **BREAKING**: Changed imports from absolute (`src.module`) to relative (`.module`) imports
- Updated `call_log_generator.create_call_log()` to accept and use `output_dir` parameter instead of always writing to current directory
- Modernized code style (removed unnecessary parentheses around conditionals)
- Improved README with clearer usage instructions and multiple installation/execution methods
- Updated build system to use hatchling with proper package configuration
- Enhanced path handling: input now accepts directories or files (auto-detects parent directory if file is specified)
- Improved path flexibility: supports relative paths (`./local/`), parent directories (`../parent/`), home directory expansion (`~/backups/`), and absolute paths

### Fixed
- Fixed critical bug in `contacts_vcard_extractor.py` where `key` variable was undefined in list comprehension (line 27)
- Fixed `call_log_generator.py` to write output to specified directory instead of current working directory
- Added proper error handling for missing input directories in all extraction functions
- Improved CSV writing with `newline=''` parameter for cross-platform compatibility
- Fixed entry point configuration in `pyproject.toml`

### Removed
- Removed deprecated `mms_images_extractor.py` file (replaced by `mms_media_extractor.py`)
- Removed old `backup_extractor.py` from project root (moved to `src/`)

### Documentation
- Updated README with modern installation instructions for uv
- Added multiple usage examples with clear path placeholders
- Documented alternative execution methods (uv run, python -m, pip install -e)

### Contributors
- Rich Lewis - GitHub: @RichLewis007 - Modernized project structure, fixed bugs, and updated tooling

---

## [1.0.0] - Previous Version

Initial release with basic functionality for:
- Extracting MMS media from SMS backup XML files
- Generating call logs from call backup XML files
- Extracting media from VCF/vCard contact files
