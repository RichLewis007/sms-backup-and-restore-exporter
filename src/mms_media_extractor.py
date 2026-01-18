"""
MMS Media Extractor for SMS Backup & Restore archives.

This module extracts media attachments (images, videos, audio, PDFs) from
SMS Backup & Restore XML backup files. Media files are Base64-encoded in
the backup format and are decoded back to their original binary format.

Supported media types:
- Images: GIF, JPG, PNG, HEIC, BMP, WebP, AVIF, TIFF
- Videos: MP4, AVI, MPEG, 3GPP, OGG, WebM, QuickTime, WMV, FLV
- Audio: WAV, AMR, MP4, M4A, OGG, WebM, MPEG, FLAC, 3GPP
- Documents: PDF

Credits:
  Original idea and v1 code: Raleigh Littles - GitHub: @raleighlittles
  Updated and upgraded v2 app: Rich Lewis - GitHub: @RichLewis007
"""
import base64
import datetime
import hashlib
import os
import random
import string
import sys
import time

import lxml.etree

# Filesystem constraints
MAX_FILENAME_LENGTH = 200
MAX_FULLPATH_LENGTH = 252  # Common filesystem limit (e.g., Windows)

# MIME type categories and supported subtypes
CONTENT_TYPES = {"image", "video", "audio", "application"}

IMAGE_SUBTYPES = {
    "avif", "bmp", "gif", "heic", "heif", "jpeg", "pjpeg", "png", "tiff",
    "webp", "x-icon", "*"
}
VIDEO_SUBTYPES = {
    "3gpp", "avi", "mp4", "mpeg", "ogg", "quicktime", "webm", "x-ms-wmv",
    "x-flv"
}
AUDIO_SUBTYPES = {
    "3gpp", "amr", "flac", "mp4", "mpeg", "ogg", "webm", "wav"
}
APPLICATION_SUBTYPES = {"pdf"}


def get_datetime_from_epoch_milliseconds(epoch_milliseconds: str) -> str:
    """
    Convert epoch timestamp (milliseconds) to formatted datetime string.
    
    Args:
        epoch_milliseconds: Unix timestamp in milliseconds as string
        
    Returns:
        Formatted datetime string in format 'YYYYMMDD-HHMMSS'
        
    Example:
        >>> get_datetime_from_epoch_milliseconds("1609459200000")
        '20210101-000000'
    """
    timestamp_seconds = int(epoch_milliseconds) / 1000
    dt = datetime.datetime.fromtimestamp(timestamp_seconds)
    return dt.strftime('%Y%m%d-%H%M%S')


def safe_filename(base_dir: str, filename: str, max_len: int = MAX_FILENAME_LENGTH) -> str:
    """
    Ensure filename fits within filesystem path length limits.
    
    If the full path would exceed MAX_FULLPATH_LENGTH, the filename is
    shortened by truncating the base name and appending an MD5 hash.
    
    Args:
        base_dir: Base directory path
        filename: Original filename
        max_len: Maximum filename length (default: MAX_FILENAME_LENGTH)
        
    Returns:
        Safe filename that fits within filesystem limits
    """
    full_path = os.path.join(base_dir, filename)
    if len(full_path) <= MAX_FULLPATH_LENGTH:
        return filename  # Already safe for most filesystems

    # Shorten filename by truncating base and adding hash
    base, ext = os.path.splitext(filename)
    hashed = hashlib.md5(base.encode('utf-8')).hexdigest()[:8]
    short_base = base[:50]
    short_filename = f"{short_base}_{hashed}{ext}"

    # Check if still too long, use hash-only as fallback
    full_path = os.path.join(base_dir, short_filename)
    if len(full_path) > MAX_FULLPATH_LENGTH:
        short_filename = hashed + ext

    return short_filename


def handle_duplicate_name(base_dir: str, safe_filename: str) -> str:
    """
    Generate a unique filename if a file with the same name already exists.
    
    If a file with the given name exists, appends a numeric suffix (-1, -2, etc.)
    until a unique filename is found.
    
    Args:
        base_dir: Directory where the file will be saved
        safe_filename: Base filename to check
        
    Returns:
        Unique file path (may be the original if no conflict exists)
        
    Example:
        If 'photo.jpg' exists, returns 'photo-1.jpg'
        If 'photo-1.jpg' also exists, returns 'photo-2.jpg'
    """
    safe_filename_base, safe_filename_ext = os.path.splitext(safe_filename)
    unique_output_file = os.path.join(base_dir, safe_filename)
    counter = 0
    
    while os.path.exists(unique_output_file):
        counter += 1
        unique_output_file = os.path.join(
            base_dir,
            f"{safe_filename_base}-{counter}{safe_filename_ext}"
        )

    return unique_output_file


def is_valid_output_directory(output_media_dir: str) -> bool:
    """
    Validate that the output directory is valid and empty.
    
    Creates the directory if it doesn't exist. Ensures it's a directory
    and that it's empty (to avoid overwriting existing files).
    
    Args:
        output_media_dir: Path to output directory
        
    Returns:
        True if directory is valid and ready, False otherwise
    """
    if not os.path.exists(output_media_dir):
        os.makedirs(output_media_dir, exist_ok=True)
        return True

    if not os.path.isdir(output_media_dir):
        print(f"Error: OUTPUT_DIR is not a directory: {output_media_dir}")
        return False

    # Check if directory is empty
    with os.scandir(output_media_dir) as entries:
        if any(entries):
            print(f"Error: OUTPUT_DIR is not empty: {output_media_dir}")
            return False

    return True


def reconstruct_mms_media(
    sms_xml_dir: str,
    output_media_dir: str,
    process_image: bool,
    process_video: bool,
    process_audio: bool,
    process_pdf: bool
) -> None:
    """
    Extract media attachments from SMS Backup & Restore XML files.
    
    Processes all XML files starting with 'sms' in the input directory,
    extracts Base64-encoded media attachments, and saves them as binary files.
    Duplicate files (by content hash) and empty files are removed after extraction.
    
    Args:
        sms_xml_dir: Directory containing SMS backup XML files
        output_media_dir: Directory where extracted media files will be saved
        process_image: Whether to extract image files
        process_video: Whether to extract video files
        process_audio: Whether to extract audio files
        process_pdf: Whether to extract PDF files
    """
    if not is_valid_output_directory(output_media_dir):
        return

    if not os.path.exists(sms_xml_dir):
        print(f"Error: Input directory does not exist: {sms_xml_dir}")
        print("Please provide a valid directory path containing SMS backup XML files.")
        return

    if not os.path.isdir(sms_xml_dir):
        print(f"Error: Input path is not a directory: {sms_xml_dir}")
        return

    start_time = time.time()
    orig_files_count = 0

    # Build status message showing which media types are being processed
    media_types = []
    if process_image:
        media_types.append('images')
    if process_video:
        media_types.append('videos')
    if process_audio:
        media_types.append('audio')
    if process_pdf:
        media_types.append('PDFs')
    
    content_msg = f"Processing messages ({', '.join(media_types)})..."
    print(content_msg, end="", flush=True)

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
            recover=True  # Continue parsing even if XML is malformed
        )

        for event, elem in context:
            if elem.tag != 'part':
                elem.clear()
                continue

            # Get MIME content type (e.g., "image/jpeg")
            ct_value = elem.get('ct', '').lower()
            ct_type, _, ct_subtype = ct_value.partition('/')

            # Skip if not a supported content type
            if ct_type not in CONTENT_TYPES:
                elem.clear()
                continue

            # Check if this media type should be processed
            should_process = False
            if ct_type == 'image' and process_image and ct_subtype in IMAGE_SUBTYPES:
                should_process = True
            elif ct_type == 'video' and process_video and ct_subtype in VIDEO_SUBTYPES:
                should_process = True
            elif ct_type == 'audio' and process_audio and ct_subtype in AUDIO_SUBTYPES:
                should_process = True
            elif ct_type == 'application' and process_pdf and ct_subtype in APPLICATION_SUBTYPES:
                should_process = True

            if not should_process:
                elem.clear()
                continue

            # Get parent MMS node for metadata
            parent_parts = elem.getparent()  # <parts>
            if parent_parts is None:
                elem.clear()
                continue

            mms_node = parent_parts.getparent()  # <mms>
            if mms_node is None:
                elem.clear()
                continue

            # Extract metadata
            media_date_field = mms_node.get('date', '')
            media_sender_field = mms_node.get('address', '')
            data = elem.get('data', '')  # Base64-encoded media data
            content_location = elem.get('cl', '')  # Original filename

            # Clean phone number (remove non-digits)
            clean_phone = "".join(c for c in media_sender_field if c.isdigit())

            # Generate filename if not provided
            if not content_location or content_location == 'null':
                content_location = (
                    "".join(random.sample(string.ascii_letters, 10))
                    + f".{ct_subtype}"
                )

            # Build base filename: timestamp_phonenumber_filename
            base_name = (
                get_datetime_from_epoch_milliseconds(media_date_field)
                + f"_{clean_phone}_{content_location}"
            )

            # Add extension if missing
            if '.' not in content_location:
                base_name += f".{ct_subtype}"

            # Ensure filename fits filesystem limits
            target_filename = safe_filename(output_media_dir, base_name)

            # Handle duplicate filenames (multiple attachments with same name)
            output_file_path = handle_duplicate_name(output_media_dir, target_filename)

            # Decode and write media file
            try:
                with open(output_file_path, 'wb') as out_f:
                    decoded_data = base64.b64decode(data)
                    out_f.write(decoded_data)
                    orig_files_count += 1
            except Exception as e:
                print(f"\nERROR writing file {output_file_path}: {e}")

            # Free memory by clearing processed element
            elem.clear()
            parent = elem.getparent()
            if parent is not None:
                parent.remove(elem)

        # Done parsing this file
        del context

    print("complete.", flush=True)
    
    # Remove duplicates and empty files after extraction
    num_dup_files = remove_duplicate_files(output_media_dir)
    end_time = time.time()

    print(
        f"{orig_files_count} media files found in messages, "
        f"{num_dup_files} duplicates (or empty files) removed. "
        f"Time elapsed: {round(end_time - start_time, 2)} seconds"
    )


def remove_duplicate_files(output_media_dir: str) -> int:
    """
    Remove duplicate files and empty files from the output directory.
    
    Files are considered duplicates if they have the same MD5 hash.
    Empty files (0 bytes) are also removed.
    
    Args:
        output_media_dir: Directory containing extracted files
        
    Returns:
        Number of duplicate/empty files removed
        
    Raises:
        SystemExit: If a subdirectory is found in the output directory
    """
    duplicate_files_count = 0
    unique_hashes = set()
    
    print("Removing duplicates...", end="", flush=True)
    
    for filename in os.listdir(output_media_dir):
        file_path = os.path.join(output_media_dir, filename)
        
        if not os.path.isfile(file_path):
            print(f"\nERROR: Subdirectory found in output directory: {filename}")
            sys.exit(1)
        
        # Calculate file hash
        with open(file_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()

        # Remove if duplicate or empty
        if file_hash in unique_hashes or os.path.getsize(file_path) == 0:
            os.remove(file_path)
            duplicate_files_count += 1
        else:
            unique_hashes.add(file_hash)

    print("complete.", flush=True)
    return duplicate_files_count
