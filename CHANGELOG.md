# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2024-12-19

### Added
- Modern `pyproject.toml` configuration for uv and pip package management
- `.gitignore` file with comprehensive Python project exclusions
- Entry point script `backup-extractor` for easy command-line usage
- Improved error handling with clear messages for missing directories
- Support for `uv` tooling as the primary package manager
- Dependency groups configuration using modern `[dependency-groups]` format
- `__init__.py` file in `src/` for proper package structure

### Changed
- **BREAKING**: Moved all Python code to `src/` directory following modern Python project structure (src-layout)
- **BREAKING**: Changed imports from absolute (`src.module`) to relative (`.module`) imports
- Updated `call_log_generator.create_call_log()` to accept and use `output_dir` parameter instead of always writing to current directory
- Modernized code style (removed unnecessary parentheses around conditionals)
- Improved README with clearer usage instructions and multiple installation/execution methods
- Updated build system to use hatchling with proper package configuration

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
