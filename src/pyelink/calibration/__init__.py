"""Calibration backend factory and auto-detection.

This module provides the factory function for creating calibration display objects
with automatic backend detection based on installed packages and Python version.

IMPORTANT: Backend imports are LAZY to avoid conflicts between psychopy/pyglet.
"""

import logging
import sys

from ..version import check_python_version, get_recommended_backends

logger = logging.getLogger(__name__)

# Backend registry - populated lazily
_backend_cache: dict[str, object] = {}

# List of supported backends
SUPPORTED_BACKENDS = ["pygame", "psychopy", "pyglet"]


def _import_backend(name: str) -> object | None:
    """Lazily import a backend module.

    Args:
        name: Backend name ('pygame', 'psychopy', 'pyglet')

    Returns:
        Class or None if import fails or version incompatible

    """
    # Return cached if already imported
    if name in _backend_cache:
        return _backend_cache[name]

    # Check Python version compatibility first
    is_compatible, _msg = check_python_version(name)
    if not is_compatible:
        _backend_cache[name] = None
        return None

    try:
        if name == "pygame":
            from .pygame_backend import PygameCalibrationDisplay  # noqa: PLC0415

            _backend_cache[name] = PygameCalibrationDisplay
        elif name == "psychopy":
            from .psychopy_backend import PsychopyCalibrationDisplay  # noqa: PLC0415

            _backend_cache[name] = PsychopyCalibrationDisplay
        elif name == "pyglet":
            from .pyglet_backend import PygletCalibrationDisplay  # noqa: PLC0415

            _backend_cache[name] = PygletCalibrationDisplay
        else:
            _backend_cache[name] = None

        return _backend_cache[name]
    except ImportError:
        _backend_cache[name] = None
        return None


def get_available_backends() -> dict[str, object]:
    """Get dictionary of currently available (installed) backends.

    Returns:
        Dict mapping backend name to class

    """
    available = {}
    for name in SUPPORTED_BACKENDS:
        backend = _import_backend(name)
        if backend is not None:
            available[name] = backend
    return available


def get_backend(name: str | None = None) -> object:
    """Get calibration backend by name or auto-detect.

    Args:
        name: Backend name ('pygame', 'psychopy', 'pyglet') or None for auto-detect

    Returns:
        CalibrationDisplay class

    Raises:
        ImportError: If no backends available
        RuntimeError: If Python version incompatible with requested backend
        ValueError: If requested backend not available

    """
    if name is None:
        # Auto-select first available backend
        available = get_available_backends()
        if not available:
            recommended = get_recommended_backends()
            raise ImportError(
                "No visualization backend available!\n\n"
                f"For Python {sys.version_info[0]}.{sys.version_info[1]}, "
                "you can install:\n" + "\n".join([f"  pip install pyelink[{b}]" for b in recommended])
            )
        name = next(iter(available.keys()))
        logger.info("Auto-selected backend: %s", name)

    # Check Python version compatibility
    is_compatible, msg = check_python_version(name)
    if not is_compatible:
        recommended = get_recommended_backends()
        raise RuntimeError(
            f"{msg}\n\n"
            f"For Python {sys.version_info[0]}.{sys.version_info[1]}, "
            f"compatible backends are: {', '.join(recommended)}"
        )

    # Try to import the specific backend
    backend = _import_backend(name)
    if backend is None:
        available = get_available_backends()
        available_names = ", ".join(available.keys())
        if available_names:
            raise ValueError(
                f"Backend '{name}' not available.\n"
                f"Available backends: {available_names}\n"
                f"Install with: pip install pyelink[{name}]"
            )
        recommended = get_recommended_backends()
        raise ValueError(
            f"Backend '{name}' not available and no other backends are installed.\n"
            f"For Python {sys.version_info[0]}.{sys.version_info[1]}, "
            "you can install:\n" + "\n".join([f"  pip install pyelink[{b}]" for b in recommended])
        )

    return backend


def _detect_backend_from_window(window: object) -> str | None:
    """Auto-detect backend from window type.

    Args:
        window: Window object (PsychoPy Window, pygame Surface, or pyglet Window)

    Returns:
        str | None: Backend name ('psychopy', 'pygame', 'pyglet') or None if unknown

    """
    # Check window's module to detect library
    window_module = type(window).__module__
    window_class = type(window).__name__

    # PsychoPy detection
    if "psychopy" in window_module or (window_class == "Window" and hasattr(window, "flip")):
        return "psychopy"

    # pygame detection
    if "pygame" in window_module or window_class == "Surface":
        return "pygame"

    # pyglet detection
    if "pyglet" in window_module or (window_class == "Window" and hasattr(window, "dispatch_events")):
        return "pyglet"

    return None


def create_calibration(settings: object, tracker: object, window: object, backend: str | None = None) -> object:
    """Factory function to create calibration display.

    Automatically detects the backend from the window type if not explicitly specified.
    The window you pass here is YOUR experiment window - it stays open for the entire
    experiment duration (calibration + trials).

    Args:
        settings: Settings object with configuration
        tracker: EyeLink tracker instance
        window: Display window object - YOUR experiment window that stays open
                - PsychoPy: visual.Window()
                - pygame: pygame.display.set_mode() or Surface
                - pyglet: pyglet.window.Window()
        backend: Backend name ('pygame', 'psychopy', 'pyglet') or None for auto-detect
                If None, automatically detects from window type

    Returns:
        CalibrationDisplay instance that wraps your window for calibration

    Example:
        >>> import pyelink as el
        >>> from psychopy import visual
        >>>
        >>> # Create YOUR window once (stays open for entire experiment)
        >>> win = visual.Window(size=[1920, 1080], fullscr=True)
        >>>
        >>> # Setup tracker
        >>> settings = el.Settings()
        >>> tracker = el.EyeLink(settings)
        >>>
        >>> # Auto-detect backend from window type (recommended)
        >>> calibration = el.create_calibration(settings, tracker, win)
        >>>
        >>> # Calibrate
        >>> tracker.calibrate(calibration)
        >>>
        >>> # Continue using YOUR window for experiment
        >>> # ... show stimuli, run trials, etc. ...
        >>> win.close()  # Close at end of experiment

    Note:
        The calibration object doesn't own or manage the window - it just wraps it
        for EyeLink calibration. You retain full control of your window.

    """
    # Auto-detect backend from window type if not specified
    if backend is None:
        backend = _detect_backend_from_window(window)
        if backend is None:
            raise ValueError(
                "Could not auto-detect backend from window type. "
                "Please specify backend explicitly:\n"
                "  create_calibration(settings, tracker, window, backend='psychopy')\n"
                "  create_calibration(settings, tracker, window, backend='pygame')\n"
                "  create_calibration(settings, tracker, window, backend='pyglet')"
            )
        logger.info("Auto-detected backend: %s", backend)

    calibration_class = get_backend(backend)
    return calibration_class(settings, tracker, window)


__all__ = [
    "SUPPORTED_BACKENDS",
    "create_calibration",
    "get_available_backends",
    "get_backend",
]
