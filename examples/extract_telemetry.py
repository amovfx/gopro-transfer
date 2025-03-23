#!/usr/bin/env python
"""Example script demonstrating how to extract telemetry from GoPro videos."""

import os
import sys
from pathlib import Path

# Add the src directory to the path so we can import the package
sys.path.append(str(Path(__file__).parent.parent))

from gopro_transfer.logger import setup_logger
from gopro_transfer.telemetry import extract_telemetry, save_telemetry


def main():
    """Extract telemetry from GoPro videos."""
    # Set up logging
    logger = setup_logger()
    logger.info("Starting GoPro Telemetry Extraction Example")

    # Get the video path from the command line or use a default
    if len(sys.argv) > 1:
        video_path = Path(sys.argv[1])
    else:
        print("Usage: python extract_telemetry.py <path_to_video>")
        return 1

    # Check if the file exists
    if not video_path.exists():
        logger.error(f"Video file not found: {video_path}")
        return 1

    if not video_path.name.lower().endswith(".mp4"):
        logger.error(f"Not a video file: {video_path}")
        return 1

    logger.info(f"Processing video: {video_path}")

    try:
        # Extract telemetry
        logger.info("Extracting telemetry data...")
        telemetry = extract_telemetry(video_path)

        # Display summary of extracted data
        logger.success("Telemetry extracted successfully")
        logger.info(f"GPS data points: {len(telemetry.gps)}")
        logger.info(f"Accelerometer data points: {len(telemetry.accl)}")
        logger.info(f"Gyroscope data points: {len(telemetry.gyro)}")
        logger.info(f"Temperature data points: {len(telemetry.temp)}")

        # Save telemetry data
        logger.info("Saving telemetry data...")
        output_files = save_telemetry(telemetry, video_path, formats=["json", "csv"])

        # Display paths to saved files
        logger.success("Telemetry data saved to:")
        for format_name, file_path in output_files.items():
            logger.info(f"  {format_name}: {file_path}")

        # Show pairing information
        video_name = video_path.stem
        logger.info(
            f"Telemetry files are named with the pattern: {video_name}_<type>.<ext>"
        )
        logger.info(
            "This makes it easy to pair each telemetry file with its source video."
        )

    except Exception as e:
        logger.error(f"Error extracting telemetry: {e}")
        return 1

    logger.success("Telemetry extraction completed successfully")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
