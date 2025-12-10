"""Python version compatibility checking for eyelink-wrapper backends.

This module provides runtime checks to ensure that the Python version is compatible
with the requested visualization backend before attempting to import it.
"""

import sys
import warnings

# Version requirements for each backend
# Based on official documentation and testing as of 2025
BACKEND_REQUIREMENTS = {
    "psychopy": {
        "min_python": (3, 9),
        "max_python": (3, 11),
        "package": "psychopy",
        "reason": "PsychoPy officially supports Python 3.9-3.11",
    },
    "pygame": {
        "min_python": (3, 9),
        "max_python": (3, 14),
        "package": "pygame",
        "reason": "pygame supports Python 3.9-3.14",
    },
    "pyglet": {
        "min_python": (3, 8),
        "max_python": (3, 14),
        "package": "pyglet",
        "reason": "pyglet supports modern Python versions",
    },
}


def check_python_version(backend_name: str) -> tuple[bool, str]:
    """Check if current Python version is compatible with the requested backend.

    Args:
        backend_name: Name of the backend ('psychopy', 'pygame', 'pyglet')

    Returns:
        tuple: (is_compatible: bool, message: str)
            - is_compatible: True if Python version is compatible
            - message: Status message or error description

    """
    if backend_name not in BACKEND_REQUIREMENTS:
        return False, f"Unknown backend: {backend_name}"

    req = BACKEND_REQUIREMENTS[backend_name]
    current_version = sys.version_info[:2]

    if current_version < req["min_python"]:
        min_ver = ".".join(map(str, req["min_python"]))
        current_ver = sys.version.split()[0]
        return False, (
            f"{backend_name} requires Python >={min_ver} but you're using {current_ver}. Reason: {req['reason']}"
        )

    if current_version > req["max_python"]:
        max_ver = ".".join(map(str, req["max_python"]))
        current_ver = sys.version.split()[0]
        return False, (
            f"{backend_name} requires Python <={max_ver} but you're using {current_ver}. Reason: {req['reason']}"
        )

    return True, "Compatible"


def warn_if_incompatible(backend_name: str) -> bool:
    """Warn user if Python version is incompatible with backend.

    This function will issue a UserWarning if the Python version is not compatible
    with the requested backend, providing clear guidance on what to do.

    Args:
        backend_name: Name of the backend to check

    Returns:
        bool: True if compatible, False otherwise

    """
    is_compatible, message = check_python_version(backend_name)
    if not is_compatible:
        warnings.warn(
            f"\n{'=' * 60}\nWARNING: {message}\n{'=' * 60}\n",
            UserWarning,
            stacklevel=2,
        )
    return is_compatible


def get_recommended_backends() -> list[str]:
    """Get list of backends compatible with current Python version.

    Returns:
        list[str]: List of backend names that are compatible with the current
                   Python version

    """
    current_version = sys.version_info[:2]
    compatible = []

    for backend, req in BACKEND_REQUIREMENTS.items():
        if req["min_python"] <= current_version <= req["max_python"]:
            compatible.append(backend)

    return compatible


def get_incompatible_reason(backend_name: str) -> str | None:
    """Get the reason why a backend is incompatible with current Python version.

    Args:
        backend_name: Name of the backend

    Returns:
        str | None: Reason for incompatibility, or None if compatible

    """
    is_compatible, message = check_python_version(backend_name)
    if is_compatible:
        return None
    return message
