"""Media file information utilities."""

import os
import re
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, Tuple

from loguru import logger


def get_media_metadata(file_path: Path) -> Dict[str, Any]:
    """Extract metadata from a media file.

    Args:
        file_path: Path to the media file

    Returns:
        dict: Media metadata
    """
    logger.debug(f"Extracting metadata for {file_path.name}")

    metadata = {
        "filename": file_path.name,
        "path": str(file_path),
        "size": file_path.stat().st_size,
        "creation_date": None,
        "modification_date": None,
    }

    # Get file dates
    stat_info = file_path.stat()

    # Use creation time on macOS
    if hasattr(stat_info, "st_birthtime"):
        metadata["creation_date"] = datetime.fromtimestamp(stat_info.st_birthtime)
        logger.trace(f"Creation date for {file_path.name}: {metadata['creation_date']}")

    # Modification time is available on all platforms
    metadata["modification_date"] = datetime.fromtimestamp(stat_info.st_mtime)
    logger.trace(
        f"Modification date for {file_path.name}: {metadata['modification_date']}"
    )

    # Try to extract GoPro-specific metadata from filename
    gopro_info = parse_gopro_filename(file_path.name)
    metadata.update(gopro_info)

    return metadata


def parse_gopro_filename(filename: str) -> Dict[str, Any]:
    """Parse GoPro filename to extract metadata.

    GoPro typically names files like:
    GX123456.MP4 (older models)
    GOPR1234.MP4 (main file)
    GP011234.MP4 (chapter 1 of file 1234)

    Args:
        filename: GoPro filename

    Returns:
        dict: Extracted metadata
    """
    logger.trace(f"Parsing GoPro filename: {filename}")
    info = {}

    # GoPro Hero5 and later use format GXNNNNNN.MP4
    # G = camera letter (X/O/H/etc)
    # X = First letter: G for main file, number for chapter
    # NNNNNN = file number
    match = re.match(r"G([A-Z0-9])(\d{6})\.", filename)
    if match:
        type_code, file_number = match.groups()

        if type_code.isdigit():
            info["file_type"] = "chapter"
            info["chapter"] = int(type_code)
        else:
            info["file_type"] = "main"

        info["file_number"] = file_number
        logger.trace(f"Parsed newer GoPro format: {info}")
        return info

    # Older GoPro format: GOPRNNNN.MP4 (main) or GPSSNNNN.MP4 (chapter)
    # SS = chapter number
    # NNNN = file number
    match = re.match(r"(GOPR|GP(\d{2}))(\d{4})\.", filename)
    if match:
        prefix, chapter, file_number = match.groups()

        if prefix == "GOPR":
            info["file_type"] = "main"
        else:
            info["file_type"] = "chapter"
            info["chapter"] = int(chapter)

        info["file_number"] = file_number
        logger.trace(f"Parsed older GoPro format: {info}")
        return info

    logger.debug(f"Unable to parse GoPro format for: {filename}")
    return {}


def get_video_duration(file_path: Path) -> Optional[float]:
    """Get the duration of a video file in seconds.

    Requires ffprobe (ffmpeg) to be installed.

    Args:
        file_path: Path to the video file

    Returns:
        float: Duration in seconds or None if not available
    """
    logger.debug(f"Getting video duration for {file_path.name}")
    try:
        # Try to use ffprobe to get video duration
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(file_path),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if result.returncode == 0 and result.stdout.strip():
            duration = float(result.stdout.strip())
            logger.debug(f"Video duration: {duration} seconds")
            return duration
    except (subprocess.SubprocessError, ValueError, FileNotFoundError) as e:
        logger.warning(f"Failed to get video duration: {e}")

    logger.warning(f"Could not determine video duration for {file_path.name}")
    return None


def get_gopro_folder_structure(gopro_path: Path) -> Dict[str, Any]:
    """Analyze GoPro SD card folder structure.

    Args:
        gopro_path: Path to the GoPro SD card

    Returns:
        dict: Folder structure information
    """
    logger.debug(f"Analyzing GoPro folder structure at {gopro_path}")

    result = {
        "path": str(gopro_path),
        "dcim_folder": False,
        "media_folders": [],
        "media_count": 0,
    }

    dcim_path = gopro_path / "DCIM"
    if not dcim_path.exists() or not dcim_path.is_dir():
        logger.warning(f"DCIM folder not found at {gopro_path}")
        return result

    result["dcim_folder"] = True
    logger.debug("Found DCIM folder")

    # Look for media folders (typically 100GOPRO, 101GOPRO, etc.)
    for item in dcim_path.iterdir():
        if item.is_dir() and re.match(r"\d{3}GOPRO", item.name):
            mp4_count = sum(1 for _ in item.glob("*.MP4"))
            jpg_count = sum(1 for _ in item.glob("*.JPG"))

            folder_info = {
                "name": item.name,
                "path": str(item),
                "media_count": mp4_count,
                "photo_count": jpg_count,
            }
            result["media_folders"].append(folder_info)
            result["media_count"] += (
                folder_info["media_count"] + folder_info["photo_count"]
            )

            logger.debug(
                f"Found media folder: {item.name} with {mp4_count} videos and {jpg_count} photos"
            )

    logger.info(
        f"Found {len(result['media_folders'])} media folders with {result['media_count']} total files"
    )
    return result
