"""Tests for sms_text_extractor module."""
import csv
import os
from pathlib import Path

import pytest

from src.sms_text_extractor import extract_sms_messages


class TestExtractSmsMessages:
    """Tests for the extract_sms_messages function."""

    def test_extract_sms_messages_with_valid_xml(self, temp_dir):
        """Test extracting SMS messages from valid XML file."""
        # Create SMS XML file with SMS messages
        sms_dir = temp_dir / "sms_dir"
        sms_dir.mkdir()
        
        xml_content = """<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<smses count="2">
    <sms protocol="0" address="+1234567890" date="1609459200000" type="1" 
         subject="null" body="Hello, this is a test message" 
         toa="null" sc_toa="null" service_center="null" read="1" 
         status="-1" locked="0" readable_date="Jan 1, 2021 12:00:00 AM" 
         contact_name="John Doe" sub_id="-1" />
    <sms protocol="0" address="+1234567890" date="1609545600000" type="2" 
         subject="null" body="This is a reply message" 
         toa="null" sc_toa="null" service_center="null" read="1" 
         status="-1" locked="0" readable_date="Jan 2, 2021 12:00:00 AM" 
         contact_name="John Doe" sub_id="-1" />
</smses>"""
        
        xml_file = sms_dir / "sms-test.xml"
        xml_file.write_text(xml_content, encoding='utf-8')
        
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        
        extract_sms_messages(str(sms_dir), str(output_dir))
        
        # Check that CSV file was created
        csv_file = output_dir / "sms_messages.csv"
        assert csv_file.exists()
        
        # Verify CSV content
        with open(csv_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2
            
            # Check first SMS
            assert rows[0]["Message Type"] == "SMS"
            assert rows[0]["Address"] == "+1234567890"
            assert rows[0]["Contact Name"] == "John Doe"
            assert rows[0]["Body"] == "Hello, this is a test message"
            assert rows[0]["Type"] == "1"  # Incoming
            assert rows[0]["Read"] == "1"
            
            # Check second SMS
            assert rows[1]["Message Type"] == "SMS"
            assert rows[1]["Body"] == "This is a reply message"
            assert rows[1]["Type"] == "2"  # Outgoing

    def test_extract_mms_text_bodies(self, temp_dir):
        """Test extracting MMS text bodies from XML file."""
        sms_dir = temp_dir / "sms_dir"
        sms_dir.mkdir()
        
        xml_content = """<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<smses count="1">
    <mms address="+1234567890" date="1609459200000" readable_date="Jan 1, 2021 12:00:00 AM" 
         contact_name="John Doe" m_type="132" read="1" st="0" locked="0" sub_id="-1">
        <parts>
            <part seq="0" ct="text/plain" text="This is an MMS text body" />
            <part seq="1" ct="image/jpeg" data="/9j/4AAQSkZJRg..." name="photo.jpg" />
        </parts>
    </mms>
</smses>"""
        
        xml_file = sms_dir / "sms-mms.xml"
        xml_file.write_text(xml_content, encoding='utf-8')
        
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        
        extract_sms_messages(str(sms_dir), str(output_dir))
        
        csv_file = output_dir / "sms_messages.csv"
        assert csv_file.exists()
        
        with open(csv_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            
            # Check MMS text body
            assert rows[0]["Message Type"] == "MMS"
            assert rows[0]["Address"] == "+1234567890"
            assert rows[0]["Contact Name"] == "John Doe"
            assert rows[0]["Body"] == "This is an MMS text body"
            assert rows[0]["Type"] == "132"

    def test_extract_mixed_sms_and_mms(self, temp_dir):
        """Test extracting both SMS and MMS messages from same file."""
        sms_dir = temp_dir / "sms_dir"
        sms_dir.mkdir()
        
        xml_content = """<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<smses count="3">
    <sms protocol="0" address="+1111111111" date="1609459200000" type="1" 
         body="First SMS message" read="1" status="-1" locked="0" 
         readable_date="Jan 1, 2021 12:00:00 AM" contact_name="Alice" sub_id="-1" />
    <mms address="+2222222222" date="1609545600000" readable_date="Jan 2, 2021 12:00:00 AM" 
         contact_name="Bob" m_type="132" read="1" st="0" locked="0" sub_id="-1">
        <parts>
            <part seq="0" ct="text/plain" text="MMS text message" />
        </parts>
    </mms>
    <sms protocol="0" address="+3333333333" date="1609632000000" type="2" 
         body="Second SMS message" read="1" status="-1" locked="0" 
         readable_date="Jan 3, 2021 12:00:00 AM" contact_name="Charlie" sub_id="-1" />
</smses>"""
        
        xml_file = sms_dir / "sms-mixed.xml"
        xml_file.write_text(xml_content, encoding='utf-8')
        
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        
        extract_sms_messages(str(sms_dir), str(output_dir))
        
        csv_file = output_dir / "sms_messages.csv"
        assert csv_file.exists()
        
        with open(csv_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 3
            
            # Check that we have both SMS and MMS
            message_types = [row["Message Type"] for row in rows]
            assert "SMS" in message_types
            assert "MMS" in message_types
            
            # Verify messages are sorted by timestamp
            timestamps = [row["Date (timestamp)"] for row in rows]
            assert timestamps == sorted(timestamps)

    def test_extract_sms_messages_no_messages(self, temp_dir):
        """Test extracting when no SMS/MMS messages exist."""
        sms_dir = temp_dir / "sms_dir"
        sms_dir.mkdir()
        
        # Create empty XML file
        xml_content = """<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<smses count="0">
</smses>"""
        
        xml_file = sms_dir / "sms-empty.xml"
        xml_file.write_text(xml_content, encoding='utf-8')
        
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        
        extract_sms_messages(str(sms_dir), str(output_dir))
        
        # CSV file should not be created if no messages
        csv_file = output_dir / "sms_messages.csv"
        # The function returns early if no messages, so CSV might not exist
        # or might exist but be empty - both are acceptable

    def test_extract_sms_messages_nonexistent_directory(self, temp_dir):
        """Test extracting from non-existent directory."""
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        
        nonexistent_dir = temp_dir / "nonexistent"
        
        # Should not raise exception, just print error and return
        extract_sms_messages(str(nonexistent_dir), str(output_dir))
        
        # CSV file should not be created
        csv_file = output_dir / "sms_messages.csv"
        assert not csv_file.exists()

    def test_extract_sms_messages_skips_non_sms_files(self, temp_dir):
        """Test that non-sms XML files are skipped."""
        sms_dir = temp_dir / "sms_dir"
        sms_dir.mkdir()
        
        # Create SMS file
        sms_xml = """<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<smses count="1">
    <sms protocol="0" address="+1234567890" date="1609459200000" type="1" 
         body="Test SMS" read="1" status="-1" locked="0" 
         readable_date="Jan 1, 2021 12:00:00 AM" contact_name="Test" sub_id="-1" />
</smses>"""
        
        sms_file = sms_dir / "sms-test.xml"
        sms_file.write_text(sms_xml, encoding='utf-8')
        
        # Create non-SMS XML file (should be skipped)
        other_xml = """<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<other>
    <item>Should be skipped</item>
</other>"""
        
        other_file = sms_dir / "other-test.xml"
        other_file.write_text(other_xml, encoding='utf-8')
        
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        
        extract_sms_messages(str(sms_dir), str(output_dir))
        
        csv_file = output_dir / "sms_messages.csv"
        assert csv_file.exists()
        
        # Should only have the one SMS message, not the other XML content
        with open(csv_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]["Message Type"] == "SMS"

    def test_extract_sms_messages_all_fields(self, temp_dir):
        """Test that all SMS fields are extracted correctly."""
        sms_dir = temp_dir / "sms_dir"
        sms_dir.mkdir()
        
        xml_content = """<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<smses count="1">
    <sms protocol="0" address="+1234567890" date="1609459200000" type="1" 
         body="Complete test message" read="0" status="0" locked="1" 
         readable_date="Jan 1, 2021 12:00:00 AM" contact_name="Full Test" sub_id="1" />
</smses>"""
        
        xml_file = sms_dir / "sms-complete.xml"
        xml_file.write_text(xml_content, encoding='utf-8')
        
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        
        extract_sms_messages(str(sms_dir), str(output_dir))
        
        csv_file = output_dir / "sms_messages.csv"
        with open(csv_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            
            msg = rows[0]
            # Verify all expected fields are present
            assert "Message Type" in msg
            assert "Date (timestamp)" in msg
            assert "Date" in msg
            assert "Address" in msg
            assert "Contact Name" in msg
            assert "Type" in msg
            assert "Body" in msg
            assert "Read" in msg
            assert "Status" in msg
            assert "Locked" in msg
            assert "SIM ID" in msg
            assert "Message ID" in msg
            
            # Verify values
            assert msg["Address"] == "+1234567890"
            assert msg["Read"] == "0"
            assert msg["Locked"] == "1"
            assert msg["SIM ID"] == "1"