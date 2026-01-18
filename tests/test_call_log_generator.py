"""Tests for call_log_generator module."""
import csv
from pathlib import Path

import pytest

from src.call_log_generator import create_call_log, get_human_readable_duration


class TestGetHumanReadableDuration:
    """Tests for the get_human_readable_duration function."""

    def test_zero_seconds(self):
        """Test formatting 0 seconds."""
        result = get_human_readable_duration("0")
        assert result == "0 seconds"

    def test_single_second(self):
        """Test formatting 1 second."""
        result = get_human_readable_duration("1")
        assert result == "1 second"

    def test_multiple_seconds(self):
        """Test formatting multiple seconds."""
        result = get_human_readable_duration("45")
        assert result == "45 seconds"

    def test_single_minute(self):
        """Test formatting 1 minute."""
        result = get_human_readable_duration("60")
        assert "1 minute" in result
        assert "second" not in result.lower() or "0 second" in result

    def test_minutes_and_seconds(self):
        """Test formatting minutes and seconds."""
        result = get_human_readable_duration("125")
        assert "2 minutes" in result
        assert "5 seconds" in result

    def test_hours_minutes_seconds(self):
        """Test formatting hours, minutes, and seconds."""
        result = get_human_readable_duration("3661")  # 1 hour, 1 minute, 1 second
        assert "1 hours" in result or "1 hour" in result
        assert "1 minute" in result
        assert "1 second" in result

    def test_multiple_hours(self):
        """Test formatting multiple hours."""
        result = get_human_readable_duration("7200")  # 2 hours
        assert "2 hours" in result


class TestCreateCallLog:
    """Tests for the create_call_log function."""

    def test_create_call_log_with_valid_xml(self, temp_dir, sample_calls_xml_file):
        """Test creating call log from valid XML file."""
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        
        # Create the calls XML file in a subdirectory
        calls_dir = temp_dir / "calls_dir"
        calls_dir.mkdir()
        calls_xml = calls_dir / "calls-test.xml"
        calls_xml.write_text(sample_calls_xml_file.read_text())
        
        create_call_log(str(calls_dir), str(output_dir))
        
        # Check that CSV file was created
        csv_file = output_dir / "call_log.csv"
        assert csv_file.exists()
        
        # Verify CSV content
        with open(csv_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2
            
            # Check first call
            assert rows[0]["Call type"] == "Incoming"  # type 1
            assert rows[0]["Caller name"] == "John Doe"
            assert rows[0]["Caller #"] == "+1234567890"
            
            # Verify all expected fields are present (including new ones)
            assert "Read status" in rows[0]
            assert "SIM slot" in rows[0]
            assert "Features" in rows[0]

    def test_create_call_log_no_calls(self, temp_dir):
        """Test creating call log when no calls XML files exist."""
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        
        empty_dir = temp_dir / "empty_dir"
        empty_dir.mkdir()
        
        # Should not raise an error, just return early or create empty CSV
        create_call_log(str(empty_dir), str(output_dir))
        
        # CSV might not exist if no calls found, or might be empty
        csv_file = output_dir / "call_log.csv"
        # The function should handle this gracefully

    def test_create_call_log_deduplicates(self, temp_dir):
        """Test that duplicate calls (same timestamp) are deduplicated."""
        # Create XML with duplicate timestamps
        xml_content = """<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<calls count="3">
    <call number="+1234567890" duration="120" date="1609459200000" type="1" readable_date="Jan 1, 2021 12:00:00 AM" contact_name="John Doe" />
    <call number="+1234567890" duration="120" date="1609459200000" type="1" readable_date="Jan 1, 2021 12:00:00 AM" contact_name="John Doe" />
    <call number="+9876543210" duration="45" date="1609545600000" type="2" readable_date="Jan 2, 2021 12:00:00 AM" contact_name="Jane Smith" />
</calls>"""
        
        calls_dir = temp_dir / "calls_dir"
        calls_dir.mkdir()
        xml_file = calls_dir / "calls-duplicate.xml"
        xml_file.write_text(xml_content)
        
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        
        create_call_log(str(calls_dir), str(output_dir))
        
        csv_file = output_dir / "call_log.csv"
        with open(csv_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            # Should only have 2 unique calls (duplicate removed)
            assert len(rows) == 2

    def test_create_call_log_missed_calls(self, temp_dir):
        """Test that missed calls don't have duration fields."""
        xml_content = """<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<calls count="1">
    <call number="+1234567890" duration="0" date="1609459200000" type="3" readable_date="Jan 1, 2021 12:00:00 AM" contact_name="John Doe" />
</calls>"""
        
        calls_dir = temp_dir / "calls_dir"
        calls_dir.mkdir()
        xml_file = calls_dir / "calls-missed.xml"
        xml_file.write_text(xml_content)
        
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        
        create_call_log(str(calls_dir), str(output_dir))
        
        csv_file = output_dir / "call_log.csv"
        with open(csv_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]["Call type"] == "Missed"
            assert rows[0]["Call duration"] == "N/A"
            assert rows[0]["Call duration (s)"] == "N/A"
            # Verify new fields are present
            assert "Read status" in rows[0]
            assert "SIM slot" in rows[0]
            assert "Features" in rows[0]

    def test_create_call_log_with_new_fields(self, temp_dir):
        """Test that new call log fields (Read status, SIM slot, Features) are extracted."""
        xml_content = """<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<calls count="2">
    <call number="+1234567890" duration="120" date="1609459200000" type="1" 
          readable_date="Jan 1, 2021 12:00:00 AM" contact_name="John Doe" 
          read="1" subscription_id="1" presentation="1" />
    <call number="+9876543210" duration="45" date="1609545600000" type="2" 
          readable_date="Jan 2, 2021 12:00:00 AM" contact_name="Jane Smith" 
          read="0" subscription_id="2" post_dial_digits="123" 
          subscription_component_name="SIM2" />
</calls>"""
        
        calls_dir = temp_dir / "calls_dir"
        calls_dir.mkdir()
        xml_file = calls_dir / "calls-enhanced.xml"
        xml_file.write_text(xml_content)
        
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        
        create_call_log(str(calls_dir), str(output_dir))
        
        csv_file = output_dir / "call_log.csv"
        with open(csv_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2
            
            # Check first call with basic new fields
            assert rows[0]["Read status"] == "1"
            assert rows[0]["SIM slot"] == "1"
            
            # Check second call with all new fields including features
            assert rows[1]["Read status"] == "0"
            assert rows[1]["SIM slot"] == "2"
            # Features should include post_dial (note: code uses "post_dial" prefix)
            assert "post_dial:123" in rows[1]["Features"]
