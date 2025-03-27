"""Main entry point for GoPro Transfer application."""

import sys
from pathlib import Path

import fire
from loguru import logger

from gopro_transfer.config import get_settings
from gopro_transfer.logger import setup_logging
from gopro_transfer.telemetry import extract_telemetry, save_telemetry
from gopro_transfer.transfer.operations import (
    get_gopro_mount_path,
    get_media_files,
    list_media_info,
    transfer_files,
)


class GoProTransfer:
    """GoPro Transfer CLI tool for managing GoPro media files."""

    def __init__(self):
        """Initialize the GoProTransfer class."""
        # Setup logging with default settings
        setup_logging()
        logger.info("GoPro Transfer - Initialized")

    def transfer(
        self,
        source=None,
        destination=None,
        media_dir=None,
        date_format=None,
        move=False,
        extract_tel=False,
        tel_formats=None,
        all_dates=False,
        log_level=None,
        log_file=None,
    ):
        """Transfer files from GoPro SD card to organized folders.

        Args:
            source: Path to the GoPro SD card
            destination: Destination path for videos
            media_dir: Media directory name on the SD card
            date_format: Format for date folders
            move: Move files instead of copying them
            extract_tel: Extract telemetry data from videos
            tel_formats: Formats to save telemetry data ('json', 'csv' or comma-separated list)
            all_dates: Transfer files from all dates (default: False, only latest day)
            log_level: Set logging level (TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL)
            log_file: Path to log file

        Returns:
            int: 0 for success, 1 for error
        """
        # Setup logging with command line options
        setup_logging(log_level=log_level, log_file=log_file)
        logger.info("GoPro Transfer - Starting transfer operation")

        # Get settings
        settings = get_settings()
        destination_base = destination or settings.destination_path

        # Parse telemetry formats
        telemetry_formats = []
        if extract_tel:
            if tel_formats:
                telemetry_formats = tel_formats.split(",")
            else:
                telemetry_formats = ["json"]

        # Transfer files
        transferred = transfer_files(
            source,
            destination_base,
            media_dir,
            date_format,
            None,  # Use default file extensions
            move,
            all_dates,
        )

        # Report results
        operation = "moved" if move else "copied"
        if transferred:
            logger.success(f"Successfully {operation} {len(transferred)} files")
            logger.info(f"Files organized in date folders at: {destination_base}")

            # Extract telemetry if requested
            if extract_tel and transferred:
                logger.info("Extracting telemetry data from transferred videos")
                for src_file, dest_file in transferred:
                    if dest_file.lower().endswith(".mp4"):
                        try:
                            logger.info(f"Extracting telemetry from {dest_file}")
                            telemetry = extract_telemetry(dest_file)
                            save_telemetry(
                                telemetry, dest_file, formats=telemetry_formats
                            )
                        except Exception as e:
                            logger.error(
                                f"Failed to extract telemetry from {dest_file}: {e}"
                            )

            return 0
        else:
            logger.error("No files were transferred")
            return 1

    def list(
        self,
        source=None,
        media_dir=None,
        log_level=None,
        log_file=None,
    ):
        """List media files on the GoPro SD card without transferring.

        Args:
            source: Path to the GoPro SD card
            media_dir: Media directory name on the SD card
            log_level: Set logging level (TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL)
            log_file: Path to log file

        Returns:
            int: 0 for success, 1 for error
        """
        # Setup logging with command line options
        setup_logging(log_level=log_level, log_file=log_file)
        logger.info("GoPro Transfer - Listing media files")

        # Get GoPro SD card path
        gopro_path = get_gopro_mount_path(source)
        if not gopro_path:
            logger.error("Failed to find GoPro SD card")
            return 1

        # Find media files
        media_files = get_media_files(gopro_path, media_dir)
        if not media_files:
            logger.error("No media files found")
            return 1

        # Show the files
        list_media_info(media_files)
        return 0

    def telemetry(
        self,
        video_path,
        output_dir=None,
        formats="json",
        log_level=None,
        log_file=None,
    ):
        """Extract telemetry data from GoPro videos.

        Args:
            video_path: Path to GoPro video file or directory containing videos
            output_dir: Directory to save telemetry files (defaults to same as video)
            formats: Formats to save telemetry data ('json', 'csv' or comma-separated list)
            log_level: Set logging level (TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL)
            log_file: Path to log file

        Returns:
            int: 0 for success, 1 for error
        """
        # Setup logging with command line options
        setup_logging(log_level=log_level, log_file=log_file)
        logger.info("GoPro Transfer - Starting telemetry extraction")

        video_path = Path(video_path)
        if not video_path.exists():
            logger.error(f"Video path not found: {video_path}")
            return 1

        # Parse formats
        format_list = formats.split(",")

        # Process single video file
        if video_path.is_file():
            if not video_path.name.lower().endswith(".mp4"):
                logger.error(f"Not a video file: {video_path}")
                return 1

            try:
                logger.info(f"Extracting telemetry from {video_path}")
                telemetry = extract_telemetry(video_path)

                # Determine output path
                output_path = video_path
                if output_dir:
                    output_dir = Path(output_dir)
                    output_dir.mkdir(parents=True, exist_ok=True)
                    output_path = output_dir / video_path.name

                # Save telemetry data
                save_telemetry(telemetry, output_path, formats=format_list)
                logger.success(f"Successfully extracted telemetry from {video_path}")
                return 0
            except Exception as e:
                logger.error(f"Error extracting telemetry: {e}")
                return 1

        # Process directory of videos
        elif video_path.is_dir():
            logger.info(f"Searching for MP4 files in {video_path}")
            mp4_files = list(video_path.glob("**/*.MP4"))
            mp4_files.extend(list(video_path.glob("**/*.mp4")))

            if not mp4_files:
                logger.error(f"No MP4 files found in {video_path}")
                return 1

            logger.info(f"Found {len(mp4_files)} MP4 files")

            # Create output directory if specified
            if output_dir:
                output_dir = Path(output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)

            success_count = 0
            error_count = 0

            for video_file in mp4_files:
                try:
                    logger.info(f"Extracting telemetry from {video_file}")
                    telemetry = extract_telemetry(video_file)

                    # Determine output path
                    output_path = video_file
                    if output_dir:
                        output_path = output_dir / video_file.name

                    # Save telemetry data
                    save_telemetry(telemetry, output_path, formats=format_list)
                    success_count += 1
                except Exception as e:
                    logger.error(f"Error extracting telemetry from {video_file}: {e}")
                    error_count += 1

            logger.success(
                f"Telemetry extraction completed: {success_count} successful, {error_count} failed"
            )
            return 0 if error_count == 0 else 1

        else:
            logger.error(f"Invalid path: {video_path}")
            return 1


def main():
    """Run the GoPro Transfer application with Fire CLI."""
    # Return the exit code
    return fire.Fire(GoProTransfer)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
