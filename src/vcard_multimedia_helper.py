"""
vCard Multimedia Helper Functions.

This module provides utilities for extracting and decoding multimedia content
from vCard files. It handles Base64-encoded data and URL-based media for
PHOTO, SOUND, LOGO, and KEY fields.
"""

import base64
from typing import List

import requests

# Multimedia field key names in parsed contact dictionaries
MULTIMEDIA_TAG_TAG_TYPE_KEY = "tag_type"
MULTIMEDIA_TAG_TAG_DATA_KEY = "tag_data"
MULTIMEDIA_TAG_TAG_URL_KEY = "tag_url"
MULTIMEDIA_TAG_TAG_MIME_TYPE_KEY = "tag_mime_type"


def get_advanced_key_names() -> List[str]:
    """
    Get list of vCard field names that may contain multiline multimedia content.

    These fields (PHOTO, SOUND, LOGO, KEY) can span multiple lines in VCF files
    and require special handling during parsing.

    Returns:
        List of field names: ["KEY", "LOGO", "PHOTO", "SOUND"]
    """
    return ["KEY", "LOGO", "PHOTO", "SOUND"]


def get_multimedia_tag_list() -> List[str]:
    """
    Get list of multimedia tag attribute keys.

    Returns:
        List of keys used in multimedia tag dictionaries:
        ["tag_type", "tag_data", "tag_url", "tag_mime_type"]
    """
    return [
        MULTIMEDIA_TAG_TAG_TYPE_KEY,
        MULTIMEDIA_TAG_TAG_DATA_KEY,
        MULTIMEDIA_TAG_TAG_URL_KEY,
        MULTIMEDIA_TAG_TAG_MIME_TYPE_KEY,
    ]


def extract_key_multimedia(contact: dict, base_filename: str) -> None:
    """
    Extract and save multimedia content from a contact.

    Searches for PHOTO, SOUND, LOGO, and KEY fields in the contact dictionary
    and extracts them to files. Handles both Base64-encoded data and URLs.

    Args:
        contact: Dictionary containing parsed contact data
        base_filename: Base filename (without extension) for the output file

    Raises:
        Exception: If file extension cannot be determined from multimedia data
        Exception: If URL download fails
    """
    for key_name in get_advanced_key_names():
        if key_name not in contact:
            continue

        # Determine file extension from tag_type or MIME type
        file_extension = ""
        if MULTIMEDIA_TAG_TAG_TYPE_KEY in contact[key_name]:
            file_extension = contact[key_name][MULTIMEDIA_TAG_TAG_TYPE_KEY]
        elif MULTIMEDIA_TAG_TAG_MIME_TYPE_KEY in contact[key_name]:
            # Extract extension from MIME type (e.g., "image/jpeg" -> "jpeg")
            mime_type = contact[key_name][MULTIMEDIA_TAG_TAG_MIME_TYPE_KEY]
            file_extension = mime_type.split("/")[1]
        else:
            raise ValueError(
                f"Couldn't determine extension for {key_name}. "
                f"Contents didn't match expected format."
            )

        # Remove dots from base filename (to avoid extension confusion)
        clean_base = base_filename.replace(".", "")
        filename = f"{clean_base}.{file_extension}"

        # Check if media is URL-based or Base64-encoded
        is_url = MULTIMEDIA_TAG_TAG_URL_KEY in contact[key_name]

        if is_url:
            data_or_url = contact[key_name][MULTIMEDIA_TAG_TAG_URL_KEY]
        else:
            data_or_url = contact[key_name][MULTIMEDIA_TAG_TAG_DATA_KEY]

        decode_multimedia_data_field(data_or_url, is_url, filename)


def decode_multimedia_data_field(
    data_or_url: str, is_url: bool, output_filename: str
) -> None:
    """
    Decode and save multimedia data from Base64 or URL.

    If is_url is True, downloads the media from the URL.
    Otherwise, decodes Base64-encoded data.

    Args:
        data_or_url: Either a URL string or Base64-encoded data string
        is_url: True if data_or_url is a URL, False if it's Base64 data
        output_filename: Path where the decoded file should be saved

    Raises:
        Exception: If URL download fails or Base64 decoding fails
    """
    with open(output_filename, "wb") as file_handle:
        if is_url:
            # Download from URL
            response = requests.get(data_or_url, stream=True)

            if not response.ok:
                raise RuntimeError(
                    f"Couldn't download media from URL '{data_or_url}'. "
                    f"HTTP status: {response.status_code}"
                )

            # Write file in chunks to handle large files
            for block in response.iter_content(1024):
                if not block:
                    break
                file_handle.write(block)
        else:
            # Decode Base64 data
            decoded_data = base64.b64decode(data_or_url)
            file_handle.write(decoded_data)
