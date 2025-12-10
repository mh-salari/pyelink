"""Core EyeLink wrapper functionality.

This module provides the main interface for interacting with SR Research EyeLink
eye trackers via Pylink. It includes Settings configuration and the unified
EyeLink tracker interface.
"""

from __future__ import annotations

import atexit
import contextlib
import json
import logging
import os
import signal
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Self

import pylink

from . import defaults
from .calibration import create_calibration
from .data import DataBuffer
from .events import EventProcessor

if TYPE_CHECKING:
    import types

logger = logging.getLogger(__name__)

# Configure logging to output to console by default
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)


@dataclass
class Settings:
    """Default settings for EyeLink tracker configuration.

    All default values come from pyelink.defaults module. Override any attribute after instantiation.
    """

    # File settings
    FILENAME: str = defaults.FILENAME  # Name of the EDF file to be created for each session
    FILEPATH: str = defaults.FILEPATH  # Path where the EDF file will be saved (empty string = current directory)

    # Sampling settings
    SAMPLE_RATE: int = defaults.SAMPLE_RATE  # Always use 1000 Hz; lower rates are filtered/downsampled versions

    # Calibration settings
    N_CAL_TARGETS: int = defaults.N_CAL_TARGETS  # Number of calibration points (9 is standard; 13 for widescreens)
    PACING_INTERVAL: int = defaults.PACING_INTERVAL  # Time in ms to fixate each target during calibration
    CALIBRATION_CORNER_SCALING: float = (
        defaults.CALIBRATION_CORNER_SCALING
    )  # How far corner calibration points are from the screen edge (1=default; <1 closer to center, >1 closer to edge)
    VALIDATION_CORNER_SCALING: float = (
        defaults.VALIDATION_CORNER_SCALING
    )  # How far corner validation points are from the screen edge (same scaling as above)
    CALIBRATION_AREA_PROPORTION: list[float] = field(
        default_factory=defaults.CALIBRATION_AREA_PROPORTION.copy
    )  # [width, height] as proportion of screen used for calibration targets (e.g., 0.9 = 90% of screen)
    VALIDATION_AREA_PROPORTION: list[float] = field(
        default_factory=defaults.VALIDATION_AREA_PROPORTION.copy
    )  # [width, height] as proportion of screen used for validation targets

    # Target settings
    TARGET_TYPE: str = defaults.TARGET_TYPE  # "ABC", "AB", "A", "B", "C", "CIRCLE", or "IMAGE" (see docs)
    TARGET_IMAGE_PATH: str | None = defaults.TARGET_IMAGE_PATH  # Path to image file (for TARGET_TYPE="IMAGE")
    CAL_BACKGROUND_COLOR: tuple[int, int, int] = defaults.CAL_BACKGROUND_COLOR  # RGB background color for calibration

    # Fixation target settings (for A/B/C/AB/ABC types)
    FIXATION_CENTER_DIAMETER: float = defaults.FIXATION_CENTER_DIAMETER  # "A" component (deg visual angle)
    FIXATION_OUTER_DIAMETER: float = defaults.FIXATION_OUTER_DIAMETER  # "B" component (deg visual angle)
    FIXATION_CROSS_WIDTH: float = defaults.FIXATION_CROSS_WIDTH  # "C" component (deg visual angle)
    FIXATION_CENTER_COLOR: tuple[int, int, int, int] = defaults.FIXATION_CENTER_COLOR  # RGBA
    FIXATION_OUTER_COLOR: tuple[int, int, int, int] = defaults.FIXATION_OUTER_COLOR  # RGBA
    FIXATION_CROSS_COLOR: tuple[int, int, int, int] = defaults.FIXATION_CROSS_COLOR  # RGBA

    # Circle target settings (for TARGET_TYPE="CIRCLE")
    CIRCLE_OUTER_RADIUS: int = defaults.CIRCLE_OUTER_RADIUS  # Outer radius in pixels
    CIRCLE_INNER_RADIUS: int = defaults.CIRCLE_INNER_RADIUS  # Inner radius in pixels
    CIRCLE_OUTER_COLOR: tuple[int, int, int] = defaults.CIRCLE_OUTER_COLOR  # RGB
    CIRCLE_INNER_COLOR: tuple[int, int, int] = defaults.CIRCLE_INNER_COLOR  # RGB

    # Screen settings (ALL MEASUREMENTS IN MILLIMETERS)
    SCREEN_RES: list[int] = field(default_factory=defaults.SCREEN_RES.copy)  # [width, height] in pixels
    SCREEN_WIDTH: float = defaults.SCREEN_WIDTH  # Physical width in mm
    SCREEN_HEIGHT: float = defaults.SCREEN_HEIGHT  # Physical height in mm
    CAMERA_TO_SCREEN_DISTANCE: float = (
        defaults.CAMERA_TO_SCREEN_DISTANCE
    )  # Distance from camera to center of screen in mm
    VIEWING_DIST_TOP_BOTTOM: list[int] | None = field(
        default_factory=lambda: defaults.VIEWING_DIST_TOP_BOTTOM.copy() if defaults.VIEWING_DIST_TOP_BOTTOM else None
    )  # [top_mm, bottom_mm] for parser output (optional)
    REMOTE_LENS: int | None = defaults.REMOTE_LENS  # Remote mode lens focal length in mm (optional)

    # Display settings
    BACKEND: str = defaults.BACKEND  # Visualization backend: "pygame", "psychopy", or "pyglet"
    FULLSCREEN: bool = defaults.FULLSCREEN  # True for fullscreen window, False for windowed mode
    DISPLAY_INDEX: int = defaults.DISPLAY_INDEX  # Monitor index: 0=primary, 1=secondary, etc.

    # Tracking settings
    PUPIL_TRACKING_MODE: str = defaults.PUPIL_TRACKING_MODE  # "CENTROID" or "ELLIPSE"
    PUPIL_SIZE_MODE: str = defaults.PUPIL_SIZE_MODE  # 'AREA' or 'DIAMETER'
    HEURISTIC_FILTER: list[int] = field(
        default_factory=defaults.HEURISTIC_FILTER.copy
    )  # [link, file] (0=off, 1=normal, 2=extra)
    SET_HEURISTIC_FILTER: bool = (
        defaults.SET_HEURISTIC_FILTER
    )  # Activate filter or not (must be set every time recording starts)

    # Data filter settings
    FILE_EVENT_FILTER: str = defaults.FILE_EVENT_FILTER  # Which events to record to file
    LINK_EVENT_FILTER: str = defaults.LINK_EVENT_FILTER  # Which events to record over link
    LINK_SAMPLE_DATA: str = defaults.LINK_SAMPLE_DATA  # Sample fields over link
    FILE_SAMPLE_DATA: str = defaults.FILE_SAMPLE_DATA  # Sample fields to file

    # Recording settings
    RECORD_SAMPLES_TO_FILE: int = defaults.RECORD_SAMPLES_TO_FILE  # 1=on, 0=off
    RECORD_EVENTS_TO_FILE: int = defaults.RECORD_EVENTS_TO_FILE  # 1=on, 0=off
    RECORD_SAMPLE_OVER_LINK: int = defaults.RECORD_SAMPLE_OVER_LINK  # 1=on, 0=off
    RECORD_EVENT_OVER_LINK: int = defaults.RECORD_EVENT_OVER_LINK  # 1=on, 0=off

    # Hardware settings (not in defaults - specific to setup)
    ENABLE_SEARCH_LIMITS: str = defaults.ENABLE_SEARCH_LIMITS  # ON (default) or OFF
    ILLUMINATION_POWER: int = defaults.ILLUMINATION_POWER  # 'elcl_tt_power' setting: 1=100%, 2=75%, 3=50%
    HOST_IP: str = defaults.HOST_IP  # IP address of EyeLink Host PC

    # Physical setup configuration
    EL_CONFIGURATION: str = (
        defaults.EL_CONFIGURATION
    )  # Options: MTABLER, BTABLER, RTABLER, RBTABLER, AMTABLER, ARTABLER, BTOWER
    EYE_TRACKED: str = (
        defaults.EYE_TRACKED
    )  # BOTH/LEFT/RIGHT. Sets binocular_enabled=YES for both, or active_eye=LEFT/RIGHT for monocular

    def __post_init__(self) -> None:
        """Validate settings after initialization."""
        # Sampling rate validation
        if self.SAMPLE_RATE not in {250, 500, 1000, 2000}:
            raise ValueError(f"Invalid SAMPLE_RATE: {self.SAMPLE_RATE}. Must be one of: 250, 500, 1000, 2000")

        # Calibration targets validation
        if self.N_CAL_TARGETS not in {3, 5, 9, 13}:
            raise ValueError(f"Invalid N_CAL_TARGETS: {self.N_CAL_TARGETS}. Must be one of: 3, 5, 9, 13")

        # Screen resolution validation - must be list of 2 positive integers
        if not isinstance(self.SCREEN_RES, list) or len(self.SCREEN_RES) != 2:
            raise ValueError(f"SCREEN_RES must be a list of 2 integers, got: {self.SCREEN_RES}")
        if not all(isinstance(x, int) and x > 0 for x in self.SCREEN_RES):
            raise ValueError(f"SCREEN_RES values must be positive integers, got: {self.SCREEN_RES}")

        # Screen dimensions validation - must be positive non-zero values
        if self.SCREEN_WIDTH <= 0:
            raise ValueError(f"SCREEN_WIDTH must be positive, got: {self.SCREEN_WIDTH}")
        if self.SCREEN_HEIGHT <= 0:
            raise ValueError(f"SCREEN_HEIGHT must be positive, got: {self.SCREEN_HEIGHT}")

        # Camera to screen distance validation - must be positive non-zero
        if self.CAMERA_TO_SCREEN_DISTANCE <= 0:
            raise ValueError(f"CAMERA_TO_SCREEN_DISTANCE must be positive, got: {self.CAMERA_TO_SCREEN_DISTANCE}")

        # Viewing distance top/bottom validation - if provided, must have exactly 2 elements
        if self.VIEWING_DIST_TOP_BOTTOM is not None:
            if not isinstance(self.VIEWING_DIST_TOP_BOTTOM, list) or len(self.VIEWING_DIST_TOP_BOTTOM) != 2:
                raise ValueError(
                    f"VIEWING_DIST_TOP_BOTTOM must be None or a list of 2 numbers, got: {self.VIEWING_DIST_TOP_BOTTOM}"
                )
            if not all(isinstance(x, (int, float)) and x > 0 for x in self.VIEWING_DIST_TOP_BOTTOM):
                raise ValueError(
                    f"VIEWING_DIST_TOP_BOTTOM values must be positive numbers, got: {self.VIEWING_DIST_TOP_BOTTOM}"
                )

        # Calibration area proportion validation
        if not isinstance(self.CALIBRATION_AREA_PROPORTION, list) or len(self.CALIBRATION_AREA_PROPORTION) != 2:
            raise ValueError(
                f"CALIBRATION_AREA_PROPORTION must be a list of 2 numbers, got: {self.CALIBRATION_AREA_PROPORTION}"
            )
        if not (0 < self.CALIBRATION_AREA_PROPORTION[0] <= 1.0 and 0 < self.CALIBRATION_AREA_PROPORTION[1] <= 1.0):
            raise ValueError(
                f"CALIBRATION_AREA_PROPORTION values must be in (0, 1], got: {self.CALIBRATION_AREA_PROPORTION}"
            )

        # Validation area proportion validation
        if not isinstance(self.VALIDATION_AREA_PROPORTION, list) or len(self.VALIDATION_AREA_PROPORTION) != 2:
            raise ValueError(
                f"VALIDATION_AREA_PROPORTION must be a list of 2 numbers, got: {self.VALIDATION_AREA_PROPORTION}"
            )
        if not (0 < self.VALIDATION_AREA_PROPORTION[0] <= 1.0 and 0 < self.VALIDATION_AREA_PROPORTION[1] <= 1.0):
            raise ValueError(
                f"VALIDATION_AREA_PROPORTION values must be in (0, 1], got: {self.VALIDATION_AREA_PROPORTION}"
            )

        # Eye tracked validation
        if self.EYE_TRACKED not in {"Left", "Right", "Both"}:
            raise ValueError(f"Invalid EYE_TRACKED: {self.EYE_TRACKED}. Must be one of: 'Left', 'Right', 'Both'")

        # Pupil tracking mode validation
        if self.PUPIL_TRACKING_MODE not in {"CENTROID", "ELLIPSE"}:
            raise ValueError(
                f"Invalid PUPIL_TRACKING_MODE: {self.PUPIL_TRACKING_MODE}. Must be 'CENTROID' or 'ELLIPSE'"
            )

        # Pupil size mode validation
        if self.PUPIL_SIZE_MODE not in {"AREA", "DIAMETER"}:
            raise ValueError(f"Invalid PUPIL_SIZE_MODE: {self.PUPIL_SIZE_MODE}. Must be 'AREA' or 'DIAMETER'")

        # Heuristic filter validation
        if not isinstance(self.HEURISTIC_FILTER, list) or len(self.HEURISTIC_FILTER) != 2:
            raise ValueError(f"HEURISTIC_FILTER must be a list of 2 integers, got: {self.HEURISTIC_FILTER}")
        if not all(isinstance(x, int) and 0 <= x <= 2 for x in self.HEURISTIC_FILTER):
            raise ValueError(f"HEURISTIC_FILTER values must be integers 0-2, got: {self.HEURISTIC_FILTER}")

        # Illumination power validation
        if self.ILLUMINATION_POWER not in {1, 2, 3}:
            raise ValueError(
                f"Invalid ILLUMINATION_POWER: {self.ILLUMINATION_POWER}. Must be 1 (100%), 2 (75%), or 3 (50%)"
            )

        # Target type validation
        valid_target_types = {"ABC", "AB", "A", "B", "C", "CIRCLE", "IMAGE"}
        if self.TARGET_TYPE not in valid_target_types:
            raise ValueError(
                f"Invalid TARGET_TYPE: {self.TARGET_TYPE}. Must be one of: {', '.join(sorted(valid_target_types))}"
            )

        # Target image path validation
        if self.TARGET_TYPE == "IMAGE" and not self.TARGET_IMAGE_PATH:
            raise ValueError("TARGET_IMAGE_PATH must be provided when TARGET_TYPE is 'IMAGE'")

        # EyeLink configuration validation
        valid_configurations = {"MTABLER", "BTABLER", "RTABLER", "RBTABLER", "AMTABLER", "ARTABLER", "BTOWER"}
        if self.EL_CONFIGURATION not in valid_configurations:
            raise ValueError(
                f"Invalid EL_CONFIGURATION: {self.EL_CONFIGURATION}. "
                f"Must be one of: {', '.join(sorted(valid_configurations))}"
            )

        # RGB color validation helper
        def _validate_rgb_color(color: tuple, name: str) -> None:
            if not isinstance(color, tuple) or len(color) != 3:
                raise ValueError(f"{name} must be a tuple of 3 integers (R, G, B), got: {color}")
            if not all(isinstance(x, int) and 0 <= x <= 255 for x in color):
                raise ValueError(f"{name} values must be integers 0-255, got: {color}")

        # RGBA color validation helper
        def _validate_rgba_color(color: tuple, name: str) -> None:
            if not isinstance(color, tuple) or len(color) != 4:
                raise ValueError(f"{name} must be a tuple of 4 integers (R, G, B, A), got: {color}")
            if not all(isinstance(x, int) and 0 <= x <= 255 for x in color):
                raise ValueError(f"{name} values must be integers 0-255, got: {color}")

        # Validate RGBA color settings (fixation targets)
        _validate_rgba_color(self.FIXATION_CENTER_COLOR, "FIXATION_CENTER_COLOR")
        _validate_rgba_color(self.FIXATION_OUTER_COLOR, "FIXATION_OUTER_COLOR")
        _validate_rgba_color(self.FIXATION_CROSS_COLOR, "FIXATION_CROSS_COLOR")

        # Validate RGB color settings (circle targets and calibration)
        _validate_rgb_color(self.CIRCLE_OUTER_COLOR, "CIRCLE_OUTER_COLOR")
        _validate_rgb_color(self.CIRCLE_INNER_COLOR, "CIRCLE_INNER_COLOR")
        _validate_rgb_color(self.CAL_BACKGROUND_COLOR, "CAL_BACKGROUND_COLOR")

        # Validate fixation target dimensions (must be positive)
        if self.FIXATION_CENTER_DIAMETER <= 0:
            raise ValueError(f"FIXATION_CENTER_DIAMETER must be positive, got: {self.FIXATION_CENTER_DIAMETER}")
        if self.FIXATION_OUTER_DIAMETER <= 0:
            raise ValueError(f"FIXATION_OUTER_DIAMETER must be positive, got: {self.FIXATION_OUTER_DIAMETER}")
        if self.FIXATION_CROSS_WIDTH <= 0:
            raise ValueError(f"FIXATION_CROSS_WIDTH must be positive, got: {self.FIXATION_CROSS_WIDTH}")

        # Validate circle target dimensions (must be positive)
        if self.CIRCLE_OUTER_RADIUS <= 0:
            raise ValueError(f"CIRCLE_OUTER_RADIUS must be positive, got: {self.CIRCLE_OUTER_RADIUS}")
        if self.CIRCLE_INNER_RADIUS <= 0:
            raise ValueError(f"CIRCLE_INNER_RADIUS must be positive, got: {self.CIRCLE_INNER_RADIUS}")
        if self.CIRCLE_INNER_RADIUS >= self.CIRCLE_OUTER_RADIUS:
            raise ValueError(
                f"CIRCLE_INNER_RADIUS ({self.CIRCLE_INNER_RADIUS}) must be less than "
                f"CIRCLE_OUTER_RADIUS ({self.CIRCLE_OUTER_RADIUS})"
            )

        # Remote lens validation (optional)
        if self.REMOTE_LENS is not None and self.REMOTE_LENS <= 0:
            raise ValueError(f"REMOTE_LENS must be positive or None, got: {self.REMOTE_LENS}")

        # Backend validation
        valid_backends = {"pygame", "psychopy", "pyglet"}
        if self.BACKEND not in valid_backends:
            raise ValueError(f"Invalid BACKEND: {self.BACKEND}. Must be one of: {', '.join(sorted(valid_backends))}")

        # Display index validation (must be non-negative integer)
        if not isinstance(self.DISPLAY_INDEX, int) or self.DISPLAY_INDEX < 0:
            raise ValueError(f"DISPLAY_INDEX must be a non-negative integer, got: {self.DISPLAY_INDEX}")

    def to_dict(self) -> dict[str, Any]:
        """Convert settings to a dictionary.

        Returns:
            Dictionary containing all settings values

        """
        return asdict(self)

    def save_to_file(self, filepath: str | Path) -> None:
        """Save settings to a JSON file.

        Args:
            filepath: Path to save the configuration file

        Example:
            >>> settings = Settings(SAMPLE_RATE=500, SCREEN_RES=[1920, 1080])
            >>> settings.save_to_file("my_config.json")

        """
        filepath = Path(filepath)
        config_dict = self.to_dict()

        # Ensure parent directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with filepath.open("w") as f:
            json.dump(config_dict, f, indent=2)

        logger.info("Settings saved to %s", filepath)

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> Self:
        """Create Settings instance from a dictionary.

        Args:
            config_dict: Dictionary containing settings values

        Returns:
            New Settings instance with values from the dictionary

        """
        # Convert list color values back to tuples (JSON doesn't preserve tuples)
        # RGBA fields (fixation targets) - convert RGB to RGBA by adding alpha=255
        rgba_fields = [
            "FIXATION_CENTER_COLOR",
            "FIXATION_OUTER_COLOR",
            "FIXATION_CROSS_COLOR",
        ]
        # RGB fields (circle targets, calibration background) - keep as RGB
        rgb_fields = [
            "CIRCLE_OUTER_COLOR",
            "CIRCLE_INNER_COLOR",
            "CAL_BACKGROUND_COLOR",
        ]

        processed_dict = config_dict.copy()

        # Convert RGBA fields (accept 3-tuple and add alpha, or keep 4-tuple)
        for field_name in rgba_fields:
            if field_name in processed_dict and isinstance(processed_dict[field_name], list):
                if len(processed_dict[field_name]) == 3:
                    processed_dict[field_name] = (*tuple(processed_dict[field_name]), 255)
                else:
                    processed_dict[field_name] = tuple(processed_dict[field_name])

        # Convert RGB fields (must be 3-tuple)
        for field_name in rgb_fields:
            if field_name in processed_dict and isinstance(processed_dict[field_name], list):
                processed_dict[field_name] = tuple(processed_dict[field_name])

        return cls(**processed_dict)

    @classmethod
    def load_from_file(cls, filepath: str | Path) -> Self:
        """Load settings from a JSON file.

        Args:
            filepath: Path to the configuration file

        Returns:
            New Settings instance with values from the file

        Raises:
            FileNotFoundError: If the configuration file doesn't exist
            ValueError: If the file contains invalid configuration values

        Example:
            >>> settings = Settings.load_from_file("my_config.json")

        """
        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"Configuration file not found: {filepath}")

        with filepath.open("r") as f:
            config_dict = json.load(f)

        logger.info("Settings loaded from %s", filepath)
        return cls.from_dict(config_dict)


class _MinimalAlertHandler(pylink.EyeLinkCustomDisplay):
    """Minimal alert handler for EyeLink connection phase.

    This provides the bare minimum implementation needed to handle alerts
    during tracker connection. Used internally before full calibration display.
    """

    def alert_printf(self, msg: str) -> None:  # noqa: PLR6301
        """Display alert message.

        Args:
            msg: Alert message to display

        Note:
            Must be instance method to override pylink.EyeLinkCustomDisplay.

        """
        logger.warning("EyeLink alert: %s", msg)


def _cleanup_on_exit() -> None:
    """Clean up graphics on exit.

    Closes any open pylink graphics connections. Used for cleanup before
    program termination.
    """
    with contextlib.suppress(Exception):
        pylink.closeGraphics()


class EyeLink:  # noqa: PLR0904
    """Unified EyeLink tracker interface with integrated display management.

    This class provides a complete interface for interacting with SR Research
    EyeLink eye trackers. It combines hardware connection, display window management,
    recording, data access, and configuration in a single unified class.

    The tracker creates and owns the display window throughout the experiment.
    Users can access the window directly via tracker.window (Option A) or use
    backend-agnostic helper methods (Option B).

    Graceful shutdown: Press Ctrl+C at any time (including during calibration)
    to automatically stop recording, close the window, save data, and disconnect.

    This class uses two-phase initialization to separate object construction
    from I/O operations:
    - __init__: Sets up the object state (no side effects)
    - connect(): Performs network connection, file operations, and creates display window

    Example:
        settings = Settings(BACKEND='pygame', FULLSCREEN=True)
        tracker = EyeLink(settings)  # Auto-connects and creates window

        # Option A: Direct window access
        tracker.window.fill((128, 128, 128))
        tracker.flip()

        # Option B: Backend-agnostic helpers
        tracker.fill((128, 128, 128))
        tracker.display.draw_text("Fixate", center=True)
        tracker.flip()

        # Ctrl+C at any point will gracefully shut down and save data

    Dummy mode (for testing without hardware):
        settings = Settings(BACKEND='pygame', HOST_IP='dummy')
        tracker = EyeLink(settings)  # Creates window in dummy mode
        # Full window functionality available for development/testing

    Or use two-phase initialization:
        tracker = EyeLink(settings, auto_connect=False)
        tracker.connect()  # Connect and create window when ready

    Or use as a context manager:
        with EyeLink(settings) as tracker:
            # use tracker and window
            pass  # auto-cleanup

    """

    def __init__(
        self,
        settings: Settings,
        record_raw_data: bool = False,
        sample_buffer_length: int = 0,
        use_sample_buffer: bool = False,
        read_from_eyelink_buffer: bool = True,
        event_buffer_length: int = 0,
        auto_connect: bool = True,
    ) -> None:
        """Initialize EyeLink tracker interface.

        Args:
            settings: Settings object with tracker configuration
            record_raw_data: Set to True to record pupil/CR (raw) data
            sample_buffer_length: Store samples in buffer if you need more than the latest
            use_sample_buffer: Store data from buffer in RingBuffer
            read_from_eyelink_buffer: Use getNextData() instead of getNewestSample()
                                     (the former draws from an internal buffer and should miss fewer samples)
            event_buffer_length: Store events in buffer if you need more than the latest
            auto_connect: If True, automatically connect during initialization.
                         If False, you must call connect() manually (two-phase initialization).

        """
        self.settings = settings
        self.record_raw_data = record_raw_data

        # Hardware connection state
        self.tracker: pylink.EyeLink | None = None
        self.realconnect = False
        self.edfname = settings.FILENAME + ".edf"
        self._alert_handler: object | None = None

        # Store initialization parameters for deferred setup
        self._sample_buffer_length = sample_buffer_length
        self._use_sample_buffer = use_sample_buffer
        self._read_from_eyelink_buffer = read_from_eyelink_buffer
        self._event_buffer_length = event_buffer_length

        # Component initialization state
        self._connected = False
        self._cleaned_up = False
        self._is_recording = False

        # Components (will be initialized in connect())
        self.data = None
        self.events = None
        self.display = None

        # Store data save path for Ctrl+C cleanup
        self._data_save_path = settings.FILEPATH or "./"

        # Connect immediately if auto_connect is True
        if auto_connect:
            self.connect()

        # Register end_experiment with atexit for automatic cleanup
        atexit.register(lambda: self.end_experiment(self._data_save_path))

        # Set up Ctrl+C signal handler for graceful shutdown
        # This handles both terminal focus (SIGINT) and window focus (called by display backends)
        signal.signal(signal.SIGINT, self._signal_handler)

    def set_data_save_path(self, path: str) -> None:
        """Update the path where EDF file will be saved on cleanup.

        This path is used when Ctrl+C is pressed or when end_experiment() is called
        without a path argument.

        Args:
            path: Directory path where EDF file should be saved (include trailing slash)

        Example:
            tracker.set_data_save_path("./data/session1/")

        """
        self._data_save_path = path
        logger.info("Data save path updated to: %s", path)

    def _signal_handler(self, signum: int, frame: object) -> None:  # noqa: ARG002
        """Handle Ctrl+C for graceful shutdown.

        This handler is called in two scenarios:
        1. Terminal has focus: OS sends SIGINT signal
        2. Window has focus: Display backend detects Ctrl+C and calls this directly

        Ensures that pressing Ctrl+C at any point during the experiment
        (including during calibration) will:
        1. Stop recording if active
        2. Close the display window
        3. Save the EDF file to the configured path
        4. Disconnect from the tracker
        5. Exit the program

        Args:
            signum: Signal number (SIGINT) or None if called by display backend
            frame: Current stack frame (unused) or None if called by display backend

        """
        logger.critical("Ctrl+C detected - shutting down gracefully...")
        self.end_experiment(self._data_save_path)
        logger.critical("Cleanup complete. Exiting.")
        os._exit(0)

    def connect(self) -> None:
        """Connect to tracker and initialize all components.

        This method performs all I/O operations including:
        - Network connection to tracker (or dummy mode if HOST_IP is None/'dummy')
        - Opening the EDF data file
        - Setting tracker to offline mode
        - Initializing data buffers and event processors
        - Configuring tracker settings
        - Creating display window (works in both real and dummy mode)

        Call this manually if auto_connect=False was used.
        """
        if self._connected:
            logger.warning("Already connected")
            return

        # Set up minimal alert handler BEFORE connecting
        self._alert_handler = _MinimalAlertHandler()
        with contextlib.suppress(RuntimeError):
            pylink.openGraphicsEx(self._alert_handler)

        logger.info("Connecting to EyeLink...")

        # Dummy mode if explicitly requested
        if self.settings.HOST_IP is None or str(self.settings.HOST_IP).lower() == "dummy":
            logger.info("Using EyeLink in dummy mode (settings.HOST_IP is None or 'dummy')")
            self.tracker = pylink.EyeLink(None)
            self.realconnect = False
        else:
            try:
                self.tracker = pylink.EyeLink(trackeraddress=self.settings.HOST_IP)
                # Check if connection actually succeeded
                if self.tracker is not None:
                    try:
                        is_connected = self.tracker.isConnected()
                    except Exception:
                        is_connected = False
                else:
                    is_connected = False
            except RuntimeError:
                # User-facing troubleshooting messages - not exception logging
                logger.error("ERROR: Could not connect to EyeLink tracker!")  # noqa: TRY400
                logger.error("Current Host PC IP setting: %s", self.settings.HOST_IP)  # noqa: TRY400
                logger.error("Please check:")  # noqa: TRY400
                logger.error("  1. EyeLink Host PC is powered on")  # noqa: TRY400
                logger.error("  2. Ethernet cable is connected")  # noqa: TRY400
                logger.error("  3. Host PC IP address matches settings.HOST_IP")  # noqa: TRY400
                logger.error("  4. Your computer's IP is on the same subnet (e.g., 100.1.1.2)")  # noqa: TRY400
                logger.error("Cleaning up and exiting...")  # noqa: TRY400
                _cleanup_on_exit()
                sys.exit(1)
            except Exception:
                logger.exception("Unexpected error while connecting to EyeLink")
                logger.error("Cleaning up and exiting...")  # noqa: TRY400
                _cleanup_on_exit()
                sys.exit(1)

            if self.tracker is not None and is_connected:
                self.realconnect = True
                logger.info("Successfully connected to EyeLink at %s", self.settings.HOST_IP)
            else:
                logger.error("Failed to connect to EyeLink at %s (unknown error)", self.settings.HOST_IP)
                _cleanup_on_exit()
                sys.exit(1)

        # Close the minimal alert handler graphics
        with contextlib.suppress(Exception):
            pylink.closeGraphics()

        if self.realconnect:
            # Stop tracking if tracker is running (safety measure)
            with contextlib.suppress(Exception):
                self.tracker.stopRecording()

        # Flush keyboard queue and set tracker to offline mode
        pylink.flushGetkeyQueue()
        self.tracker.setOfflineMode()

        # Open EDF data file
        self._open_data_file()

        # Initialize data buffer
        self.data = DataBuffer(
            self,
            buffer_length=self._sample_buffer_length,
            use_buffer=self._use_sample_buffer,
            read_from_tracker_buffer=self._read_from_eyelink_buffer,
            record_raw_data=self.record_raw_data,
        )

        # Initialize event processor
        self.events = EventProcessor(self, buffer_length=self._event_buffer_length)

        # Which eye should be tracked?
        self._select_eye(eye_tracked=self.settings.EYE_TRACKED)

        # Override default settings
        self._set_all_constants()

        # Setup the EDF-file such that it adds 'raw' data
        self._setup_raw_data_recording(enable=self.record_raw_data)

        # Create display window (works in both real and dummy mode)
        mode_str = "dummy mode" if not self.realconnect else "real tracker"
        logger.info("Creating %s display window (%s)...", self.settings.BACKEND, mode_str)
        self.display = self._create_display(self.settings.BACKEND)
        logger.info("Display window created on monitor %d", self.settings.DISPLAY_INDEX)

        self._connected = True
        logger.info("EyeLink connected and configured")

    def _ensure_connected(self) -> None:
        """Ensure tracker is connected, raise error if not.

        Raises:
            RuntimeError: If tracker is not connected

        """
        if self.tracker is None:
            raise RuntimeError("Tracker not connected. Call connect() first or use auto_connect=True in __init__")

    def disconnect(self) -> None:
        """Close the connection to the tracker."""
        if self.tracker is not None:
            with contextlib.suppress(Exception):
                self.tracker.close()
            self.tracker = None

    def is_connected(self) -> bool:
        """Check if connected to tracker.

        Returns:
            True if connected to real tracker, False otherwise

        """
        return self.tracker is not None and self.realconnect

    def __enter__(self) -> Self:
        """Enable use as a context manager."""
        if not self._connected:
            self.connect()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        """Ensure tracker is cleaned up on context exit."""
        self.end_experiment(self.settings.FILEPATH or "./")

    def __del__(self) -> None:
        """Ensure tracker is cleaned up on deletion (safety net)."""
        with contextlib.suppress(Exception):
            self.end_experiment(self.settings.FILEPATH or "./")

    def _create_display(self, backend_name: str) -> object:
        """Create display window based on backend name.

        Uses lazy importing to only load the backend that's actually installed.

        Args:
            backend_name: Backend identifier ("pygame", "psychopy", or "pyglet")

        Returns:
            Display instance (PygameDisplay, PsychopyDisplay, or PygletDisplay)

        Raises:
            ImportError: If backend not installed
            ValueError: If backend name invalid

        """
        if backend_name == "pygame":
            from .display.pygame_display import PygameDisplay  # noqa: PLC0415

            return PygameDisplay(self.settings, shutdown_handler=self._signal_handler)
        if backend_name == "psychopy":
            from .display.psychopy_display import PsychopyDisplay  # noqa: PLC0415

            return PsychopyDisplay(self.settings, shutdown_handler=self._signal_handler)
        if backend_name == "pyglet":
            from .display.pyglet_display import PygletDisplay  # noqa: PLC0415

            return PygletDisplay(self.settings, shutdown_handler=self._signal_handler)
        raise ValueError(
            f"Invalid backend: {backend_name}. Must be 'pygame', 'psychopy', or 'pyglet'. "
            f"Install with: uv pip install -e '.[{backend_name}]'"
        )

    @property
    def window(self) -> object:
        """Get raw backend window object for direct access (Option A).

        Returns:
            Backend-specific window:
            - pygame: pygame.Surface
            - psychopy: psychopy.visual.Window
            - pyglet: pyglet.window.Window

        Example:
            # Direct pygame access
            tracker.window.fill((128, 128, 128))
            tracker.window.blit(my_surface, (x, y))

        """
        if self.display is None:
            raise RuntimeError("Display not created. Call connect() first or use auto_connect=True in __init__")
        return self.display.window

    def flip(self) -> None:
        """Update display to show drawn content.

        Convenience method that delegates to display.flip().
        """
        if self.display is not None:
            self.display.flip()

    def fill(self, color: tuple[int, int, int]) -> None:
        """Fill window with specified RGB color.

        Convenience method that delegates to display.fill().

        Args:
            color: RGB tuple (0-255, 0-255, 0-255)

        """
        if self.display is not None:
            self.display.fill(color)

    def clear(self) -> None:
        """Clear window to black.

        Convenience method that delegates to display.clear().
        """
        if self.display is not None:
            self.display.clear()

    def wait_for_key(self, key: str | None = None, timeout: float | None = None) -> str | None:
        """Wait for keyboard input (Option B helper).

        Args:
            key: Specific key to wait for (e.g., 'space', 'return'), or None for any key
            timeout: Maximum time to wait in seconds, or None to wait indefinitely

        Returns:
            Key name that was pressed, or None if timeout

        Example:
            tracker.show_message("Press SPACE to continue")
            tracker.wait_for_key('space')

        """
        if self.display is not None:
            return self.display.wait_for_key(key, timeout)
        return None

    def wait(self, duration: float) -> None:
        """Wait for specified duration while handling UI events.

        Prevents event queue buildup during delays.

        Args:
            duration: Time to wait in seconds

        Example:
            tracker.show_message("Get ready...")
            tracker.wait(2.0)

        """
        if self.display is not None:
            self.display.wait(duration)

    def show_message(
        self,
        text: str,
        duration: float | None = None,
        bg_color: tuple[int, int, int] = (128, 128, 128),
        text_color: tuple[int, int, int] = (255, 255, 255),
        text_size: int = 32,
    ) -> None:
        """Display text message centered on screen (Option B helper).

        Args:
            text: Message to display
            duration: Time to display in seconds, or None to display without waiting
            bg_color: Background RGB color (default: gray (128, 128, 128))
            text_color: Text RGB color (default: white (255, 255, 255))
            text_size: Font size in points (default: 32)

        Example:
            tracker.show_message("Press SPACE when ready")
            tracker.wait_for_key('space')

            # Or with auto-wait:
            tracker.show_message("Get ready...", duration=2.0)

            # Custom colors:
            tracker.show_message(
                "Error!",
                bg_color=(255, 0, 0),  # Red background
                text_color=(255, 255, 255),  # White text
                text_size=48
            )

        """
        if self.display is not None:
            self.display.fill(bg_color)
            self.display.draw_text(text, center=True, size=text_size, color=text_color)
            self.display.flip()
            if duration is not None:
                self.wait(duration)

    def run_trial(
        self,
        draw_func: object,
        trial_data: dict | None = None,
        duration: float | None = None,
        record: bool = True,
        on_ui_event: object | None = None,
    ) -> dict:
        """Run a trial with automatic recording and event handling (Option B helper).

        This is a structured trial runner that handles the common pattern:
        start recording → draw loop → handle events → stop recording.

        Args:
            draw_func: Function that draws the trial. Called as `draw_func(window, trial_data)`.
                      Should draw but NOT flip - flipping happens automatically.
            trial_data: Optional dict passed to draw_func
            duration: Maximum trial duration in seconds, or None for unlimited
            record: If True, start/stop recording automatically
            on_ui_event: Optional callback for UI events. Called as `on_ui_event(event_dict, trial_data)`.
                        UI events = keyboard/mouse, NOT eye-tracking events.
                        Return True to end trial early.

        Returns:
            dict with keys:
                - 'duration': Actual trial duration in seconds
                - 'ui_events': List of UI event dicts that occurred
                - 'ended_by': 'duration', 'callback', or 'escape'

        Example:
            def draw_stimulus(window, data):
                # window is raw backend window (Option A access within callback)
                window.fill((128, 128, 128))
                # ... draw your stimulus ...

            def handle_response(event, data):
                if event['type'] == 'keydown' and event['key'] == 'space':
                    data['response_time'] = time.time() - data['trial_start']
                    return True  # End trial
                return False

            trial_data = {'trial_start': time.time(), 'stimulus': 'image.png'}
            result = tracker.run_trial(
                draw_func=draw_stimulus,
                trial_data=trial_data,
                duration=5.0,
                on_ui_event=handle_response
            )

        """
        if self.display is None:
            raise RuntimeError("Display not created. Call connect() first")

        start_time = time.time()
        ui_events = []
        ended_by = "duration"

        if trial_data is None:
            trial_data = {}

        if record:
            self.start_recording()

        try:
            while True:
                # Draw
                draw_func(self.window, trial_data)
                self.flip()

                # Handle UI events (keyboard/mouse)
                events = self.display.get_events()
                for event in events:
                    ui_events.append(event)

                    # Check for escape key
                    if event.get("type") == "keydown" and event.get("key") in {"escape", "esc"}:
                        ended_by = "escape"
                        break

                    # Call user callback
                    if on_ui_event is not None:
                        should_end = on_ui_event(event, trial_data)
                        if should_end:
                            ended_by = "callback"
                            break

                if ended_by != "duration":
                    break

                # Check duration
                if duration is not None and (time.time() - start_time) >= duration:
                    break

                time.sleep(0.001)

        finally:
            if record:
                self.stop_recording()

        return {
            "duration": time.time() - start_time,
            "ui_events": ui_events,
            "ended_by": ended_by,
        }

    def send_command(self, command: str) -> None:
        """Send a command to the EyeLink tracker.

        Commands configure tracker behavior but are not recorded in the data file.

        Args:
            command: Command to send

        """
        self._ensure_connected()
        self.tracker.sendCommand(command)

    def send_message(self, message: str) -> None:
        """Send a message to the tracker that is recorded in the EDF.

        Messages are timestamped annotations in the data file, useful for marking
        events during recording (trial starts, stimulus onsets, responses, etc.).

        Args:
            message: Message to send

        """
        self._ensure_connected()
        self.tracker.sendMessage(message)

    def get_tracker_version(self) -> int:
        """Get the tracker version as an integer.

        Returns:
            Tracker version as int, or 0 if not connected or parsing fails

        """
        self._ensure_connected()
        try:
            return int(self.tracker.getTrackerVersion())
        except Exception:
            return 0

    def set_offline_mode(self) -> None:
        """Set tracker to offline mode."""
        self._ensure_connected()
        self.tracker.setOfflineMode()

    def stop_recording(self) -> None:
        """Stop recording."""
        if self.record_raw_data:
            self.data.stop_raw_thread()
            self._disable_realtime_mode()

        self.data.stop_sample_thread()
        self.events.stop_event_thread()

        self._stop_recording()

    def _stop_recording(self) -> None:
        """Stop recording data (internal method)."""
        if not self._is_recording:
            return

        self._ensure_connected()
        self.tracker.stopRecording()
        self._is_recording = False
        logger.info("Recording stopped")

    def eye_available(self) -> int:
        """Get which eye is being tracked.

        Returns:
            0=left, 1=right, 2=binocular, -1 if not available

        """
        self._ensure_connected()
        return self.tracker.eyeAvailable()

    def get_newest_sample(self) -> object | None:
        """Get the newest sample from the tracker.

        Returns:
            Sample object or None

        """
        self._ensure_connected()
        return self.tracker.getNewestSample()

    def get_next_data(self) -> int:
        """Get next data type from the tracker buffer.

        Returns:
            Data type code (200=sample, 4=blink, 8=fixation, 0x3F/0=no data)

        """
        self._ensure_connected()
        return self.tracker.getNextData()

    def get_float_data(self) -> object | None:
        """Get float data from tracker buffer.

        Returns:
            Data object or None

        """
        self._ensure_connected()
        return self.tracker.getFloatData()

    def set_calibration_type(self, cal_type: str) -> None:
        """Set calibration type.

        Args:
            cal_type: Calibration type string (e.g., 'HV9', 'HV13')

        """
        self._ensure_connected()
        self.tracker.setCalibrationType(cal_type)

    def set_auto_calibration_pacing(self, pacing_ms: int) -> None:
        """Set automatic calibration pacing interval.

        Args:
            pacing_ms: Pacing interval in milliseconds

        """
        self._ensure_connected()
        self.tracker.setAutoCalibrationPacing(pacing_ms)

    def do_tracker_setup(self, width: int, height: int) -> None:
        """Enter tracker setup/calibration mode.

        Args:
            width: Screen width in pixels
            height: Screen height in pixels

        """
        self._ensure_connected()
        self.tracker.doTrackerSetup(width, height)

    def draw_text(self, text: str, position: tuple[float, float]) -> None:
        """Draw text on the tracker display.

        Args:
            text: Text to display
            position: (x, y) position tuple

        """
        self._ensure_connected()
        self.tracker.drawText(text, position)

    def calibrate(self, record_samples: bool = False) -> None:
        """Calibrate eye-tracker using internal display window.

        Creates calibration display automatically based on settings.BACKEND
        and uses the tracker's internal window (tracker.display.window).

        Args:
            record_samples: Record samples during calibration and validation

        Example:
            tracker = EyeLink(settings)
            tracker.calibrate()  # No window parameter needed

        """
        # Create calibration display using internal window
        calibration_display = create_calibration(self.settings, self)

        # Set the tracker on the calibration display to self (which has the pylink tracker)
        calibration_display.set_tracker(self)

        if self.realconnect:
            # Set calibration type
            calst = f"HV{self.settings.N_CAL_TARGETS}"
            self.set_calibration_type(calst)

            # Set calibration pacing
            self.set_auto_calibration_pacing(self.settings.PACING_INTERVAL)

            # Execute custom calibration display
            # Try to open graphics, but skip if already open (for subsequent calibrations)
            try:
                pylink.openGraphicsEx(calibration_display)
            except RuntimeError as e:
                if "previous EyeLinkCustomDisplay is active" in str(e):
                    # Graphics already open from previous calibration, continue
                    pass
                else:
                    # Different error, re-raise it
                    raise

            # Record samples during calibration and validation and store in edf file
            if record_samples:
                if self.record_raw_data:
                    self.send_command("sticky_mode_data_enable DATA = 1 1 1 1")
                else:
                    self.send_command("sticky_mode_data_enable DATA = 1 1 0 0")

            # Calibrate
            self.do_tracker_setup(self.settings.SCREEN_RES[0], self.settings.SCREEN_RES[1])

            # Stop sending samples
            if record_samples:
                self.send_command("sticky_mode_data_enable")
                self.send_command("set_idle_mode")
                time.sleep(0.1)  # Wait to finish mode transition

                # sticky_mode_data_enable is only switched off when there is an actual
                # mode change. The above set_idle_mode is a no-op as the tracker is
                # already offline at that point. If sticky mode is not switched off
                # properly, we end up with junk samples in a small bit of the edf file,
                # overwriting part of the next trial
                self.send_command("setup_menu_mode")
                time.sleep(0.1)  # Wait to finish mode transition
                self.send_command("set_idle_mode")
                time.sleep(0.1)  # Wait to finish mode transition
        # Dummy mode - call dummynote if available
        elif hasattr(calibration_display, "dummynote"):
            calibration_display.dummynote()

    def start_recording(self, sendlink: bool = False) -> None:
        """Start recording. Waits 50ms to allow EyeLink to prepare.

        Args:
            sendlink: Toggle for sending eye data over the link to display computer during recording

        Note:
            heuristic_filter needs to be set each time recording starts as it is reset at
            recording stop according to the manual. It's on per default.

        """
        self._start_recording(sendlink=sendlink, record_raw_data=self.record_raw_data)

        if self.record_raw_data:
            self._enable_raw_data(do_enable=True)
            self._enable_realtime_mode()
            self.data.start_raw_thread()

        if self.data.use_buffer:
            self.data.start_sample_thread()

    def _start_recording(self, sendlink: bool = False, record_raw_data: bool = False) -> None:
        """Start recording data to EDF file (internal method).

        Args:
            sendlink: Toggle for sending eye data over the link during recording
            record_raw_data: Whether raw pupil/CR data is being recorded

        Note:
            heuristic_filter needs to be set each time recording starts as it is
            reset at recording stop according to the manual.

        """
        if self._is_recording:
            logger.warning("Recording already started")
            return

        self._ensure_connected()

        if self.settings.SET_HEURISTIC_FILTER:
            cstr = f"heuristic_filter {self.settings.HEURISTIC_FILTER[0]} {self.settings.HEURISTIC_FILTER[1]}"
            self.send_command(cstr)

        self.send_command("set_idle_mode")
        time.sleep(0.05)

        if record_raw_data:
            sendlink = True

        if sendlink:
            self.tracker.startRecording(1, 1, 1, 1)
        else:
            self.tracker.startRecording(1, 1, 0, 0)

        self._is_recording = True
        logger.info("Recording started")

    def end_experiment(self, spath: str | None = None) -> None:
        """Comprehensive cleanup: stop recording, save EDF, and disconnect.

        This is the single cleanup method that ensures all resources are properly
        cleaned up and the EDF file is saved. Called automatically on exit, on Ctrl+C,
        or can be called explicitly by the user.

        Works at any point during the experiment, including during calibration.

        WARNING: Don't retrieve a file using PsychoPy. Start exp program from cmd
        otherwise file transfer can be very slow.

        Args:
            spath: File path of where to save EDF file (include trailing slash).
                   If None, uses the path stored during initialization.

        """
        # Use stored path if not provided
        if spath is None:
            spath = self._data_save_path
        # Prevent duplicate cleanup
        if self._cleaned_up:
            return
        self._cleaned_up = True

        # Only cleanup if we were connected
        if not self._connected or self.tracker is None:
            return

        logger.info("Experiment cleanup and EDF file transfer...")

        # Stop recording if active
        with contextlib.suppress(Exception):
            self.stop_recording()

        # Shutdown data and events buffers
        with contextlib.suppress(Exception):
            if self.data is not None:
                self.data.shutdown()
        with contextlib.suppress(Exception):
            if self.events is not None:
                self.events.shutdown()

        # Close display window
        with contextlib.suppress(Exception):
            if self.display is not None:
                self.display.close()
                logger.info("Display window closed")

        # Transfer EDF file (most important - always try to save data)
        with contextlib.suppress(Exception):
            self._transfer_data_file(spath)
            logger.info("EDF file transferred to: %s", spath)

        # Disconnect from tracker
        with contextlib.suppress(Exception):
            self.disconnect()

        self.tracker = None
        self._connected = False

        logger.info("Experiment cleanup complete")

    # Recording management methods (from recorder.py)

    def _open_data_file(self) -> None:
        """Open EDF data file on the tracker."""
        self._ensure_connected()
        self.tracker.openDataFile(self.edfname)
        logger.info("Data file opened: %s", self.edfname)

    def is_recording(self) -> bool:
        """Check if currently recording.

        Returns:
            True if recording, False otherwise

        """
        return self._is_recording

    def _close_data_file(self) -> None:
        """Close the EDF data file on the tracker."""
        self._ensure_connected()
        self.tracker.closeDataFile()
        logger.info("Data file closed")

    def _transfer_data_file(self, save_path: str) -> None:
        """Transfer EDF file from tracker to display computer.

        WARNING: Don't retrieve a file using PsychoPy. Start exp program from cmd
        otherwise file transfer can be very slow.

        Args:
            save_path: Directory path where the EDF file will be saved (include trailing slash)

        """
        self._ensure_connected()

        # Generate file path
        fpath = save_path + self.edfname

        # Set tracker to offline mode
        self.set_offline_mode()
        time.sleep(0.5)

        # Close the file
        self._close_data_file()
        time.sleep(1)

        # Transfer file
        logger.info("Receiving data file: %s -> %s", self.edfname, fpath)
        self.tracker.receiveDataFile(self.edfname, fpath)
        logger.info("Data file transfer complete")

    def set_status_message(self, message: str) -> None:
        """Set status message to appear on host's screen while recording.

        Args:
            message: Text to send (must be < 80 characters)

        """
        msg = f"record_status_message '{message}'"
        self.send_command(msg)

    def set_trial_id(self, idval: int = 1) -> None:
        """Send message indicating start of trial in EDF.

        Args:
            idval: Value to set for TRIALID

        """
        tid = f"TRIALID {idval}"
        self.send_message(tid)

    def set_trial_result(self, rval: float | str = 0, scrcol: int = 0) -> None:
        """Send trial result to indicate trial end in EDF.

        Also clears the screen on EyeLink Display.

        Args:
            rval: Value to set for TRIAL_RESULT
            scrcol: Color to clear screen to (defaults to black)

        """
        trmsg = f"TRIAL_RESULT {rval}"
        cscmd = f"clear_screen {scrcol}"

        self.send_message(trmsg)
        self.send_command(cscmd)

    # Configuration methods (from config.py)

    def _build_screen_phys_coords_command(self, use_equals: bool = False) -> str:
        """Build screen physical coordinates command string.

        Args:
            use_equals: If True, include '=' in command format

        Returns:
            Command string with screen physical coordinates in mm
            Format: "screen_phys_coords [=] left top right bottom"

        Note:
            SCREEN_WIDTH and SCREEN_HEIGHT are already in mm

        """
        left = -self.settings.SCREEN_WIDTH / 2.0
        top = self.settings.SCREEN_HEIGHT / 2.0
        right = self.settings.SCREEN_WIDTH / 2.0
        bottom = -self.settings.SCREEN_HEIGHT / 2.0
        separator = " = " if use_equals else " "
        return f"screen_phys_coords{separator}{left} {top} {right} {bottom}"

    def _select_eye(self, eye_tracked: str = "both") -> None:
        """Select eye to track.

        Args:
            eye_tracked: 'both', 'left', or 'right'

        """
        if "BOTH" in eye_tracked.upper():
            self.send_command("binocular_enabled = YES")
        else:
            self.send_command("binocular_enabled = NO")
            self.send_command("active_eye = " + eye_tracked.upper())

    def _set_all_constants(self) -> None:
        """Override values in final.ini to ensure proper settings are used.

        Values are imported from Settings object.
        """
        sres = self.settings.SCREEN_RES

        # Set illumination power
        self.send_command("elcl_tt_power " + str(self.settings.ILLUMINATION_POWER))

        # Set display coords for dataviewer
        disptxt = f"DISPLAY_COORDS 0 0 {sres[0] - 1} {sres[1] - 1}"
        self.send_message(disptxt)

        scrtxt = f"screen_pixel_coords 0 0 {sres[0] - 1} {sres[1] - 1}"
        self.send_command(scrtxt)

        # Set geometry to be able to use parser output (left, top, right, bottom, in mm)
        self.send_command(self._build_screen_phys_coords_command())

        if self.settings.VIEWING_DIST_TOP_BOTTOM:
            scrtxt = f"screen_distance {self.settings.VIEWING_DIST_TOP_BOTTOM[0]} {self.settings.VIEWING_DIST_TOP_BOTTOM[1]}"
            self.send_command(scrtxt)

        # Set remote mode lens if provided
        if self.settings.REMOTE_LENS is not None:
            self.send_command(f"camera_lens_focal_length = {self.settings.REMOTE_LENS}")

        # Set content of edf file
        self.send_command("file_event_filter = " + self.settings.FILE_EVENT_FILTER)
        self.send_command("link_event_filter = " + self.settings.LINK_EVENT_FILTER)
        self.send_command("link_sample_data = " + self.settings.LINK_SAMPLE_DATA)
        self.send_command("file_sample_data = " + self.settings.FILE_SAMPLE_DATA)

        self.send_command(
            f"screen_distance = {self.settings.CAMERA_TO_SCREEN_DISTANCE} {self.settings.CAMERA_TO_SCREEN_DISTANCE}"
        )
        self.send_command(self._build_screen_phys_coords_command(use_equals=True))
        self.send_command(f"sample_rate = {self.settings.SAMPLE_RATE}")
        self.send_command(f"pupil_size_diameter = {self.settings.PUPIL_SIZE_MODE}")

        self.send_command(" ".join(["calibration_corner_scaling", "=", str(self.settings.CALIBRATION_CORNER_SCALING)]))
        self.send_command(" ".join(["validation_corner_scaling", "=", str(self.settings.VALIDATION_CORNER_SCALING)]))
        self.send_command(
            " ".join([
                "calibration_area_proportion",
                "=",
                " ".join([str(i) for i in self.settings.CALIBRATION_AREA_PROPORTION]),
            ])
        )
        self.send_command(
            " ".join([
                "validation_area_proportion",
                "=",
                " ".join([str(i) for i in self.settings.VALIDATION_AREA_PROPORTION]),
            ])
        )
        self.send_command(f"heuristic_filter {self.settings.HEURISTIC_FILTER[0]} {self.settings.HEURISTIC_FILTER[1]}")

        if "CENTROID" in self.settings.PUPIL_TRACKING_MODE:
            self.send_command("use_ellipse_fitter = NO")
        else:
            self.send_command("use_ellipse_fitter = YES")

    def set_pupil_only_mode(self) -> None:
        """Set tracker in pupil only mode (no corneal reflection)."""
        # Activate the selection of pupil only mode
        self.send_command("force_corneal_reflection = OFF")  # Default OFF
        self.send_command("allow_pupil_without_cr = ON")  # overwritten in Pupil/CR mode
        self.send_command("elcl_hold_if_no_corneal = OFF")  # Default OFF
        self.send_command("elcl_search_if_no_corneal = OFF")  # Default OFF
        self.send_command("elcl_use_pcr_matching = OFF")  # Default ON

        # Select it!
        self.send_command("corneal_mode = NO")  # Default ON

    def _enable_raw_data(self, do_enable: bool = True) -> None:
        """Enable/disable raw pupil and CR in online sample data over link.

        Args:
            do_enable: True to enable, False to disable

        """
        # Switch tracker to idle and give it time to complete mode switch
        self.set_offline_mode()
        time.sleep(0.050)
        pylink.enablePCRSample(do_enable)

    @staticmethod
    def _enable_realtime_mode() -> None:
        """Enable EyeLink realtime mode."""
        pylink.beginRealTimeMode(100)

    @staticmethod
    def _disable_realtime_mode() -> None:
        """Disable EyeLink realtime mode."""
        pylink.endRealTimeMode()

    def draw_text_on_host(self, msg: str) -> None:
        """Draw text on eye-tracker screen.

        Args:
            msg: Text to draw

        """
        # Figure out center
        x = self.settings.SCREEN_RES[0] / 2

        # Send message
        txt = f'"{msg}"'
        self.draw_text(txt, (x, 50))

    def _setup_raw_data_recording(self, enable: bool = True) -> None:
        """Configure tracker for raw pupil/CR data recording.

        Args:
            enable: True to enable raw data, False to disable

        """
        # Setup the EDF-file such that it adds 'raw' data
        if enable:
            self.send_command("file_sample_raw_pcr = 0")  # Don't write raw data to file...
            self.send_command("link_sample_raw_pcr = 1")  # only over link
            self.send_command("raw_pcr_dual_corneal = 1")  # Enable tracking of two CR (corneal reflections)

            self.send_command("inputword_is_window = ON")
            self.send_command(
                "file_sample_data = LEFT,RIGHT,GAZE,GAZERES,AREA,HREF,PUPIL,STATUS,INPUT,HMARKER,HTARGET"
            )
            self.send_command(
                "link_sample_data = LEFT,RIGHT,GAZE,GAZERES,AREA,HREF,PUPIL,STATUS,INPUT,HMARKER,HTARGET"
            )
        else:
            self.send_command("file_sample_raw_pcr = 0")
            self.send_command("link_sample_raw_pcr = 0")
            self.send_command("raw_pcr_dual_corneal = 0")

            self.send_command(
                "file_sample_data = LEFT,RIGHT,GAZE,GAZERES,AREA,HREF,PUPIL,STATUS,INPUT,HMARKER,HTARGET"
            )
            self.send_command(
                "link_sample_data = LEFT,RIGHT,GAZE,GAZERES,AREA,HREF,PUPIL,STATUS,INPUT,HMARKER,HTARGET"
            )


__all__ = ["EyeLink", "Settings"]
