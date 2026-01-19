"""
Call Log Generator for SMS Backup & Restore archives.

This module extracts call history from SMS Backup & Restore XML backup files
and generates a deduplicated CSV call log. The CSV includes call type,
duration, caller information, timestamps, and additional metadata.

Call types supported:
- Incoming, Outgoing, Missed, Voicemail, Rejected, Blocked, Answered Externally

Credits:
  Original idea and v1 code: Raleigh Littles - GitHub: @raleighlittles
  Updated and upgraded v2 app: Rich Lewis - GitHub: @RichLewis007
"""

import csv
import os
from typing import Optional

import lxml.etree


def get_human_readable_duration(duration_raw_s: str) -> str:
    """
    Convert seconds to a human-readable duration string.

    Formats duration with proper pluralization:
    - "0" -> "0 seconds"
    - "65" -> "1 minute, 5 seconds"
    - "3661" -> "1 hours, 1 minute, 1 second"

    Args:
        duration_raw_s: Duration in seconds as a string

    Returns:
        Formatted duration string with hours, minutes, and seconds

    Example:
        >>> get_human_readable_duration("192")
        "3 minutes, 12 seconds"
        >>> get_human_readable_duration("0")
        "0 seconds"
    """
    duration_s = int(duration_raw_s)

    # Convert seconds to hours, minutes, seconds
    # Reference: https://stackoverflow.com/questions/775049
    time_divisor = 60
    minutes, seconds = divmod(duration_s, time_divisor)
    hours, minutes = divmod(minutes, time_divisor)

    formatted_str = ""

    if hours > 0:
        hour_word = "hours" if hours != 1 else "hour"
        formatted_str += f"{hours} {hour_word}"

    if minutes > 0:
        if formatted_str:
            formatted_str += ", "
        minute_word = "minutes" if minutes != 1 else "minute"
        formatted_str += f"{minutes} {minute_word}"

    # Always show seconds if no hours/minutes, or if seconds > 0
    if seconds > 0 or (seconds == 0 and not formatted_str):
        if formatted_str:
            formatted_str += ", "
        second_word = "seconds" if seconds != 1 else "second"
        formatted_str += f"{seconds} {second_word}"

    return formatted_str


def create_call_log(calls_xml_dir: str, output_dir: Optional[str] = None) -> None:
    """
    Generate a deduplicated call log CSV from SMS Backup & Restore XML files.

    Uses lxml.etree.iterparse() for memory-efficient processing of large files.
    Processes either a single XML file or all XML files starting with "calls" in a directory.
    Extracts call information including additional metadata fields, and writes
    a CSV file with deduplicated entries. Calls are deduplicated by timestamp.

    Args:
        calls_xml_dir: Directory containing call backup XML files, or a single XML file path
        output_dir: Directory where call_log.csv will be written
                   (defaults to current directory if None)

    CSV Output Columns:
        - Call Date (timestamp): Unix timestamp in milliseconds
        - Call date: Human-readable date string
        - Call type: Incoming, Outgoing, Missed, etc.
        - Caller name: Contact name or "(Unknown)"
        - Caller #: Phone number
        - Call duration (s): Duration in seconds (or "N/A" for missed calls)
        - Call duration: Human-readable duration (or "N/A" for missed calls)
        - Read status: "1" if read, "0" if unread (when available)
        - SIM slot: Subscription ID (1, 2, etc. for dual SIM devices)
        - Features: Additional call features (video call, HD, etc. when available)
        - Call Id #: Sequential call identifier
    """
    all_calls_list = []

    # Map Android call type codes to human-readable names
    # Reference: https://developer.android.com/reference/android/provider/CallLog.Calls#TYPE
    call_type_map = {
        "1": "Incoming",
        "2": "Outgoing",
        "3": "Missed",
        "4": "Voicemail",
        "5": "Rejected",
        "6": "Blocked",
        "7": "AnsweredExternally",
    }

    # Track timestamps to prevent duplicate entries
    # Multiple calls cannot happen at the same exact timestamp
    call_timestamps = set()
    call_timestamp_key_name = "Call Date (timestamp)"
    num_calls = 0

    # Determine files to process - single file or all matching files in directory
    files_to_process = []
    if os.path.isfile(calls_xml_dir):
        # Single file specified - use only that file if it matches pattern
        if calls_xml_dir.endswith(".xml") and os.path.basename(calls_xml_dir).startswith("calls"):
            files_to_process = [calls_xml_dir]
        else:
            print(f"Error: Input file '{calls_xml_dir}' does not match expected pattern (should be 'calls*.xml').")
            return
    elif os.path.isdir(calls_xml_dir):
        # Directory specified - process all matching files
        for filename in os.listdir(calls_xml_dir):
            if not (filename.endswith(".xml") and filename.startswith("calls")):
                continue
            file_path = os.path.join(calls_xml_dir, filename)
            files_to_process.append(file_path)
    else:
        print(f"Error: Input path is neither a file nor a directory: {calls_xml_dir}")
        return

    if not files_to_process:
        print("No call backup XML files found to process.")
        print("Please ensure your input path contains files matching 'calls*.xml' pattern.")
        return

    # Process each call backup XML file
    for file_path in files_to_process:

        # Use iterparse for memory-efficient XML parsing
        context = lxml.etree.iterparse(
            file_path, events=("end",), huge_tree=True, recover=True
        )

        for event, elem in context:
            if elem.tag != "call":
                elem.clear()
                continue

            call_timestamp = elem.get("date", "")

            # Skip if this call timestamp was already processed (deduplication)
            if not call_timestamp or call_timestamp in call_timestamps:
                elem.clear()
                parent = elem.getparent()
                if parent is not None:
                    parent.remove(elem)
                continue

            call_entry_obj = {}
            call_entry_obj[call_timestamp_key_name] = call_timestamp
            call_entry_obj["Call date"] = elem.get("readable_date", "")

            # Map call type code to readable name
            call_type_code = elem.get("type", "")
            call_type = call_type_map.get(call_type_code, "Unknown")
            call_entry_obj["Call type"] = call_type

            call_entry_obj["Caller name"] = elem.get("contact_name", "(Unknown)")
            call_entry_obj["Caller #"] = elem.get("number", "")

            # Handle call duration
            # Missed calls don't have duration, but incoming/outgoing calls
            # may have duration of 0 if you hang up immediately
            call_duration_raw = elem.get("duration", "0")

            if call_type != "Missed":
                # Store both raw seconds and human-readable format
                call_entry_obj["Call duration (s)"] = call_duration_raw
                call_entry_obj["Call duration"] = get_human_readable_duration(
                    call_duration_raw
                )
            else:
                # Missed calls: set duration fields to "N/A"
                # All dictionaries must have the same keys for CSV writer
                call_entry_obj["Call duration (s)"] = "N/A"
                call_entry_obj["Call duration"] = "N/A"

            # Extract additional metadata fields
            # Read status: "1" = read, "0" = unread (if available)
            read_status = elem.get("read", "")
            call_entry_obj["Read status"] = read_status if read_status else "N/A"

            # SIM slot: subscription_id indicates which SIM card (for dual SIM)
            subscription_id = elem.get("subscription_id", "")
            call_entry_obj["SIM slot"] = subscription_id if subscription_id else "N/A"

            # Features: Additional call features (presentation, post_dial_digits, etc.)
            features = []
            presentation = elem.get("presentation", "")
            if presentation and presentation != "1":  # 1 is default/normal
                features.append(f"presentation:{presentation}")

            post_dial = elem.get("post_dial_digits", "")
            if post_dial:
                features.append(f"post_dial:{post_dial}")

            # Check for video call or other features (may be in other attributes)
            # The XML may contain additional feature indicators in future versions
            call_entry_obj["Features"] = ", ".join(features) if features else "N/A"

            call_entry_obj["Call Id #"] = num_calls

            # Mark this timestamp as processed
            call_timestamps.add(call_timestamp)
            all_calls_list.append(call_entry_obj)
            num_calls += 1

            # Free memory by clearing processed element
            elem.clear()
            parent = elem.getparent()
            if parent is not None:
                parent.remove(elem)

        # Done parsing this file
        del context

    # Write call log to CSV file
    if output_dir is None:
        output_dir = os.getcwd()
    else:
        try:
            os.makedirs(output_dir, exist_ok=True)
        except OSError as e:
            print(f"Error: Cannot create output directory '{output_dir}': {e}")
            print("Please check that:")
            print("  - The path is correct and writable")
            print("  - You have permission to create directories in the parent location")
            print("  - The path doesn't point to a read-only file system")
            return

    output_file = os.path.join(output_dir, "call_log.csv")

    if not all_calls_list:
        print("No calls found to export.")
        print("The input XML files do not contain any call records, or all calls were filtered out.")
        return

    # Write CSV with proper newline handling for cross-platform compatibility
    with open(output_file, "w", newline="") as csv_file_handle:
        csv_writer = csv.writer(csv_file_handle)

        # Write header row using keys from first call entry
        csv_writer.writerow(all_calls_list[0].keys())

        # Write call entries sorted by timestamp
        for call_entry in sorted(
            all_calls_list, key=lambda k: k[call_timestamp_key_name]
        ):
            csv_writer.writerow(list(call_entry.values()))

    print(f"Call log written to {output_file}")
