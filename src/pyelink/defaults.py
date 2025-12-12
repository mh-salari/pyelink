"""Default configuration values for pyelink.

All default values are defined here in one place.
Change these values to modify the library's default behavior.

Many of these settings are based on the original Pylink wrapper for PsychoPy by Marcus Nyström (Lund University Humanities Lab).
Comments below provide context and rationale for default values, as in the original codebase.
"""

# =============================================================================
# FILE SETTINGS
# =============================================================================
FILENAME = "test"  # Name of the EDF file to be created for each session
FILEPATH = ""  # Path where the EDF file will be saved (empty string = current directory)


# =============================================================================
# SAMPLING SETTINGS
# =============================================================================
SAMPLE_RATE = 1000  # Always use 1000 Hz; lower rates are filtered/downsampled versions


# =============================================================================
# CALIBRATION SETTINGS
# =============================================================================
N_CAL_TARGETS = 9  # Number of calibration points (9 is standard; 13 for widescreens)
ENABLE_AUTOMATIC_CALIBRATION = (
    True  # YES=auto-advance through calibration points, NO=manual (SPACE to accept each point)
)
PACING_INTERVAL = (
    1000  # Time in ms to fixate each target during calibration (only used if ENABLE_AUTOMATIC_CALIBRATION=True)
)
CALIBRATION_CORNER_SCALING = (
    1  # How far corner calibration points are from the screen edge (1=default; <1 closer to center, >1 closer to edge)
)
VALIDATION_CORNER_SCALING = 1  # How far corner validation points are from the screen edge (same scaling as above)
CALIBRATION_AREA_PROPORTION = [
    0.88,
    0.83,
]  # [width, height] as proportion of screen used for calibration targets (e.g., 0.9 = 90% of screen)
VALIDATION_AREA_PROPORTION = [0.88, 0.83]  # [width, height] as proportion of screen used for validation targets


# =============================================================================
# CALIBRATION TARGET SETTINGS
# =============================================================================
TARGET_TYPE = "ABC"  # "ABC", "AB", "A", "B", "C", "CIRCLE", or "IMAGE" (see docs)
TARGET_IMAGE_PATH = None  # Path to image file (for TARGET_TYPE="IMAGE")
CAL_BACKGROUND_COLOR = (128, 128, 128)  # RGB gray background for calibration
CALIBRATION_INSTRUCTION_TEXT = (
    "C to calibrate | V to validate | Enter to show camera image"  # Instruction text on calibration screen
)
CALIBRATION_TEXT_COLOR = (255, 255, 255)  # RGB white text color for instructions

# Fixation target settings (for A/B/C/AB/ABC types)
FIXATION_TARGET_SCALE = 0.75
FIXATION_CENTER_DIAMETER = 0.1 * FIXATION_TARGET_SCALE  # "A" component (deg visual angle)
FIXATION_OUTER_DIAMETER = 0.6 * FIXATION_TARGET_SCALE  # "B" component (deg visual angle)
FIXATION_CROSS_WIDTH = 0.17 * FIXATION_TARGET_SCALE  # "C" component (deg visual angle)
FIXATION_CENTER_COLOR = (0, 0, 0, 255)  # RGBA black, fully opaque
FIXATION_OUTER_COLOR = (0, 0, 0, 255)  # RGBA black, fully opaque
FIXATION_CROSS_COLOR = (255, 255, 255, 0)  # Transparent white cross (alpha=0)

# Circle target settings (for TARGET_TYPE="CIRCLE")
CIRCLE_OUTER_RADIUS = 15  # Outer radius in pixels
CIRCLE_INNER_RADIUS = 5  # Inner radius in pixels
CIRCLE_OUTER_COLOR = (0, 0, 0)  # RGB black
CIRCLE_INNER_COLOR = (128, 128, 128)  # RGB gray


# =============================================================================
# SCREEN SETTINGS (ALL MEASUREMENTS IN MILLIMETERS)
# =============================================================================
SCREEN_RES = [1280, 1024]  # [width, height] in pixels
SCREEN_WIDTH = 376.0  # Physical width in mm
SCREEN_HEIGHT = 301.0  # Physical height in mm

# Screen distance parameters (at least one must be provided):
SCREEN_DISTANCE = None  # Distance from eye to center of screen in mm (float or None)
SCREEN_DISTANCE_TOP_BOTTOM = [960, 1000]  # [top, bottom] (list of two positive numbers or None)
# If both are provided, SCREEN_DISTANCE_TOP_BOTTOM is used for higher accuracy.

CAMERA_TO_SCREEN_DISTANCE = 475.0  # Distance from camera to screen in mm (optional, for remote mode)
CAMERA_LENS_FOCAL_LENGTH = 38  # Remote mode lens focal length in mm (optional, for remote mode)


# =============================================================================
# TRACKING SETTINGS
# =============================================================================
PUPIL_TRACKING_MODE = "CENTROID"  # "CENTROID" or "ELLIPSE"
PUPIL_SIZE_MODE = "AREA"  # 'AREA' or 'DIAMETER'
HEURISTIC_FILTER = [0, 0]  # [link, file] (0=off, 1=normal, 2=extra). Default for EyeLink II/1000 is [1, 2]
SET_HEURISTIC_FILTER = True  # Activate filter or not (must be set every time recording starts)
ENABLE_DUAL_CORNEAL_TRACKING = False  # Enable tracking of secondary corneal reflections


# =============================================================================
# RECORDING SETTINGS and CONTENT of EDF FILE
# =============================================================================
FILE_EVENT_FILTER = "LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT"  # Which events to record to file
LINK_EVENT_FILTER = "LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT"  # Over link
LINK_SAMPLE_DATA = "LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,HTARGET"  # Sample fields over link
FILE_SAMPLE_DATA = "LEFT,RIGHT,GAZE,GAZERES,AREA,HREF,PUPIL,STATUS,INPUT,HMARKER,HTARGET"  # To file

RECORD_SAMPLES_TO_FILE = 1  # 1=on, 0=off
RECORD_EVENTS_TO_FILE = 1  # 1=on, 0=off
RECORD_SAMPLE_OVER_LINK = 1  # 1=on, 0=off
RECORD_EVENT_OVER_LINK = 1  # 1=on, 0=off


# =============================================================================
# DISPLAY SETTINGS
# =============================================================================
BACKEND = "pygame"  # Visualization backend: "pygame", "psychopy", or "pyglet"
FULLSCREEN = True  # True for fullscreen window, False for windowed mode
DISPLAY_INDEX = 0  # Monitor index: 0=primary, 1=secondary, etc.


# =============================================================================
# HARDWARE SETTINGS
# =============================================================================
ENABLE_SEARCH_LIMITS = "ON"  # ON (default) or OFF
TRACK_SEARCH_LIMITS = "OFF"  # OFF (default) or ON - limits tracking search area
AUTOTHRESHOLD_CLICK = "YES"  # YES (default) or NO - auto-adjust threshold on click
AUTOTHRESHOLD_REPEAT = "YES"  # YES (default) or NO - repeat auto-threshold
ENABLE_CAMERA_POSITION_DETECT = "ON"  # OFF (default) or ON - camera position detection
ILLUMINATION_POWER = 2  # 'elcl_tt_power' setting: 1=100%, 2=75%, 3=50%
HOST_IP = "100.1.1.1"  # IP address of EyeLink Host PC
EL_CONFIGURATION = "BTABLER"  # Options: MTABLER, BTABLER, RTABLER, RBTABLER, AMTABLER, ARTABLER, BTOWER
EYE_TRACKED = "BOTH"  # BOTH/LEFT/RIGHT. Sets binocular_enabled=YES for both, or active_eye=LEFT/RIGHT for monocular
