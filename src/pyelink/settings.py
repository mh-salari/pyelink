"""EyeLink tracker settings with runtime validation.

This module defines all configuration settings for EyeLink tracker operation.
Settings use Pydantic for runtime validation and rich IDE support via comprehensive docstrings.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Callable, Literal

from pydantic import BaseModel, Field, ValidationInfo, field_validator, model_validator


class Settings(BaseModel):
    """EyeLink tracker configuration with runtime validation.

    All settings have comprehensive docstrings visible in IDE autocomplete.
    Values are validated at creation and on assignment.

    Example:
        settings = Settings()
        settings.n_cal_targets = 13
        settings.save_to_file("my_config.json")

    """

    # =========================================================================
    # FILE SETTINGS
    # =========================================================================

    filename: str = Field(
        default="test",
        min_length=1,
        description="""EDF filename without .edf extension.

        Length restrictions depend on enable_long_filenames setting:
        - When False: Maximum 8 characters (DOS 8.3 format)
        - When True: Maximum 64 characters

        Only alphanumeric characters and underscores are allowed.

        Example: "test", "exp01", "participant_01_session_2"
        """,
    )

    filepath: str = Field(
        default="./",
        description="""Directory where EDF file will be saved locally.

        Defaults to current directory ("./").
        Path is created if it doesn't exist.

        Example: "./data/", "./experiment_data/session1/"
        """,
    )

    enable_long_filenames: bool = Field(
        default=True,
        description="""Enable long filename support on EyeLink Host PC.

        When True, sends 'long_filename_enabled = YES' command to Host PC,
        allowing filenames up to 64 characters with more flexible character rules.
        When False, enforces legacy 8-character DOS 8.3 format.

        Falls back to 8-character mode if Host PC doesn't support long filenames.
        """,
    )

    max_filename_length: int = Field(
        default=64,
        ge=8,
        le=255,
        description="""Maximum filename length when long filenames are enabled.

        Default: 64 characters (conservative limit for most EyeLink systems)
        Only applies when enable_long_filenames=True.
        """,
    )

    # =========================================================================
    # SAMPLING SETTINGS
    # =========================================================================

    sample_rate: Literal[250, 500, 1000, 2000] = Field(
        default=1000,
        description="""Sampling rate in Hz.

        Available rates:
        - 250 Hz: Pupil-only mode, standard speed
        - 500 Hz: Pupil-CR mode, standard speed
        - 1000 Hz: Pupil-CR mode, high speed (recommended)
        - 2000 Hz: Pupil-only mode, high speed

        Note: Lower rates are filtered/downsampled versions of 1000/2000 Hz.
        Always use 1000 Hz unless specific requirements demand otherwise.

        Reference: DEFAULTS.INI line 20
        """,
    )

    # =========================================================================
    # CALIBRATION SETTINGS
    # =========================================================================

    n_cal_targets: Literal[3, 5, 9, 13] = Field(
        default=9,
        description="""Number of calibration points.

        Available configurations:
        - 3: H3 horizontal-only (specialized use cases)
        - 5: HV5 bi-quadratic
        - 9: HV9 bi-quadratic with corner correction (standard, recommended)
        - 13: HV13 bi-cubic for large displays (>±20 degrees angular extent)

        WARNING: HV9 should NOT be used for remote mode.
        WARNING: HV13 should NOT be used when accurate data from corners is required.

        Reference: CALIBR.INI line 19-30, DEFAULTS.INI line 26
        """,
    )

    enable_automatic_calibration: bool = Field(
        default=True,
        description="""Enable automatic sequencing of calibration targets.

        - True: Auto-advance through points when participant fixates (hands-free)
        - False: Manual triggering with SPACE key or remote collection

        Automatic mode detects fixation and advances automatically.
        Manual mode requires experimenter to press SPACE to accept each point.

        Reference: CALIBR.INI line 228-231, DEFAULTS.INI line 27-29
        """,
    )

    pacing_interval: int = Field(
        default=1000,
        ge=500,
        le=3000,
        description="""Minimum time (ms) between target presentation in automatic mode.

        Controls subjective speed of calibration sequence.
        Only used when enable_automatic_calibration=True.

        Range: 500-3000 ms
        Default: 1000 ms (balanced)

        Shorter intervals = faster calibration but may rush participants.
        Longer intervals = more comfortable but slower overall.

        Reference: CALIBR.INI line 252-254, DEFAULTS.INI line 30-32
        """,
    )

    calibration_corner_scaling: float = Field(
        default=1.0,
        ge=0.5,
        le=1.5,
        description="""Distance of corner calibration targets from screen edge.

        - 1.0: Default position (standard)
        - <1.0: Closer to center (reduces required gaze excursion)
        - >1.0: Closer to edge (increases coverage area)

        Range: 0.5-1.5

        Use <1.0 to reduce head movement requirements or limit gaze angles.
        Use >1.0 only if you need to calibrate extreme peripheral vision.

        Reference: CALIBR.INI line 127-138, DEFAULTS.INI line 33-35
        """,
    )

    validation_corner_scaling: float = Field(
        default=1.0,
        ge=0.5,
        le=1.5,
        description="""Distance of corner validation targets from screen edge.

        Same scaling as calibration_corner_scaling but for validation.
        Common to use 0.88 to pull validation points slightly inward
        from calibration points for independent accuracy assessment.

        Reference: DEFAULTS.INI line 36
        """,
    )

    calibration_area_proportion: tuple[float, float] = Field(
        default=(0.88, 0.83),
        description="""[width, height] proportion of screen used for calibration targets.

        Values are fractions of screen dimensions.
        Example: (0.88, 0.83) = 88% of width, 83% of height

        Default (0.88, 0.83) leaves margins at screen edges for comfort.
        For widescreen displays (>±20° angular extent), consider using 13-point
        calibration instead of increasing these values.

        Must be in range (0, 1] for both dimensions.

        Reference: CALIBR.INI line 114-125, DEFAULTS.INI line 37-40
        """,
    )

    validation_area_proportion: tuple[float, float] = Field(
        default=(0.88, 0.83),
        description="""[width, height] proportion of screen used for validation targets.

        Same format as calibration_area_proportion.
        Typically matches calibration values but can be adjusted independently.

        Reference: DEFAULTS.INI line 41
        """,
    )

    # =========================================================================
    # TARGET APPEARANCE SETTINGS
    # =========================================================================

    target_type: Literal["ABC", "AB", "A", "B", "C", "CIRCLE", "IMAGE"] = Field(
        default="ABC",
        description="""Calibration target type.

        Available types:
        - ABC: Center dot + outer ring + cross (most visible, recommended)
        - AB: Center dot + outer ring
        - A: Center dot only (minimal)
        - B: Outer ring only
        - C: Cross only
        - CIRCLE: Simple filled circle
        - IMAGE: Custom image from file (requires target_image_path)

        ABC provides maximum visibility across different backgrounds.
        Use simpler types only if you have specific requirements.

        Reference: DEFAULTS.INI line 47
        """,
    )

    target_image_path: str | None = Field(
        default=None,
        description="""Path to custom target image file.

        Required when target_type="IMAGE".
        Must be a valid image file path (PNG, JPG, etc.).

        Image should be small (recommended: <100x100 pixels) and have
        a clear fixation point.

        Reference: DEFAULTS.INI line 48
        """,
    )

    cal_background_color: tuple[int, int, int] = Field(
        default=(128, 128, 128),
        description="""RGB background color for calibration screen.

        Format: (R, G, B) where each value is 0-255.
        Default: (128, 128, 128) = middle gray (recommended for most use cases)

        Middle gray provides good contrast for both dark and light targets.
        Match this to your experiment's background color if possible.

        Reference: DEFAULTS.INI line 49
        """,
    )

    calibration_instruction_text: str = Field(
        default="C to calibrate | V to validate | Enter to show camera image",
        description="""Instruction text displayed on calibration screen.

        This text is shown at the top of the screen during calibration setup.
        Customize to match your experimental instructions or language.

        Reference: DEFAULTS.INI line 50-52
        """,
    )

    calibration_text_color: tuple[int, int, int] = Field(
        default=(255, 255, 255),
        description="""RGB text color for calibration instructions.

        Format: (R, G, B) where each value is 0-255.
        Default: (255, 255, 255) = white

        Should contrast well with cal_background_color.

        Reference: DEFAULTS.INI line 53
        """,
    )

    calibration_text_font_size: int = Field(
        default=18,
        gt=0,
        description="""Font size for calibration instruction text.

        Controls the size of the instruction text shown on the setup screen
        before calibration begins.

        Default: 18
        """,
    )

    calibration_text_font_name: str = Field(
        default="Arial",
        min_length=1,
        description="""Font name for calibration instruction text.

        System font name to use for instruction text on the setup screen.

        Default: "Arial"
        """,
    )

    calibration_instruction_page_callback: Callable[[object], None] | None = Field(
        default=None,
        exclude=True,
        description="""Custom callback to replace default calibration instruction page.

        If provided, this function replaces the default instruction screen shown
        before calibration begins. Receives the backend-specific window object.

        Signature: callback(window) -> None

        Window types by backend:
        - pygame: pygame.Surface
        - psychopy: psychopy.visual.Window
        - pyglet: pyglet.window.Window

        Note: User must call appropriate flip/display update at the end.

        Example (pygame):
            def custom_instruction_page(window):
                window.fill((0, 0, 128))  # Dark blue
                font = pygame.font.SysFont("Arial", 24)
                text = font.render("Press C to begin", True, (255, 255, 255))
                window.blit(text, (100, 100))
                pygame.display.flip()

            settings = Settings(
                backend='pygame',
                calibration_instruction_page_callback=custom_instruction_page
            )
        """,
    )

    # Fixation target settings (for ABC types)
    fixation_center_diameter: float = Field(
        default=0.075,
        ge=0.01,
        le=1.0,
        description="""Center dot diameter in degrees of visual angle ('A' component).

        This is the small central dot participants fixate on.
        Default: 0.075°
        """,
    )

    fixation_outer_diameter: float = Field(
        default=0.45,
        ge=0.1,
        le=2.0,
        description="""Outer ring diameter in degrees of visual angle ('B' component).

        Surrounds the center dot to increase visibility.
        Default: 0.45°
        """,
    )

    fixation_cross_width: float = Field(
        default=0.1275,
        ge=0.01,
        le=1.0,
        description="""Cross width in degrees of visual angle ('C' component).
        Default: 0.1275°
        """,
    )

    fixation_center_color: tuple[int, int, int, int] = Field(
        default=(0, 0, 0, 255),
        description="""RGBA color for center dot.

        Format: (R, G, B, A) where each value is 0-255.
        Default: (0, 0, 0, 255) = black, fully opaque

        Alpha channel (A) controls transparency: 255=opaque, 0=transparent.
        """,
    )

    fixation_outer_color: tuple[int, int, int, int] = Field(
        default=(0, 0, 0, 255),
        description="""RGBA color for outer ring.

        Default: (0, 0, 0, 255) = black, fully opaque
        """,
    )

    fixation_cross_color: tuple[int, int, int, int] = Field(
        default=(255, 255, 255, 0),
        description="""RGBA color for cross.

        Default: (255, 255, 255, 0) = white but fully transparent

        Set alpha to 255 to make cross visible.
        """,
    )

    # Circle target settings
    circle_outer_radius: int = Field(
        default=15,
        ge=5,
        le=100,
        description="""Outer radius in pixels for CIRCLE target type.

        Only used when target_type="CIRCLE".
        Default: 15 pixels
        """,
    )

    circle_inner_radius: int = Field(
        default=5,
        ge=1,
        le=50,
        description="""Inner radius in pixels for CIRCLE target type.

        Only used when target_type="CIRCLE".
        Creates a ring by having smaller inner filled circle.
        """,
    )

    circle_outer_color: tuple[int, int, int] = Field(
        default=(0, 0, 0),
        description="""RGB color for circle outer ring (CIRCLE target type).
        """,
    )

    circle_inner_color: tuple[int, int, int] = Field(
        default=(128, 128, 128),
        description="""RGB color for circle center (CIRCLE target type).
        """,
    )

    # =========================================================================
    # SCREEN PHYSICAL SETTINGS (ALL MEASUREMENTS IN MILLIMETERS)
    # =========================================================================

    screen_res: tuple[int, int] = Field(
        default=(1280, 1024),
        description="""[width, height] screen resolution in pixels.

        CRITICAL: Must match your actual display resolution exactly.
        Incorrect values will cause inaccurate gaze data.

        Example: (1920, 1080), (1280, 1024), (2560, 1440)

        Reference: DEFAULTS.INI line 74
        """,
    )

    screen_width: float = Field(
        default=376.0,
        gt=0,
        description="""Physical screen width in millimeters.

        CRITICAL: Measure the actual display area (NOT including bezel).
        Use a ruler or tape measure for accuracy.
        Incorrect value will cause systematic gaze position errors.

        Example: A 19-inch 4:3 monitor is typically ~376mm wide.

        Reference: DEFAULTS.INI line 75
        """,
    )

    screen_height: float = Field(
        default=301.0,
        gt=0,
        description="""Physical screen height in millimeters.

        CRITICAL: Measure the actual display area (NOT including bezel).
        Incorrect value will cause systematic gaze position errors.

        Example: A 19-inch 4:3 monitor is typically ~301mm tall.

        Reference: DEFAULTS.INI line 76
        """,
    )

    camera_to_screen_distance: float = Field(
        default=475.0,
        gt=0,
        description="""Distance from camera to screen in millimeters.

        Used for remote mode setups.
        Measure from camera lens to screen surface.

        Reference: DEFAULTS.INI line 83
        """,
    )

    screen_distance: float | None = Field(
        default=None,
        gt=0,
        description="""Distance from participant's eye to screen center in millimeters.

        CRITICAL for accurate gaze data.

        Use this OR screen_distance_top_bottom (not both).
        If both provided, screen_distance_top_bottom takes precedence.

        For chin-rest setups where viewing is perpendicular to screen,
        this single value is sufficient.

        Reference: DEFAULTS.INI line 79
        """,
    )

    screen_distance_top_bottom: tuple[float, float] | None = Field(
        default=(960.0, 1000.0),
        description="""[top, bottom] distances from eye to screen edges in millimeters.

        CRITICAL for accurate gaze data.

        More accurate than screen_distance for non-perpendicular viewing.
        Format: (distance_to_top_edge, distance_to_bottom_edge)

        Default: (960, 1000) assumes participant is slightly below screen center.

        Both values must be positive.
        At least one of screen_distance or screen_distance_top_bottom must be provided.

        Reference: DEFAULTS.INI line 80-81
        """,
    )

    camera_lens_focal_length: int | None = Field(
        default=38,
        gt=0,
        description="""Camera lens focal length in millimeters.

        For remote mode configurations.
        Check your camera specifications or headband label.

        Common values: 25mm, 38mm, 50mm

        Reference: DEFAULTS.INI line 84
        """,
    )

    # =========================================================================
    # DISPLAY BACKEND SETTINGS
    # =========================================================================

    backend: Literal["pygame", "psychopy", "pyglet"] = Field(
        default="pygame",
        description="""Display backend for rendering.

        Available backends:
        - pygame: Python 3.9-3.14, simple and reliable (recommended)
        - psychopy: Python 3.9-3.11 only, full psychophysics features
        - pyglet: Python 3.8-3.14, OpenGL-based

        Backends are mutually exclusive (PsychoPy pins pyglet 1.4.11).
        Choose based on your Python version and experimental needs.

        Reference: DEFAULTS.INI line 114
        """,
    )

    fullscreen: bool = Field(
        default=True,
        description="""Run display in fullscreen mode.

        Recommended: True for experiments (prevents distractions, accurate timing)
        Use False only for development/testing

        Reference: DEFAULTS.INI line 115
        """,
    )

    display_index: int = Field(
        default=0,
        ge=0,
        description="""Monitor index for display.

        - 0: Primary monitor
        - 1: Secondary monitor
        - etc.

        Useful for dual-monitor setups where EyeLink host is on one monitor
        and experiment on another.

        Reference: DEFAULTS.INI line 116
        """,
    )

    # =========================================================================
    # TRACKING SETTINGS
    # =========================================================================

    pupil_tracking_mode: Literal["CENTROID", "ELLIPSE"] = Field(
        default="CENTROID",
        description="""Pupil tracking algorithm.

        - CENTROID: Faster, works well for most applications (recommended)
        - ELLIPSE: More accurate for large pupils or partial occlusion

        CENTROID computes pupil center from weighted area.
        ELLIPSE fits an ellipse to pupil boundary (slower but more robust).

        Reference: DEFAULTS.INI line 90
        """,
    )

    pupil_size_mode: Literal["AREA", "DIAMETER"] = Field(
        default="AREA",
        description="""How pupil size is reported in data.

        - AREA: Raw area in arbitrary units (default)
        - DIAMETER: Converted to diameter estimate (128 * sqrt(area))

        AREA provides more direct measurement.
        DIAMETER is more intuitive but involves conversion.

        Reference: DEFAULTS.INI line 111-121
        """,
    )

    heuristic_filter: tuple[int, int] = Field(
        default=(1, 1),
        description="""[link, file] heuristic filter levels for noise reduction.

        Format: (link_filter_level, file_filter_level)

        Levels:
        - 0: OFF (no filtering)
        - 1: Normal filtering (1 sample delay) - recommended
        - 2: Extra filtering (2 sample delay)

        Default for EyeLink II/1000: (1, 2)
        Current default: (1, 1) for consistent link and file data

        Higher levels reduce noise but add latency.
        Each level adds one sample of delay.

        Reference: DEFAULTS.INI line 92, 153-166
        """,
    )

    set_heuristic_filter: bool = Field(
        default=True,
        description="""Whether to activate the heuristic filter.

        Must be set every time recording starts.
        Set to False to disable filtering entirely.

        Reference: DEFAULTS.INI line 93
        """,
    )

    enable_dual_corneal_tracking: bool = Field(
        default=False,
        description="""Enable tracking of secondary corneal reflections.

        Advanced feature for specialized setups.
        Requires specific hardware configuration.

        Reference: DEFAULTS.INI line 94
        """,
    )

    # =========================================================================
    # DATA RECORDING SETTINGS
    # =========================================================================

    file_event_filter: str = Field(
        default="LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT",
        description="""Events to record to EDF file.

        Comma-separated list of event types.

        Available: LEFT, RIGHT, FIXATION, SACCADE, BLINK, MESSAGE, BUTTON, INPUT

        Reference: DEFAULTS.INI line 100
        """,
    )

    link_event_filter: str = Field(
        default="LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT",
        description="""Events to send over ethernet link (real-time).

        Same format as file_event_filter.
        Can differ from file settings for real-time vs offline analysis.

        Reference: DEFAULTS.INI line 101
        """,
    )

    link_sample_data: str = Field(
        default="LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,HTARGET",
        description="""Sample data fields to send over link (real-time).

        Comma-separated list of data fields.
        Less data than file for reduced bandwidth.

        Available fields:
        - LEFT/RIGHT: Eye data
        - GAZE: Screen xy position
        - GAZERES: Units-per-degree resolution
        - AREA: Pupil area
        - STATUS: Flags
        - HTARGET: Head target data

        Reference: DEFAULTS.INI line 102
        """,
    )

    file_sample_data: str = Field(
        default="LEFT,RIGHT,GAZE,GAZERES,AREA,HREF,PUPIL,STATUS,INPUT,HMARKER,HTARGET",
        description="""Sample data fields to record to EDF file.

        More comprehensive than link data.

        Additional fields vs link:
        - HREF: Head-referenced position
        - PUPIL: Raw pupil coordinates
        - INPUT: Input port data
        - HMARKER: Head markers

        Reference: DEFAULTS.INI line 103, 191-210
        """,
    )

    record_samples_to_file: bool = Field(
        default=True,
        description="""Record sample data to EDF file.

        Reference: DEFAULTS.INI line 105
        """,
    )

    record_events_to_file: bool = Field(
        default=True,
        description="""Record event data to EDF file.

        Reference: DEFAULTS.INI line 106
        """,
    )

    record_sample_over_link: bool = Field(
        default=True,
        description="""Send sample data over ethernet link (real-time).

        Reference: DEFAULTS.INI line 107
        """,
    )

    record_event_over_link: bool = Field(
        default=True,
        description="""Send event data over ethernet link (real-time).

        Reference: DEFAULTS.INI line 108
        """,
    )

    # =========================================================================
    # HARDWARE SETTINGS
    # =========================================================================

    enable_search_limits: bool = Field(
        default=True,
        description="""Enable search limits for pupil detection.

        Restricts pupil search area to improve tracking reliability.

        Reference: DEFAULTS.INI line 122
        """,
    )

    track_search_limits: bool = Field(
        default=False,
        description="""Track pupil to search limits boundary.

        When enabled, search limits follow the pupil position.

        Reference: DEFAULTS.INI line 123
        """,
    )

    autothreshold_click: bool = Field(
        default=True,
        description="""Auto-adjust threshold on mouse click in camera setup.

        Automatically finds optimal pupil/CR thresholds when you click on the eye image.

        Reference: DEFAULTS.INI line 124
        """,
    )

    autothreshold_repeat: bool = Field(
        default=True,
        description="""Repeat auto-threshold if pupil not centered on first attempt.

        Reference: DEFAULTS.INI line 125
        """,
    )

    enable_camera_position_detect: bool = Field(
        default=True,
        description="""Camera position detection on click/auto-threshold.

        Helps optimize camera positioning during setup.

        Reference: DEFAULTS.INI line 126
        """,
    )

    illumination_power: Literal[1, 2, 3] = Field(
        default=2,
        description="""IR illumination power level (elcl_tt_power).

        Levels:
        - 1: 100% power (maximum brightness, may cause glare)
        - 2: 75% power (default, balanced)
        - 3: 50% power (minimum, reduces glare but may affect tracking)

        Lower power reduces participant discomfort but may degrade tracking quality.

        Reference: DEFAULTS.INI line 127
        """,
    )

    host_ip: str = Field(
        default="100.1.1.1",
        pattern=r"^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|dummy)$",
        description="""IP address of EyeLink Host PC, or "dummy" for dummy mode.

        Standard EyeLink network configuration uses 100.1.1.1 for Host PC
        and 100.1.1.2 for Display PC.

        Use "dummy" to run without EyeLink hardware (for testing).

        Do not change unless you have a custom network configuration.

        Reference: DEFAULTS.INI line 128
        """,
    )

    # =========================================================================
    # PHYSICAL SETUP CONFIGURATION
    # =========================================================================

    el_configuration: Literal["MTABLER", "BTABLER", "RTABLER", "RBTABLER", "AMTABLER", "ARTABLER", "BTOWER"] = Field(
        default="BTABLER",
        description="""EyeLink physical configuration type.

        Options:
        - MTABLER: Monocular desktop mount (chin rest)
        - BTABLER: Binocular desktop mount (most common)
        - RTABLER: Remote desktop mode
        - RBTABLER: Remote binocular desktop mode
        - AMTABLER: Arm-mounted monocular
        - ARTABLER: Arm-mounted remote
        - BTOWER: Tower mount

        Must match your actual hardware configuration.

        Reference: DEFAULTS.INI line 129
        """,
    )

    eye_tracked: Literal["BOTH", "LEFT", "RIGHT"] = Field(
        default="BOTH",
        description="""Which eye(s) to track.

        Options:
        - BOTH: Binocular tracking (sets binocular_enabled=YES)
        - LEFT: Left eye only (sets active_eye=LEFT)
        - RIGHT: Right eye only (sets active_eye=RIGHT)

        Binocular tracking provides redundancy and allows dominant eye analysis.
        Monocular tracking may be necessary if one eye cannot be tracked reliably.

        Reference: DEFAULTS.INI line 130
        """,
    )

    # =========================================================================
    # PYDANTIC CONFIGURATION
    # =========================================================================

    model_config = {
        "validate_assignment": True,  # Validate on attribute changes
        "extra": "forbid",  # Reject unknown fields
        "use_enum_values": True,  # Use literal values instead of enums
    }

    # =========================================================================
    # VALIDATORS
    # =========================================================================

    @field_validator("calibration_area_proportion", "validation_area_proportion")
    @classmethod
    def validate_area_proportions(cls, v: tuple[float, float]) -> tuple[float, float]:
        """Validate area proportions are in valid range (0, 1]."""
        if not (0 < v[0] <= 1.0 and 0 < v[1] <= 1.0):
            raise ValueError(
                f"Area proportions must be in range (0, 1], got {v}. Values represent fraction of screen dimensions."
            )
        return v

    @field_validator("heuristic_filter")
    @classmethod
    def validate_heuristic_filter(cls, v: tuple[int, int]) -> tuple[int, int]:
        """Validate heuristic filter levels are 0-2."""
        if not all(0 <= x <= 2 for x in v):
            raise ValueError(f"Heuristic filter levels must be 0 (off), 1 (normal), or 2 (extra), got {v}")
        return v

    @field_validator("screen_res")
    @classmethod
    def validate_screen_res(cls, v: tuple[int, int]) -> tuple[int, int]:
        """Validate screen resolution has positive values."""
        if v[0] <= 0 or v[1] <= 0:
            raise ValueError(
                f"Screen resolution must be positive integers, got {v}. Example: (1920, 1080) or (1280, 1024)"
            )
        return v

    @field_validator("screen_distance_top_bottom")
    @classmethod
    def validate_screen_distance(
        cls, v: tuple[float, float] | None, info: ValidationInfo
    ) -> tuple[float, float] | None:
        """Ensure at least one screen distance measurement is provided."""
        if v is None and info.data.get("screen_distance") is None:
            raise ValueError(
                "Must provide either screen_distance or screen_distance_top_bottom. "
                "At least one screen distance measurement is required for accurate gaze data."
            )
        if v is not None and (v[0] <= 0 or v[1] <= 0):
            raise ValueError(f"Screen distances must be positive, got {v}. Values should be in millimeters.")
        return v

    @model_validator(mode="after")
    def validate_file_settings(self) -> Settings:
        """Validate file-related settings after all fields are set."""
        # Validate filename based on enable_long_filenames setting
        filename = self.filename
        enable_long = self.enable_long_filenames
        max_length = self.max_filename_length

        # Determine validation rules - only length changes, character rules stay the same
        pattern = r"^[a-zA-Z0-9_]+$"
        limit = max_length if enable_long else 8
        mode_desc = f"{limit} characters" if enable_long else "8-character limit (DOS 8.3 format)"

        # Validate length
        if len(filename) > limit:
            suggestion = (
                "Either shorten the name or adjust max_filename_length setting."
                if enable_long
                else "Either shorten the name or set enable_long_filenames=True."
            )
            raise ValueError(f"Filename '{filename}' exceeds maximum length of {mode_desc}. {suggestion}")

        # Validate characters
        if not re.match(pattern, filename):
            raise ValueError(
                f"Filename '{filename}' contains invalid characters. "
                f"Only alphanumeric characters and underscores are allowed."
            )

        # Validate no path separators
        if "/" in filename or "\\" in filename:
            raise ValueError(
                f"Filename '{filename}' cannot contain path separators. Use filepath setting for directory path."
            )

        return self

    # =========================================================================
    # SERIALIZATION METHODS
    # =========================================================================

    def save_to_file(self, path: str) -> None:
        """Save settings to JSON file.

        Args:
            path: File path (will be created/overwritten)

        Example:
            settings.save_to_file("my_experiment_config.json")

        """
        Path(path).write_text(self.model_dump_json(indent=2), encoding="utf-8")

    @classmethod
    def load_from_file(cls, path: str) -> Settings:
        """Load settings from JSON file.

        Args:
            path: File path to load from

        Returns:
            Settings instance with validated values

        Example:
            settings = Settings.load_from_file("my_experiment_config.json")

        """
        return cls.model_validate_json(Path(path).read_text(encoding="utf-8"))

    def to_dict(self) -> dict:
        """Convert settings to dictionary.

        Returns:
            Dictionary representation of all settings

        """
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict) -> Settings:
        """Create Settings from dictionary with validation.

        Args:
            data: Dictionary with setting names and values

        Returns:
            Settings instance with validated values

        """
        return cls.model_validate(data)
