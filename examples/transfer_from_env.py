#!/usr/bin/env python
"""Example script demonstrating how to use the gopro-transfer library with environment variables."""

import os
import sys
from pathlib import Path

# Add the src directory to the path so we can import the package
sys.path.append(str(Path(__file__).parent.parent))

from gopro_transfer.config import Settings
from gopro_transfer.logger import setup_logger
from gopro_transfer.main import GoProTransfer


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
        # Create a new GoProTransfer instance
        transfer = GoProTransfer()

        # Call the transfer method
        result = transfer.transfer(
            source=settings.source_path,
            destination=settings.destination_path,
            media_dir=settings.media_dir,
            date_format=settings.date_format,
            log_level="INFO",
        )

        if result == 0:
            logger.success("Transfer completed successfully")
        else:
            logger.error("Transfer failed")
            return 1
    except Exception as e:
        logger.error(f"Error during transfer: {e}")
        return 1

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
