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


def create_calibration(settings: object, tracker: object, mode: str = "normal") -> object:
    """Factory function to create calibration display.

    Uses the tracker's internal window (created based on settings.backend).
    The calibration display accesses the window via tracker.display.window.

    Args:
        settings: Settings object with configuration (includes BACKEND setting)
        tracker: EyeLink tracker instance (with display.window)
        mode: Calibration mode - "normal", "calibration-only", or "validation-only"

    Returns:
        CalibrationDisplay instance using tracker's internal window

    Example:
        >>> import pyelink as el
        >>>
        >>> # Configure tracker with backend
        >>> settings = el.Settings(BACKEND='pygame', FULLSCREEN=True)
        >>> tracker = el.EyeLink(settings)  # Creates window automatically
        >>>
        >>> # Create calibration (uses tracker's window)
        >>> calibration = el.create_calibration(settings, tracker)
        >>>
        >>> # Calibrate
        >>> tracker.calibrate(calibration)
        >>>
        >>> # Use tracker's window for experiment
        >>> tracker.window.fill((128, 128, 128))
        >>> tracker.flip()

    Note:
        The calibration uses the tracker's owned window. No separate window
        management needed - tracker handles window lifecycle.

    """
    # Get backend from settings
    backend = settings.backend
    logger.info("Creating calibration display for backend: %s (mode: %s)", backend, mode)

    calibration_class = get_backend(backend)
    return calibration_class(settings, tracker, mode=mode)


__all__ = [
    "SUPPORTED_BACKENDS",
    "create_calibration",
    "get_available_backends",
    "get_backend",
]
