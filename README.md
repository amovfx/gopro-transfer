# GoPro Transfer

A tool for transferring and managing GoPro media files. This utility automatically detects your GoPro SD card, finds videos and photos, and transfers them to your computer organized in date-based folders.

## Features

- Automatically detect GoPro SD card
- Copy or move media files from SD card to your computer
- Organize files into folders by date
- Simple configuration via environment variables
- Extract basic metadata from GoPro files
- Support for older and newer GoPro naming conventions
- Structured logging to console and files

## Installation

```bash
pip install gopro-transfer
```

Or install from source:

```bash
git clone https://github.com/yourusername/gopro-transfer.git
cd gopro-transfer
pip install -e .
```

## Usage

Basic usage:

```bash
# Copy files from your GoPro SD card to your computer
gopro-transfer

# Move files instead of copying
gopro-transfer --move

# List files without transferring
gopro-transfer --list
```

Advanced options:

```bash
# Specify custom source and destination paths
gopro-transfer --source /path/to/gopro --destination /path/to/save

# Use a specific media directory on the SD card
gopro-transfer --media-dir 101GOPRO
```

## Configuration

The application uses environment variables for configuration. You can set these in your shell or create a `.env` file in your working directory.

Copy the provided `.env.example` file to `.env` and customize:

```bash
cp .env.example .env
```

### Environment Variables

Available environment variables:

- `GOPRO_SOURCE_PATH`: Path to the GoPro SD card (default: `/Volumes/GoPro`)
- `GOPRO_DESTINATION_PATH`: Path where files will be transferred to (default: `~/Documents/Videos/GoPro`)
- `GOPRO_MEDIA_DIR`: Media directory name on the SD card (default: `100GOPRO`) 
- `GOPRO_DATE_FORMAT`: Date format for organizing files (default: `%Y-%m-%d`)
- `GOPRO_FILE_EXTENSIONS`: Comma-separated list of file extensions to look for (default: `.MP4,.JPG,.RAW`)
- `GOPRO_LOG_LEVEL`: Logging level (default: `INFO`)
- `GOPRO_LOG_FILE`: Path to log file (default: `~/.logs/gopro-transfer/gopro-transfer-YYYYMMDD.log`)
- `GOPRO_LOG_DIR`: Directory to store log files (default: `~/.logs/gopro-transfer`)

Example `.env` file:

```
GOPRO_SOURCE_PATH=/Volumes/GOPRO-CARD
GOPRO_DESTINATION_PATH=/Users/username/Movies/MyGoPro
GOPRO_MEDIA_DIR=100GOPRO
GOPRO_LOG_LEVEL=DEBUG
```

## Logging

The application uses [Loguru](https://github.com/Delgan/loguru) for structured logging. By default, logs are written to both the console and a log file.

### Log Levels

Available log levels (from most to least verbose):

- `TRACE`: Most detailed information for developers
- `DEBUG`: Detailed information for debugging
- `INFO`: General information about program operation (default)
- `SUCCESS`: Successful operations
- `WARNING`: Potential issues that don't prevent operation
- `ERROR`: Errors that prevent specific operations
- `CRITICAL`: Critical errors that prevent the program from running

You can set the log level using the `--log-level` command line argument or the `GOPRO_LOG_LEVEL` environment variable.

Example:

```bash
# Run with debug logging
gopro-transfer --log-level DEBUG

# Specify a custom log file
gopro-transfer --log-file /path/to/my-log.log
```

## Development

This project uses a src-layout for Python packaging.

```bash
# Clone the repository
git clone https://github.com/yourusername/gopro-transfer.git
cd gopro-transfer

# Install development dependencies
uv add --dev pytest pytest-cov

# Run the application directly from source
python -m gopro_transfer.main
```

## License

MIT
