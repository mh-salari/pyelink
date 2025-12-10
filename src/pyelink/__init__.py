"""PyELink - Multi-backend Python wrapper for SR Research EyeLink eye trackers.

This package provides a clean, modern interface for EyeLink eye tracking with support
for multiple visualization backends (PsychoPy, pygame, pyglet).

Example:
    >>> import pyelink as el
    >>> from psychopy import visual
    >>>
    >>> # Create your experiment window
    >>> win = visual.Window(size=[1920, 1080], fullscr=True)
    >>>
    >>> # Configure tracker
    >>> settings = el.Settings()
    >>> settings.SCREEN_RES = [1920, 1080]
    >>> tracker = el.EyeLink(settings)
    >>>
    >>> # Create calibration (auto-detects backend from window type)
    >>> calibration = el.create_calibration(settings, tracker, win)
    >>>
    >>> # Calibrate
    >>> tracker.calibrate(calibration)
    >>>
    >>> # Run your experiment with the same window
    >>> # ... show stimuli, collect data ...
    >>>
    >>> # Clean up
    >>> tracker.end_experiment('./')
    >>> win.close()

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
