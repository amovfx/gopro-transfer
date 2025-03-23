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
- Extract telemetry data (GPS, accelerometer, gyroscope, temperature) from GoPro videos

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

### Command Line Interface

The application uses Google [Fire](https://github.com/google/python-fire) for its command-line interface, providing a simple and flexible way to interact with the tool.

Basic usage examples:

```bash
# Transfer files with default settings
gopro-transfer transfer

# List files on the GoPro SD card without transferring
gopro-transfer list

# Transfer files from a custom source path
gopro-transfer transfer --source /path/to/gopro

# Transfer files to a custom destination
gopro-transfer transfer --destination ~/Videos/GoPro-Footage

# Move files instead of copying
gopro-transfer transfer --move

# Set custom logging level 
gopro-transfer transfer --log-level DEBUG

# Combining multiple options
gopro-transfer transfer --source /Volumes/GOPRO --destination ~/Videos --media-dir 101GOPRO --move
```

Fire automatically generates help documentation based on docstrings. You can view the help with:

```bash
# Show top-level help
gopro-transfer --help

# Show help for the transfer command
gopro-transfer transfer --help

# Show help for the list command
gopro-transfer list --help
```

## Telemetry Extraction

GoPro cameras (Hero5 and later) capture extensive telemetry data in the MP4 files they create, including:

- GPS coordinates, altitude, and speed
- Accelerometer readings (motion in X, Y, Z axes)
- Gyroscope readings (rotation around X, Y, Z axes)
- Temperature readings
- Other sensor data depending on the camera model

### Extracting Telemetry

You can extract this telemetry data in one of two ways:

1. **During transfer** - Extract telemetry as files are transferred:

```bash
# Transfer files and extract telemetry in JSON format
gopro-transfer transfer --extract-tel

# Transfer files and extract telemetry in both JSON and CSV formats
gopro-transfer transfer --extract-tel --tel-formats=json,csv
```

2. **From existing files** - Extract telemetry from already transferred files:

```bash
# Extract telemetry from a single video file
gopro-transfer telemetry /path/to/GX010123.MP4

# Extract telemetry from a directory of videos to a specific output directory
gopro-transfer telemetry /path/to/videos --output-dir /path/to/telemetry

# Extract telemetry as CSV files
gopro-transfer telemetry /path/to/video.MP4 --formats=csv

# Extract telemetry in multiple formats
gopro-transfer telemetry /path/to/video.MP4 --formats=json,csv
```

### Telemetry Output Files

For each video file, the following telemetry files will be generated:

For a video named `GX010123.MP4`:

- `GX010123_telemetry.json` - All telemetry data in a single JSON file
- `GX010123_gps.csv` - GPS data (latitude, longitude, altitude, speed)
- `GX010123_accl.csv` - Accelerometer data (X, Y, Z axes)
- `GX010123_gyro.csv` - Gyroscope data (X, Y, Z axes)
- `GX010123_temp.csv` - Temperature data

The naming convention uses the video filename without the extension, followed by the telemetry type, making it easy to associate each telemetry file with its source video.

Note: Not all GoPro models capture all types of telemetry. The available data depends on your camera model and settings.

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
