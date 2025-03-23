#!/usr/bin/env python3
"""Example script demonstrating how to use the gopro-transfer library with environment variables."""

import os
import sys
from pathlib import Path

# Add the src directory to the path so we can import the package
sys.path.append(str(Path(__file__).parent.parent))

from gopro_transfer.config import Settings
from gopro_transfer.logger import setup_logger
from gopro_transfer.main import transfer_files


def main():
    """Run the gopro-transfer process with environment variables."""
    # Set up logging first
    logger = setup_logger()
    logger.info("Starting GoPro Transfer Example Script")

    # Load settings from environment variables
    try:
        settings = Settings()
        logger.info(
            f"Loaded settings: source={settings.source_path}, "
            f"destination={settings.destination_path}"
        )
    except Exception as e:
        logger.error(f"Failed to load settings: {e}")
        return 1

    # Get user confirmation
    logger.info("Ready to transfer files with the following settings:")
    logger.info(f"  Source: {settings.source_path}")
    logger.info(f"  Destination: {settings.destination_path}")
    logger.info(f"  Media directory: {settings.media_dir}")
    logger.info(f"  Date format: {settings.date_format}")
    logger.info(f"  File extensions: {settings.file_extensions}")

    confirm = input("Do you want to proceed with the transfer? (y/n): ")
    if confirm.lower() != "y":
        logger.info("Transfer canceled by user")
        return 0

    # Start the transfer process
    logger.info("Starting file transfer...")
    try:
        transferred_files = transfer_files(
            settings.source_path,
            settings.destination_path,
            settings.media_dir,
            settings.date_format,
            settings.file_extensions,
        )
        logger.success(f"Successfully transferred {len(transferred_files)} files")

        # Print out the transferred files
        if transferred_files:
            logger.info("Transferred files:")
            for src, dest in transferred_files:
                logger.info(f"  {src} -> {dest}")
    except Exception as e:
        logger.error(f"Error during transfer: {e}")
        return 1

    logger.info("Transfer completed successfully")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
