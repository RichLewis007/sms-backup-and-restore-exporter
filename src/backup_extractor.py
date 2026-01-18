import argparse
import os
from argparse import RawTextHelpFormatter

# locals
from . import call_log_generator
from . import mms_media_extractor
from . import contacts_vcard_extractor


def normalize_path(path: str) -> str:
    """
    Normalize a file path to handle various input formats:
    - Expands ~ to home directory
    - Resolves relative paths (./local/, ../parent/)
    - Normalizes path separators
    - Returns absolute path
    
    Args:
        path: Input path string
        
    Returns:
        Normalized absolute path string
    """
    # Expand ~ to home directory
    path = os.path.expanduser(path)
    # Normalize path separators and resolve .. and .
    path = os.path.normpath(path)
    # Convert to absolute path
    path = os.path.abspath(path)
    return path


def main():
    argparse_parser = argparse.ArgumentParser(
        description="Extracts media files, call logs, or vcf/vCard media, from an SMS Backup & Restore backup archive.",
        formatter_class=RawTextHelpFormatter,
        epilog='''Examples:
  To extract all MMS media attachments:
     backup-extractor -t sms -i input_dir -o output_dir

  To extract only Video files:
     backup-extractor -t sms -i input_dir -o output_dir --no-images --no-audio --no-pdfs

  To extract a de-duplicated call log:
     backup-extractor -t calls -i input_dir -o output_dir

  To extract VCF/vCard media:
     backup-extractor -t vcf -i input_dir -o output_dir
 
'''
    )

    argparse_parser.add_argument("-i", "--input-dir", type=str, required=True,
                                 help="The directory where XML files (for calls or messages) are located")
    argparse_parser.add_argument("-t", "--backup-type", type=str, required=True,
                                 help="The type of extraction. Either 'sms' for message media files, or 'calls' to create a call log, or 'vcf' to extract media from a VCF/vCard file")
    argparse_parser.add_argument("-o", "--output-dir", type=str, required=True,
                                 help="The directory where media files that are found, will be extracted to")

    argparse_parser.add_argument("--no-images", action='store_false',
                                 help="Don't extract image files from messages")
    argparse_parser.add_argument("--no-videos", action='store_false',
                                 help="Don't extract video files from messages")
    argparse_parser.add_argument("--no-audio", action='store_false',
                                 help="Don't extract audio files from messages")
    argparse_parser.add_argument("--no-pdfs", action='store_false',
                                 help="Don't extract PDF files from messages")

    argparse_args = argparse_parser.parse_args()

    # Normalize input and output paths to handle relative paths, ~ expansion, etc.
    input_path = normalize_path(argparse_args.input_dir)
    output_dir = normalize_path(argparse_args.output_dir)

    # If input is a file, extract its directory
    # This allows users to specify either a directory or a single file
    if os.path.isfile(input_path):
        input_dir = os.path.dirname(input_path)
        print(f"Note: Input is a file. Using parent directory: {input_dir}")
    elif os.path.isdir(input_path):
        input_dir = input_path
    else:
        # Path doesn't exist - let the extraction functions handle the error
        input_dir = input_path

    if argparse_args.backup_type == "sms":
        mms_media_extractor.reconstruct_mms_media(
            input_dir, output_dir,
            argparse_args.no_images, argparse_args.no_videos,
            argparse_args.no_audio, argparse_args.no_pdfs)

    elif argparse_args.backup_type == "calls":
        call_log_generator.create_call_log(input_dir, output_dir)

    elif argparse_args.backup_type == "vcf":
        contacts_vcard_extractor.parse_contacts_from_vcf_files(
            input_dir, output_dir)


if __name__ == "__main__":
    main()
