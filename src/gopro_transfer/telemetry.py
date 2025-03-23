"""Module for extracting telemetry data from GoPro videos."""

import json
import os
from pathlib import Path
from typing import Dict, List, Union, Optional, Any

import gpmf
from loguru import logger


class TelemetryData:
    """Class to represent the extracted telemetry data from a GoPro video."""

    def __init__(
        self,
        gps: Optional[List[Dict[str, Any]]] = None,
        accl: Optional[List[Dict[str, Any]]] = None,
        gyro: Optional[List[Dict[str, Any]]] = None,
        temp: Optional[List[Dict[str, Any]]] = None,
        other_data: Optional[Dict[str, List[Dict[str, Any]]]] = None,
    ):
        """Initialize the TelemetryData object.

        Args:
            gps: List of GPS data points
            accl: List of accelerometer data points
            gyro: List of gyroscope data points
            temp: List of temperature data points
            other_data: Dict of other telemetry data
        """
        self.gps = gps or []
        self.accl = accl or []
        self.gyro = gyro or []
        self.temp = temp or []
        self.other_data = other_data or {}

    def to_json(self, output_path: Optional[str] = None) -> Optional[str]:
        """Convert telemetry data to JSON format.

        Args:
            output_path: Path to save JSON file. If None, returns the JSON string

        Returns:
            JSON string if output_path is None, otherwise None
        """
        data = {
            "gps": self.gps,
            "accl": self.accl,
            "gyro": self.gyro,
            "temp": self.temp,
            **self.other_data,
        }

        json_data = json.dumps(data, indent=2)

        if output_path:
            with open(output_path, "w") as f:
                f.write(json_data)
            logger.info(f"Telemetry data saved to {output_path}")
            return None

        return json_data


def extract_telemetry(video_path: Union[str, Path]) -> TelemetryData:
    """Extract telemetry data from a GoPro video.

    Args:
        video_path: Path to the GoPro video file

    Returns:
        TelemetryData object containing the extracted telemetry

    Raises:
        FileNotFoundError: If the video file doesn't exist
        ValueError: If the file is not a GoPro video or has no telemetry data
    """
    video_path = Path(video_path)

    if not video_path.exists():
        logger.error(f"Video file not found: {video_path}")
        raise FileNotFoundError(f"Video file not found: {video_path}")

    logger.info(f"Extracting telemetry data from {video_path}")

    try:
        # Parse the GoPro GPMF data
        parser = gpmf.Parser(str(video_path))
    except Exception as e:
        logger.error(f"Failed to parse GPMF data: {e}")
        raise ValueError(f"Failed to parse GPMF data: {e}")

    # Get all available streams
    streams = parser.get_streams()
    logger.debug(f"Available telemetry streams: {streams}")

    # Process GPS data if available
    gps_data = []
    if "GPS5" in streams:
        logger.info("Extracting GPS data")
        try:
            gps_stream = parser.get_stream("GPS5")
            for data_point in gps_stream:
                # GPS5 format: [latitude, longitude, altitude, speed, speed3d]
                gps_data.append(
                    {
                        "timestamp": data_point["timestamp"],
                        "latitude": data_point["value"][0],
                        "longitude": data_point["value"][1],
                        "altitude": data_point["value"][2],
                        "speed": data_point["value"][3],
                        "speed3d": data_point["value"][4],
                    }
                )
            logger.success(f"Extracted {len(gps_data)} GPS data points")
        except Exception as e:
            logger.warning(f"Error extracting GPS data: {e}")

    # Process accelerometer data if available
    accl_data = []
    if "ACCL" in streams:
        logger.info("Extracting accelerometer data")
        try:
            accl_stream = parser.get_stream("ACCL")
            for data_point in accl_stream:
                # ACCL format: [x, y, z]
                accl_data.append(
                    {
                        "timestamp": data_point["timestamp"],
                        "x": data_point["value"][0],
                        "y": data_point["value"][1],
                        "z": data_point["value"][2],
                    }
                )
            logger.success(f"Extracted {len(accl_data)} accelerometer data points")
        except Exception as e:
            logger.warning(f"Error extracting accelerometer data: {e}")

    # Process gyroscope data if available
    gyro_data = []
    if "GYRO" in streams:
        logger.info("Extracting gyroscope data")
        try:
            gyro_stream = parser.get_stream("GYRO")
            for data_point in gyro_stream:
                # GYRO format: [x, y, z]
                gyro_data.append(
                    {
                        "timestamp": data_point["timestamp"],
                        "x": data_point["value"][0],
                        "y": data_point["value"][1],
                        "z": data_point["value"][2],
                    }
                )
            logger.success(f"Extracted {len(gyro_data)} gyroscope data points")
        except Exception as e:
            logger.warning(f"Error extracting gyroscope data: {e}")

    # Process temperature data if available
    temp_data = []
    if "TMPC" in streams:
        logger.info("Extracting temperature data")
        try:
            temp_stream = parser.get_stream("TMPC")
            for data_point in temp_stream:
                # TMPC format: [temperature]
                temp_data.append(
                    {
                        "timestamp": data_point["timestamp"],
                        "temperature": data_point["value"][0],
                    }
                )
            logger.success(f"Extracted {len(temp_data)} temperature data points")
        except Exception as e:
            logger.warning(f"Error extracting temperature data: {e}")

    # Process other available streams
    other_data = {}
    for stream_name in streams:
        if stream_name not in ["GPS5", "ACCL", "GYRO", "TMPC"]:
            logger.debug(f"Extracting data from stream: {stream_name}")
            try:
                stream_data = []
                data_stream = parser.get_stream(stream_name)
                for data_point in data_stream:
                    point_data = {
                        "timestamp": data_point["timestamp"],
                        "value": data_point["value"],
                    }
                    stream_data.append(point_data)

                if stream_data:
                    other_data[stream_name] = stream_data
                    logger.debug(
                        f"Extracted {len(stream_data)} data points from {stream_name}"
                    )
            except Exception as e:
                logger.debug(f"Error extracting data from {stream_name}: {e}")

    # Create and return the telemetry data object
    telemetry = TelemetryData(
        gps=gps_data,
        accl=accl_data,
        gyro=gyro_data,
        temp=temp_data,
        other_data=other_data,
    )

    logger.success(f"Successfully extracted telemetry data from {video_path}")
    return telemetry


def save_telemetry(
    telemetry: TelemetryData, base_path: Union[str, Path], formats: List[str] = ["json"]
) -> Dict[str, str]:
    """Save telemetry data to various formats.

    Args:
        telemetry: TelemetryData object to save
        base_path: Base path for saving files
        formats: List of formats to save ('json', 'csv')

    Returns:
        Dict mapping format to saved file path
    """
    base_path = Path(base_path)
    output_files = {}

    # Create directory if it doesn't exist
    base_path.parent.mkdir(parents=True, exist_ok=True)

    # Get base name without extension for cleaner file naming
    base_name = base_path.stem
    output_dir = base_path.parent

    # Save as JSON
    if "json" in formats:
        json_path = output_dir / f"{base_name}_telemetry.json"
        telemetry.to_json(str(json_path))
        output_files["json"] = str(json_path)
        logger.info(f"Telemetry data saved to {json_path}")

    # Save as CSV files - one for each data type
    if "csv" in formats:
        # GPS data
        if telemetry.gps:
            csv_path = output_dir / f"{base_name}_gps.csv"
            with open(csv_path, "w") as f:
                f.write("timestamp,latitude,longitude,altitude,speed,speed3d\n")
                for point in telemetry.gps:
                    f.write(
                        f"{point['timestamp']},{point['latitude']},{point['longitude']},"
                        f"{point['altitude']},{point['speed']},{point['speed3d']}\n"
                    )
            output_files["gps_csv"] = str(csv_path)
            logger.info(f"GPS data saved to {csv_path}")

        # Accelerometer data
        if telemetry.accl:
            csv_path = output_dir / f"{base_name}_accl.csv"
            with open(csv_path, "w") as f:
                f.write("timestamp,x,y,z\n")
                for point in telemetry.accl:
                    f.write(
                        f"{point['timestamp']},{point['x']},{point['y']},{point['z']}\n"
                    )
            output_files["accl_csv"] = str(csv_path)
            logger.info(f"Accelerometer data saved to {csv_path}")

        # Gyroscope data
        if telemetry.gyro:
            csv_path = output_dir / f"{base_name}_gyro.csv"
            with open(csv_path, "w") as f:
                f.write("timestamp,x,y,z\n")
                for point in telemetry.gyro:
                    f.write(
                        f"{point['timestamp']},{point['x']},{point['y']},{point['z']}\n"
                    )
            output_files["gyro_csv"] = str(csv_path)
            logger.info(f"Gyroscope data saved to {csv_path}")

        # Temperature data
        if telemetry.temp:
            csv_path = output_dir / f"{base_name}_temp.csv"
            with open(csv_path, "w") as f:
                f.write("timestamp,temperature\n")
                for point in telemetry.temp:
                    f.write(f"{point['timestamp']},{point['temperature']}\n")
            output_files["temp_csv"] = str(csv_path)
            logger.info(f"Temperature data saved to {csv_path}")

    return output_files
