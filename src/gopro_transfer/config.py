"""Configuration settings for GoPro Transfer using Pydantic V2."""

import os
from pathlib import Path
from typing import List, ClassVar, Optional

from pydantic import BaseModel, ConfigDict, field_validator, Field
from dotenv import load_dotenv
from loguru import logger


# Load environment variables from .env file
load_dotenv()


class Settings(BaseModel):
    """Pydantic V2 model for application settings."""

    model_config: ClassVar[ConfigDict] = ConfigDict(
        validate_assignment=True,
        extra="ignore",
        frozen=False,
        env_prefix="GOPRO_",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    source_path: str = Field(
        default="/Volumes/GoPro",
        description="Path to the GoPro SD card",
        env="GOPRO_SOURCE_PATH",
    )
    destination_path: str = Field(
        default=str(Path.home() / "Documents" / "Videos" / "GoPro"),
        description="Path where files will be transferred to",
        env="GOPRO_DESTINATION_PATH",
    )
    media_dir: str = Field(
        default="100GOPRO",
        description="Media directory name on the SD card",
        env="GOPRO_MEDIA_DIR",
    )
    date_format: str = Field(
        default="%Y-%m-%d",
        description="Date format for organizing files",
        env="GOPRO_DATE_FORMAT",
    )
    file_extensions: List[str] = Field(
        default=[".MP4", ".JPG", ".RAW"],
        description="File extensions to look for",
        env="GOPRO_FILE_EXTENSIONS",
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level",
        env="GOPRO_LOG_LEVEL",
    )
    log_file: Optional[str] = Field(
        default=None,
        description="Path to log file",
        env="GOPRO_LOG_FILE",
    )

    @field_validator("source_path", "destination_path", mode="after")
    @classmethod
    def validate_paths(cls, v: str) -> str:
        """Validate and normalize paths.

        Args:
            v: Path string to validate

        Returns:
            Normalized path string
        """
        path = str(Path(v).expanduser().resolve())
        logger.debug(f"Normalized path: {v} -> {path}")
        return path

    @field_validator("file_extensions", mode="before")
    @classmethod
    def parse_file_extensions(cls, v) -> List[str]:
        """Parse file extensions from environment variable.

        If the value comes from an environment variable, it might be a comma-separated string.

        Args:
            v: Value to parse

        Returns:
            List of file extensions
        """
        if isinstance(v, str):
            extensions = [ext.strip() for ext in v.split(",")]
            logger.debug(f"Parsed file extensions: {v} -> {extensions}")
            return extensions
        return v


def get_settings() -> Settings:
    """Load settings from environment variables.

    Returns:
        Settings: Application settings
    """
    # Create settings from environment variables
    settings = Settings()
    logger.debug(f"Loaded settings: {settings.model_dump()}")
    return settings


# For backwards compatibility with code that uses load_settings
load_settings = get_settings
