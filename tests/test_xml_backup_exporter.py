"""Tests for xml_backup_exporter module."""
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from src.xml_backup_exporter import normalize_path


class TestNormalizePath:
    """Tests for the normalize_path function."""

    def test_normalize_relative_path(self, temp_dir):
        """Test normalizing a relative path."""
        # Create a test directory
        test_dir = temp_dir / "test_subdir"
        test_dir.mkdir()
        
        # Use a simple relative path
        result = normalize_path("test_subdir")
        assert Path(result).is_absolute()
        # Result should be absolute path ending with test_subdir
        assert result.endswith("test_subdir") or Path(result).name == "test_subdir"

    def test_normalize_absolute_path(self, temp_dir):
        """Test normalizing an absolute path."""
        result = normalize_path(str(temp_dir))
        assert Path(result).is_absolute()
        assert Path(result) == temp_dir

    def test_normalize_home_directory(self):
        """Test normalizing path with ~ expansion."""
        result = normalize_path("~/test")
        assert Path(result).is_absolute()
        assert str(result).startswith(str(Path.home()))

    def test_normalize_path_with_dots(self, temp_dir):
        """Test normalizing paths with . and .."""
        subdir = temp_dir / "subdir"
        subdir.mkdir()
        
        # Test with ../
        result = normalize_path(str(subdir / ".." / "subdir"))
        assert Path(result) == subdir
        
        # Test with ./
        result = normalize_path(str(subdir / "."))
        assert Path(result) == subdir

    def test_normalize_path_normalizes_separators(self):
        """Test that path separators are normalized."""
        # Mix forward and backward slashes (Windows-style)
        test_path = "test\\dir/subdir"
        result = normalize_path(test_path)
        assert os.path.normpath(test_path) in str(result)

    @patch('src.xml_backup_exporter.mms_media_extractor')
    @patch('src.xml_backup_exporter.call_log_generator')
    @patch('src.xml_backup_exporter.contacts_vcard_extractor')
    @patch('sys.argv', ['xml-backup-exporter', '-t', 'sms', '-i', '/test/input', '-o', '/test/output'])
    def test_main_sms_extraction(self, mock_vcf, mock_calls, mock_sms):
        """Test main function with sms backup type."""
        from src.xml_backup_exporter import main
        
        with patch('src.xml_backup_exporter.normalize_path', side_effect=lambda x: x):
            with patch('os.path.isfile', return_value=False):
                with patch('os.path.isdir', return_value=True):
                    main()
        
        mock_sms.reconstruct_mms_media.assert_called_once()

    @patch('src.xml_backup_exporter.mms_media_extractor')
    @patch('src.xml_backup_exporter.call_log_generator')
    @patch('src.xml_backup_exporter.contacts_vcard_extractor')
    @patch('sys.argv', ['xml-backup-exporter', '-t', 'calls', '-i', '/test/input', '-o', '/test/output'])
    def test_main_calls_extraction(self, mock_vcf, mock_calls, mock_sms):
        """Test main function with calls backup type."""
        from src.xml_backup_exporter import main
        
        with patch('src.xml_backup_exporter.normalize_path', side_effect=lambda x: x):
            with patch('os.path.isfile', return_value=False):
                with patch('os.path.isdir', return_value=True):
                    main()
        
        mock_calls.create_call_log.assert_called_once()

    @patch('src.xml_backup_exporter.mms_media_extractor')
    @patch('src.xml_backup_exporter.call_log_generator')
    @patch('src.xml_backup_exporter.contacts_vcard_extractor')
    @patch('sys.argv', ['xml-backup-exporter', '-t', 'vcf', '-i', '/test/input', '-o', '/test/output'])
    def test_main_vcf_extraction(self, mock_vcf, mock_calls, mock_sms):
        """Test main function with vcf backup type."""
        from src.xml_backup_exporter import main
        
        with patch('src.xml_backup_exporter.normalize_path', side_effect=lambda x: x):
            with patch('os.path.isfile', return_value=False):
                with patch('os.path.isdir', return_value=True):
                    main()
        
        mock_vcf.parse_contacts_from_vcf_files.assert_called_once()

    def test_main_handles_file_input(self, temp_dir):
        """Test that normalize_path correctly handles file paths."""
        from src.xml_backup_exporter import normalize_path
        
        # Create a test file
        test_file = temp_dir / "test.xml"
        test_file.touch()
        
        result = normalize_path(str(test_file))
        assert Path(result).is_absolute()
        # On macOS, resolve() may add /private prefix, so check that paths are equivalent
        resolved_path = test_file.resolve()
        # Both should point to the same file
        assert Path(result).samefile(resolved_path)
