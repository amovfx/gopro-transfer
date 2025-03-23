"""Main entry point for GoPro Transfer application."""

import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

import fire
from loguru import logger

from gopro_transfer.config import get_settings, Settings
from gopro_transfer.logger import setup_logging
from gopro_transfer.media_info import get_media_metadata, get_gopro_folder_structure


def get_gopro_mount_path(custom_path=None):
    """Find the GoPro SD card mount path.

    Args:
        custom_path: Optional custom path to the SD card

    Returns:
        Path: Path to the GoPro SD card or None if not found
    """
    if custom_path:
        gopro_path = Path(custom_path)
        if gopro_path.exists() and gopro_path.is_dir():
            logger.info(f"Using custom GoPro path: {gopro_path}")
            return gopro_path
        logger.error(f"Custom path {custom_path} not found or not a directory")
        return None

    # On macOS, removable media is typically mounted under /Volumes
    settings = get_settings()
    default_path = settings.source_path
    gopro_path = Path(default_path)
    if gopro_path.exists() and gopro_path.is_dir():
        logger.info(f"Found GoPro SD card at {gopro_path}")
        return gopro_path

    logger.error(f"GoPro SD card not found at {default_path}")
    return None


def get_media_files(gopro_path, media_dir_name=None):
    """Get all media files from the GoPro SD card.

    Args:
        gopro_path: Path to the GoPro SD card
        media_dir_name: Name of the media directory, uses config default if None

    Returns:
        list: List of media file paths
    """
    settings = get_settings()
    media_dir_name = media_dir_name or settings.media_dir
    file_extensions = settings.file_extensions

    logger.info(f"Searching for media files in {gopro_path}")
    logger.debug(f"Using media directory: {media_dir_name}")
    logger.debug(f"Looking for file extensions: {file_extensions}")

    # Use the folder structure analyzer
    folder_info = get_gopro_folder_structure(gopro_path)

    if not folder_info["dcim_folder"]:
        logger.error(f"DCIM folder not found in {gopro_path}")
        return []

    if not folder_info["media_folders"]:
        logger.error("No GoPro media folders found")
        return []

    # If no specific media folder is specified, get files from all folders
    media_files = []

    if media_dir_name:
        # Only look in the specified folder
        for folder in folder_info["media_folders"]:
            if folder["name"] == media_dir_name:
                media_dir = Path(folder["path"])
                logger.info(f"Searching in media directory: {media_dir}")
                for ext in file_extensions:
                    files = list(media_dir.glob(f"*{ext}"))
                    logger.debug(f"Found {len(files)} {ext} files")
                    media_files.extend(files)
                break
    else:
        # Look in all media folders
        for folder in folder_info["media_folders"]:
            media_dir = Path(folder["path"])
            logger.info(f"Searching in media directory: {media_dir}")
            for ext in file_extensions:
                files = list(media_dir.glob(f"*{ext}"))
                logger.debug(f"Found {len(files)} {ext} files")
                media_files.extend(files)

    if not media_files:
        logger.warning("No media files found on the SD card")
    else:
        logger.success(f"Found {len(media_files)} media files")

    return media_files


def get_file_date(file_path):
    """Get the creation date of a file.

    Args:
        file_path: Path to the file

    Returns:
        datetime: Creation date of the file
    """
    # Use our media_info module to get metadata
    metadata = get_media_metadata(file_path)

    # Prefer creation date if available
    if metadata["creation_date"]:
        logger.trace(
            f"Using creation date for {file_path.name}: {metadata['creation_date']}"
        )
        return metadata["creation_date"]

    # Fall back to modification date
    if metadata["modification_date"]:
        logger.trace(
            f"Using modification date for {file_path.name}: {metadata['modification_date']}"
        )
        return metadata["modification_date"]

    # Last resort: current time
    logger.warning(
        f"No date information found for {file_path.name}, using current time"
    )
    return datetime.now()


def transfer_files(
    source_path=None,
    destination_path=None,
    media_dir=None,
    date_format=None,
    file_extensions=None,
    move=False,
):
    """Transfer files from GoPro SD card to destination organized by date.

    Args:
        source_path: Path to the GoPro SD card or custom source
        destination_path: Destination path for media files
        media_dir: Media directory name on the SD card
        date_format: Format string for date folders
        file_extensions: Comma-separated list of file extensions to look for
        move: Whether to move files instead of copying

    Returns:
        list: List of tuple pairs (source_path, dest_path) of transferred files
    """
    settings = get_settings()

    # Use provided values or defaults from settings
    source = source_path or settings.source_path
    destination = destination_path or settings.destination_path
    media_dirname = media_dir or settings.media_dir
    date_fmt = date_format or settings.date_format
    extensions = file_extensions or settings.file_extensions

    # Get GoPro SD card path
    gopro_path = get_gopro_mount_path(source)
    if not gopro_path:
        logger.error("Failed to find GoPro SD card")
        return []

    # Find media files
    media_files = get_media_files(gopro_path, media_dirname)
    if not media_files:
        logger.error("No media files found")
        return []

    destination_path = Path(destination)

    # Ensure the destination directory exists
    destination_path.mkdir(parents=True, exist_ok=True)

    operation = "Moving" if move else "Copying"
    logger.info(f"{operation} files to {destination_path} using date format {date_fmt}")

    transferred_files = []
    total_size = 0

    for file_path in media_files:
        # Get file metadata
        metadata = get_media_metadata(file_path)

        # Get file date and format according to config
        file_date = get_file_date(file_path)
        date_folder = file_date.strftime(date_fmt)

        # Create date folder if it doesn't exist
        date_dir = destination_path / date_folder
        date_dir.mkdir(exist_ok=True)

        # Destination file path
        dest_file = date_dir / file_path.name

        # Skip if file already exists
        if dest_file.exists():
            logger.info(f"Skipping {file_path.name} - already exists in destination")
            continue

        # Get file size in MB for reporting
        file_size_mb = metadata["size"] / (1024 * 1024)

        logger.info(
            f"{operation} {file_path.name} ({file_size_mb:.1f} MB) to {date_folder}/"
        )
        logger.debug(f"Full destination path: {dest_file}")

        try:
            if move:
                shutil.move(str(file_path), str(dest_file))
            else:
                shutil.copy2(str(file_path), str(dest_file))
            transferred_files.append((str(file_path), str(dest_file)))
            total_size += metadata["size"]
            logger.debug(f"Successfully transferred {file_path.name}")
        except Exception as e:
            logger.error(f"Error transferring {file_path}: {e}")

    # Calculate total size in MB
    total_size_mb = total_size / (1024 * 1024)
    logger.success(
        f"Total transferred: {len(transferred_files)} files ({total_size_mb:.1f} MB)"
    )

    return transferred_files


def list_media_info(media_files):
    """List information about media files.

    Args:
        media_files: List of media file paths
    """
    logger.info(f"Listing information for {len(media_files)} media files")

    for file_path in media_files:
        metadata = get_media_metadata(file_path)
        size_mb = metadata["size"] / (1024 * 1024)

        date_str = "Unknown date"
        if metadata["creation_date"]:
            date_str = metadata["creation_date"].strftime("%Y-%m-%d %H:%M:%S")

        file_type = metadata.get("file_type", "unknown")
        file_num = metadata.get("file_number", "")

        info = f"{file_path.name} ({size_mb:.1f} MB) - {date_str} - Type: {file_type} {file_num}"
        print(info)  # Keep print for direct user output
        logger.debug(f"File info: {info}")


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

        # Transfer files
        transferred = transfer_files(
            source,
            destination_base,
            media_dir,
            date_format,
            None,  # Use default file extensions
            move,
        )

        # Report results
        operation = "moved" if move else "copied"
        if transferred:
            logger.success(f"Successfully {operation} {len(transferred)} files")
            logger.info(f"Files organized in date folders at: {destination_base}")
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


def main():
    """Run the GoPro Transfer application with Fire CLI."""
    # Return the exit code
    return fire.Fire(GoProTransfer)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
