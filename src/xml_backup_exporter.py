"""
Main entry point for SMS Backup & Restore Exporter.

This application is based upon the original code from @raleighlittles
(https://github.com/raleighlittles/SMS-backup-and-restore-extractor) and has been
greatly expanded and improved upon.

This module provides the command-line interface for exporting data from
SMS Backup & Restore backup archives. It supports four types of export:
- SMS/MMS media files (images, videos, audio, PDFs)
- SMS/MMS text messages (exported to CSV)
- Call logs (as CSV files with enhanced metadata)
- vCard/VCF contact media (photos, sounds, logos, keys)

Credits:
  Original idea and v1 code: Raleigh Littles - GitHub: @raleighlittles
  Updated and upgraded v2 app: Rich Lewis - GitHub: @RichLewis007
"""

import argparse
import os
from argparse import RawTextHelpFormatter

from . import call_log_generator
from . import contacts_vcard_extractor
from . import mms_media_extractor
from . import sms_text_extractor


def normalize_path(path: str) -> str:
    """
    Normalize a file path to handle various input formats.

    This function handles:
    - Home directory expansion (~)
    - Relative paths (./local/, ../parent/)
    - Path separator normalization
    - Conversion to absolute paths

    Args:
        path: Input path string (can be relative, absolute, or use ~)

    Returns:
        Normalized absolute path string

    Example:
        >>> normalize_path("~/backups")
        '/Users/username/backups'
        >>> normalize_path("./local/")
        '/current/working/directory/local'
    """
    # Expand ~ to home directory
    path = os.path.expanduser(path)
    # Normalize path separators and resolve .. and .
    path = os.path.normpath(path)
    # Convert to absolute path
    path = os.path.abspath(path)
    return path


def main() -> None:
    """
    Main entry point for the XML backup exporter command-line tool.

    Parses command-line arguments and routes to the appropriate export
    function based on the backup type specified by the user.

    Supported backup types:
    - 'sms-mms-media': Export MMS media attachments (images, videos, audio, PDFs) from SMS backup XML files
    - 'sms-mms-text': Export SMS text messages and MMS text bodies to CSV
    - 'calls': Generate a deduplicated call log CSV from call backup XML files
    - 'vcf': Export multimedia content from vCard/VCF contact files

    The function handles path normalization and supports both directory
    and single-file inputs (for single files, uses the parent directory).
    """
    parser = argparse.ArgumentParser(
        description="Exports media files, call logs, or vcf/vCard media from SMS Backup & Restore backup archives.",
        formatter_class=RawTextHelpFormatter,
        epilog="""Examples:
  To export all MMS media attachments from SMS backup XML files:
     xml-backup-exporter -t sms-mms-media -i input_dir -o output_dir

  To export only Video files:
     xml-backup-exporter -t sms-mms-media -i input_dir -o output_dir --no-images --no-audio --no-pdfs

  To export a de-duplicated call log:
     xml-backup-exporter -t calls -i input_dir -o output_dir

  To export VCF/vCard media:
     xml-backup-exporter -t vcf -i input_dir -o output_dir

  To export SMS text messages and MMS text bodies:
     xml-backup-exporter -t sms-mms-text -i input_dir -o output_dir
 
""",
    )

    parser.add_argument(
        "-i",
        "--input-dir",
        type=str,
        required=True,
        help="The directory where XML files (for calls or messages) are located, or a single file path",
    )
    parser.add_argument(
        "-t",
        "--backup-type",
        type=str,
        required=True,
        choices=["sms-mms-media", "sms-mms-text", "calls", "vcf"],
        help="The type of export: 'sms-mms-media' for MMS media files from SMS backup XML, 'sms-mms-text' for SMS/MMS text messages, 'calls' to create a call log, or 'vcf' to export media from a VCF/vCard file",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=str,
        required=True,
        help="The directory where exported files will be saved",
    )

    # Media type filters (for sms-mms-media export only)
    parser.add_argument(
        "--no-images",
        action="store_false",
        dest="process_images",
        help="Don't export image files from messages",
    )
    parser.add_argument(
        "--no-videos",
        action="store_false",
        dest="process_videos",
        help="Don't export video files from messages",
    )
    parser.add_argument(
        "--no-audio",
        action="store_false",
        dest="process_audio",
        help="Don't export audio files from messages",
    )
    parser.add_argument(
        "--no-pdfs",
        action="store_false",
        dest="process_pdfs",
        help="Don't export PDF files from messages",
    )

    args = parser.parse_args()

    # Normalize input and output paths to handle relative paths, ~ expansion, etc.
    input_path = normalize_path(args.input_dir)
    output_dir = normalize_path(args.output_dir)

    # Route to appropriate export function based on backup type
    # Pass the input_path directly - extraction functions will handle files vs directories
    if args.backup_type == "sms-mms-media":
        mms_media_extractor.reconstruct_mms_media(
            input_path,
            output_dir,
            args.process_images,
            args.process_videos,
            args.process_audio,
            args.process_pdfs,
        )
    elif args.backup_type == "sms-mms-text":
        sms_text_extractor.extract_sms_messages(input_path, output_dir)
    elif args.backup_type == "calls":
        call_log_generator.create_call_log(input_path, output_dir)
    elif args.backup_type == "vcf":
        contacts_vcard_extractor.parse_contacts_from_vcf_files(input_path, output_dir)


if __name__ == "__main__":
    main()
