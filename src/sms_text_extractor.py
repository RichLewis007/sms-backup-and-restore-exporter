"""
SMS Text Message Extractor for SMS Backup & Restore archives.

This module extracts SMS text messages from SMS Backup & Restore XML backup files
and exports them to a CSV file. It also extracts MMS text bodies as part of
comprehensive message extraction.

Credits:
  Original idea and v1 code: Raleigh Littles - GitHub: @raleighlittles
  Updated and upgraded v2 app: Rich Lewis - GitHub: @RichLewis007
"""
import csv
import os

import lxml.etree


def extract_sms_messages(sms_xml_dir: str, output_dir: str) -> None:
    """
    Extract SMS text messages and MMS text bodies from SMS Backup & Restore XML files.
    
    Processes all XML files starting with 'sms' in the input directory,
    extracts SMS text messages and MMS text bodies, and writes them to a CSV file.
    
    Args:
        sms_xml_dir: Directory containing SMS backup XML files
        output_dir: Directory where sms_messages.csv will be written
    """
    all_messages = []

    if not os.path.exists(sms_xml_dir):
        print(f"Error: Input directory does not exist: {sms_xml_dir}")
        print("Please provide a valid directory path containing SMS backup XML files.")
        return

    if not os.path.isdir(sms_xml_dir):
        print(f"Error: Input path is not a directory: {sms_xml_dir}")
        return

    os.makedirs(output_dir, exist_ok=True)
    num_sms = 0
    num_mms_text = 0

    # Process each SMS backup XML file
    for filename in os.listdir(sms_xml_dir):
        if not (filename.endswith(".xml") and filename.startswith("sms")):
            continue

        file_path = os.path.join(sms_xml_dir, filename)

        # Use iterparse for memory-efficient XML parsing
        context = lxml.etree.iterparse(
            file_path,
            events=('end',),
            huge_tree=True,
            recover=True
        )

        for event, elem in context:
            message_entry = {}

            # Process SMS messages
            if elem.tag == 'sms':
                message_entry["Message Type"] = "SMS"
                message_entry["Date (timestamp)"] = elem.get("date", "")
                message_entry["Date"] = elem.get("readable_date", "")
                message_entry["Address"] = elem.get("address", "")
                message_entry["Contact Name"] = elem.get("contact_name", "")
                message_entry["Type"] = elem.get("type", "")  # 1=incoming, 2=outgoing
                message_entry["Body"] = elem.get("body", "")
                message_entry["Read"] = elem.get("read", "")
                message_entry["Status"] = elem.get("status", "")
                message_entry["Locked"] = elem.get("locked", "")
                message_entry["SIM ID"] = elem.get("sub_id", "")
                message_entry["Message ID"] = num_sms
                
                if message_entry["Body"]:  # Only add if body exists
                    all_messages.append(message_entry)
                    num_sms += 1

            # Process MMS text bodies
            elif elem.tag == 'part':
                # Check if this is a text/plain part
                content_type = elem.get('ct', '').lower()
                if content_type == 'text/plain':
                    # Get parent MMS node for metadata
                    parent_parts = elem.getparent()  # <parts>
                    if parent_parts is not None:
                        mms_node = parent_parts.getparent()  # <mms>
                        if mms_node is not None:
                            text_body = elem.get('text', '')
                            if text_body:  # Only add if text body exists
                                mms_message_entry = {}
                                mms_message_entry["Message Type"] = "MMS"
                                mms_message_entry["Date (timestamp)"] = mms_node.get("date", "")
                                mms_message_entry["Date"] = mms_node.get("readable_date", "")
                                mms_message_entry["Address"] = mms_node.get("address", "")
                                mms_message_entry["Contact Name"] = mms_node.get("contact_name", "")
                                mms_message_entry["Type"] = mms_node.get("m_type", "")
                                mms_message_entry["Body"] = text_body
                                mms_message_entry["Read"] = mms_node.get("read", "")
                                mms_message_entry["Status"] = mms_node.get("st", "")
                                mms_message_entry["Locked"] = mms_node.get("locked", "")
                                mms_message_entry["SIM ID"] = mms_node.get("sub_id", "")
                                mms_message_entry["Message ID"] = num_mms_text
                                
                                all_messages.append(mms_message_entry)
                                num_mms_text += 1

            # Free memory by clearing processed element
            elem.clear()
            parent = elem.getparent()
            if parent is not None:
                parent.remove(elem)

        # Done parsing this file
        del context

    # Write messages to CSV file
    output_file = os.path.join(output_dir, "sms_messages.csv")

    if not all_messages:
        print("No SMS messages or MMS text bodies found to export.")
        return

    # Write CSV with proper newline handling for cross-platform compatibility
    with open(output_file, "w", newline="", encoding='utf-8') as csv_file_handle:
        csv_writer = csv.writer(csv_file_handle)

        # Write header row using keys from first message entry
        csv_writer.writerow(all_messages[0].keys())

        # Write message entries sorted by timestamp
        for message in sorted(
            all_messages,
            key=lambda k: k.get("Date (timestamp)", "")
        ):
            # Ensure all values are strings and handle None values
            row = [str(v) if v is not None else "" for v in message.values()]
            csv_writer.writerow(row)

    print(f"SMS messages exported to {output_file}")
    print(f"  - {num_sms} SMS messages")
    print(f"  - {num_mms_text} MMS text bodies")
