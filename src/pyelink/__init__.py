"""PyELink - Multi-backend Python wrapper for SR Research EyeLink eye trackers.

This package provides a clean, modern interface for EyeLink eye tracking with support
for multiple visualization backends (pygame, PsychoPy, pyglet).

The tracker creates and owns the display window throughout the experiment.
Users can access the window directly (Option A) or use helper methods (Option B).

Example:
    >>> import pyelink as el
    >>>
    >>> # Configure tracker with backend
    >>> settings = el.Settings(
    ...     backend='pygame',  # or 'psychopy', 'pyglet'
    ...     fullscreen=True,
    ...     screen_res=[1920, 1080]
    ... )
    >>>
    >>> # Tracker creates window automatically
    >>> tracker = el.EyeLink(settings)
    >>>
    >>> # Calibrate (no parameters needed!)
    >>> tracker.calibrate()
    >>>
    >>> # Option A: Direct window access
    >>> tracker.window.fill((128, 128, 128))
    >>> tracker.flip()
    >>>
    >>> # Option B: Helper methods
    >>> tracker.show_message("Press SPACE to begin")
    >>> tracker.wait_for_key('space')
    >>>
    >>> # Run your experiment
    >>> tracker.start_recording()
    >>> # ... show stimuli, collect data ...
    >>> tracker.stop_recording()
    >>>
    >>> # Clean up (closes window automatically)
    >>> tracker.end_experiment('./')

Attribution:
    Based on code by Marcus Nyström (Lund University Humanities Lab)
    Inspired by pylinkwrapper (Nick DiQuattro) and PyGaze (Edwin Dalmaijer)

"""

from .audio import AudioPlayer, get_player, play_done_beep, play_error_beep, play_target_beep
from .calibration import SUPPORTED_BACKENDS, create_calibration, get_available_backends, get_backend
from .core import EyeLink, Settings
from .utils import RingBuffer
from .version import check_python_version, get_recommended_backends

__version__ = "1.0.0"
__author__ = "Mohammadhossein Salari"
__email__ = "Mohammadhossein.salari@gmail.com"

__all__ = [  # noqa: RUF022
    # Core functionality
    "Settings",
    "EyeLink",
    "RingBuffer",
    # Audio (works with any backend)
    "AudioPlayer",
    "get_player",
    "play_target_beep",
    "play_done_beep",
    "play_error_beep",
    # Calibration
    "create_calibration",
    "get_backend",
    "get_available_backends",
    "SUPPORTED_BACKENDS",
    # Version checking
    "check_python_version",
    "get_recommended_backends",
    # Metadata
    "__version__",
    "__author__",
    "__email__",
]
