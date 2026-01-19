"""
vCard/VCF contact parser and extractor.

This module handles parsing of vCard files (VCF format) and extracting
multimedia content from contacts (photos, sounds, logos, keys).

Credits:
  Original idea and v1 code: Raleigh Littles - GitHub: @raleighlittles
  Updated and upgraded v2 app: Rich Lewis - GitHub: @RichLewis007
"""

import os
import random
import string
from typing import Any, Callable, Dict, List, Tuple, Union

from . import vcf_field_parser
from . import vcard_multimedia_helper


# vCard 2.1 and 3.0 require "N" field, v4.0 requires "FN" field.
# However, some vCard files may have neither (non-standard).
CONTACT_ID_KEY = "N"
CONTACT_SECONDARY_ID_KEY = "FN"

# Constants for vCard parsing
BEGIN_VCARD = "BEGIN:VCARD"
END_VCARD = "END:VCARD"
RANDOM_FILENAME_LENGTH = 10


# Field parser dispatch table - maps field prefixes to their parser functions
FIELD_PARSERS: Dict[str, Callable[[str], Union[dict, tuple, str]]] = {
    "ADR": vcf_field_parser.parse_address_tag,
    "CATEGORIES": vcf_field_parser.parse_categories_tag,
    "CLIENTPIDMAP": vcf_field_parser.parse_clientpidmap_tag,
    "EMAIL": vcf_field_parser.parse_email_tag,
    "GEO": vcf_field_parser.parse_geo_tag,
    "IMPP": vcf_field_parser.parse_instant_messenger_handle_tag,
    "LABEL": vcf_field_parser.parse_mailing_label_tag,
    "MEMBER": vcf_field_parser.parse_member_tag,
    "N": vcf_field_parser.parse_name_tag,
    "ORG": vcf_field_parser.parse_organization_tag,
    "RELATED": vcf_field_parser.parse_related_tag,
    "TEL": vcf_field_parser.parse_telephone_tag,
    "UID": vcf_field_parser.parse_uuid_tag,
}


def parse_vcard_line(file_line: str) -> Dict[str, Any]:
    """
    Parse a single vCard line and extract the property and value.

    Args:
        file_line: A single line from a VCF file

    Returns:
        Dictionary containing the parsed field data
    """
    contact: Dict[str, Any] = {}

    # Check for simple keys first (these don't require special parsing)
    matching_key = next(
        (key for key in vcf_field_parser.SIMPLE_KEYS if file_line.startswith(key)), None
    )
    if matching_key:
        contact[matching_key] = vcf_field_parser.parse_simple_tag(file_line)
        return contact

    # Check dispatch table for standard field parsers
    for field_prefix, parser_func in FIELD_PARSERS.items():
        if file_line.startswith(field_prefix):
            contact[field_prefix] = parser_func(file_line)
            return contact

    # Handle multimedia fields (PHOTO, SOUND, LOGO, KEY)
    # These may span multiple lines
    multimedia_keys = vcard_multimedia_helper.get_advanced_key_names()
    for key in multimedia_keys:
        if file_line.startswith(key):
            # Remove tag name prefix before parsing (multimedia parser expects it removed)
            tag_content = file_line[len(key) :]
            contact[key] = vcf_field_parser.parse_multimedia_tag(tag_content)
            return contact

    # Unknown field - return empty dict (some fields may be ignored)
    return contact


def _generate_random_filename() -> str:
    """Generate a random filename for contacts without names."""
    return "".join(random.sample(string.ascii_letters, RANDOM_FILENAME_LENGTH))


def _get_contact_identifier(contact: Dict) -> str:
    """
    Extract a unique identifier for a contact (name-based) for use in filenames.

    Args:
        contact: Dictionary containing contact data

    Returns:
        String identifier (name or random string if no name available)
    """
    if CONTACT_ID_KEY in contact:
        return vcf_field_parser.return_name_tag_formatted(contact[CONTACT_ID_KEY])

    if CONTACT_SECONDARY_ID_KEY in contact:
        return contact[CONTACT_SECONDARY_ID_KEY]

    # Fallback: generate random identifier if no name field exists
    # This violates vCard spec, but some files may have contacts without names
    return _generate_random_filename()


def generate_multimedia_of_contact(contact: Dict, output_dir: str) -> None:
    """
    Extract and save multimedia content from a contact.

    Args:
        contact: Dictionary containing contact data
        output_dir: Directory where multimedia files should be saved
    """
    base_filename = _get_contact_identifier(contact)
    output_path = os.path.join(output_dir, base_filename)
    vcard_multimedia_helper.extract_key_multimedia(contact, output_path)


def _parse_multiline_multimedia(
    vcf_file_lines: List[str], start_line: int
) -> Tuple[str, int]:
    """
    Parse a multimedia field that may span multiple lines.

    Args:
        vcf_file_lines: List of all lines in the VCF file
        start_line: Index of the first line of the multimedia field

    Returns:
        Tuple of (concatenated multimedia tag line, next line index)
    """
    multimedia_tag_line = vcf_file_lines[start_line].strip()
    next_line_num = start_line + 1

    # Continue reading lines until we find a colon (end of multiline field)
    while next_line_num < len(vcf_file_lines):
        next_line = vcf_file_lines[next_line_num]

        # Empty line means done parsing
        if not next_line.strip():
            break

        # If line contains colon, we've reached the end
        if ":" in next_line:
            break

        multimedia_tag_line += next_line.strip()
        next_line_num += 1

    return multimedia_tag_line.strip(), next_line_num


def _parse_vcf_file(file_path: str, output_media_dir: str) -> List[Dict]:
    """
    Parse a single VCF file and extract contacts.

    Args:
        file_path: Path to the VCF file
        output_media_dir: Directory where multimedia should be extracted

    Returns:
        List of contact dictionaries
    """
    all_contacts = []

    with open(file_path, "r", encoding="utf-8") as vcf_file:
        vcf_file_lines = vcf_file.readlines()

    curr_contact: Dict[str, Any] = {}
    currently_in_contact = False
    has_multimedia = False
    line_num = 0

    while line_num < len(vcf_file_lines):
        line_content = vcf_file_lines[line_num]
        stripped_line = line_content.strip()

        if stripped_line == BEGIN_VCARD:
            if currently_in_contact:
                raise ValueError(
                    f"Missing END:VCARD tag before new BEGIN:VCARD at line {line_num + 1}"
                )
            currently_in_contact = True
            curr_contact = {}
            has_multimedia = False

        elif stripped_line == END_VCARD:
            if not currently_in_contact:
                raise ValueError(
                    f"Found END:VCARD without matching BEGIN:VCARD at line {line_num + 1}"
                )

            currently_in_contact = False
            all_contacts.append(curr_contact)

            # Extract multimedia if present
            if has_multimedia:
                generate_multimedia_of_contact(curr_contact, output_media_dir)

            # Reset for next contact
            curr_contact = {}
            has_multimedia = False

        elif currently_in_contact:
            # Check if this is a multiline multimedia field
            multimedia_keys = vcard_multimedia_helper.get_advanced_key_names()
            if any(line_content.startswith(key) for key in multimedia_keys):
                has_multimedia = True
                multimedia_tag_line, next_line_num = _parse_multiline_multimedia(
                    vcf_file_lines, line_num
                )

                new_contact_info = parse_vcard_line(multimedia_tag_line)
                if new_contact_info:
                    curr_contact.update(new_contact_info)

                line_num = next_line_num
                continue

            # Parse regular single-line field
            new_contact_info = parse_vcard_line(stripped_line)
            if new_contact_info:
                curr_contact.update(new_contact_info)

        line_num += 1

    if currently_in_contact:
        raise ValueError("File ended without closing END:VCARD tag")

    return all_contacts


def parse_contacts_from_vcf_files(vcf_files_dir: str, output_media_dir: str) -> None:
    """
    Parse VCF files and extract contact multimedia.

    Processes either a single VCF file or all VCF files in a directory.

    Args:
        vcf_files_dir: Directory containing VCF files, or a single VCF file path
        output_media_dir: Directory where extracted multimedia files will be saved
    """
    if not os.path.exists(vcf_files_dir):
        print(f"Error: Input path does not exist: {vcf_files_dir}")
        print("Please provide a valid directory or file path containing VCF/vCard files.")
        return

    # Ensure output directory exists
    try:
        os.makedirs(output_media_dir, exist_ok=True)
    except OSError as e:
        print(f"Error: Cannot create output directory '{output_media_dir}': {e}")
        print("Please check that:")
        print("  - The path is correct and writable")
        print("  - You have permission to create directories in the parent location")
        print("  - The path doesn't point to a read-only file system")
        return

    all_contacts = []

    # Determine files to process - single file or all matching files in directory
    files_to_process = []
    if os.path.isfile(vcf_files_dir):
        # Single file specified - use only that file if it matches pattern
        if vcf_files_dir.endswith(".vcf"):
            files_to_process = [vcf_files_dir]
        else:
            print(f"Error: Input file '{vcf_files_dir}' does not match expected pattern (should end with '.vcf').")
            return
    elif os.path.isdir(vcf_files_dir):
        # Directory specified - process all matching files
        for filename in os.listdir(vcf_files_dir):
            if not filename.endswith(".vcf"):
                continue
            file_path = os.path.join(vcf_files_dir, filename)
            files_to_process.append(file_path)
    else:
        print(f"Error: Input path is neither a file nor a directory: {vcf_files_dir}")
        return

    for file_path in files_to_process:

        try:
            contacts = _parse_vcf_file(file_path, output_media_dir)
            all_contacts.extend(contacts)
            print(f"Parsed {os.path.basename(file_path)}: {len(contacts)} contact(s) found")
        except ValueError as e:
            print(f"Error parsing {filename}: {e}")
            continue
        except Exception as e:
            print(f"Unexpected error parsing {filename}: {e}")
            continue

    if not all_contacts:
        print("No contacts found in VCF files.")
        print("Please check that:")
        print("  - The VCF files contain valid vCard data")
        print("  - The files are not empty or corrupted")
        return

    print(f"Total contacts parsed: {len(all_contacts)}")
