"""Base display abstraction for window management across backends.

This module provides the abstract interface that all display backends must implement.
The abstraction enables backend-agnostic experiment code while maintaining direct access
to backend-specific windows when needed.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path


class BaseDisplay(ABC):
    """Abstract base class for display window management.

    Provides unified interface for window creation, event handling, and drawing
    across pygame, psychopy, and pyglet backends. Each backend implements this
    interface with backend-specific window management.

    The display owns the window throughout the experiment lifecycle. Users can:
    - Access raw backend window via `window` property (Option A: direct access)
    - Use backend-agnostic helper methods (Option B: abstraction layer)
    """

    def __init__(self, settings: object, shutdown_handler: object = None) -> None:
        """Initialize display and create window.

        Args:
            settings: Settings object containing BACKEND, FULLSCREEN, DISPLAY_INDEX, SCREEN_RES
            shutdown_handler: Callable to invoke when Ctrl+C detected (for graceful shutdown)

        """
        self.settings = settings
        self.shutdown_handler = shutdown_handler
        self._window = self._create_window(settings)

    @property
    def window(self) -> Any:  # noqa: ANN401
        """Get raw backend-specific window object.

        This provides direct access to the underlying window for backend-specific
        operations (Option A).

        Returns:
            Backend window object:
            - pygame: pygame.Surface
            - psychopy: psychopy.visual.Window
            - pyglet: pyglet.window.Window

        """
        return self._window

    @property
    @abstractmethod
    def backend_name(self) -> str:
        """Get backend identifier string.

        Returns:
            Backend name: "pygame", "psychopy", or "pyglet"

        """

    @abstractmethod
    def _create_window(self, settings: object) -> Any:  # noqa: ANN401
        """Create backend-specific window.

        Uses settings.screen_res, settings.fullscreen, and settings.display_index
        to create appropriately configured window.

        Args:
            settings: Settings object with display configuration

        Returns:
            Backend-specific window object

        """

    @abstractmethod
    def flip(self) -> None:
        """Update display to show drawn content.

        Equivalent to:
        - pygame: pygame.display.flip()
        - psychopy: win.flip()
        - pyglet: window.flip()
        """

    @abstractmethod
    def close(self) -> None:
        """Close window and clean up display resources.

        Called during tracker cleanup in end_experiment().
        """

    @abstractmethod
    def get_events(self) -> list[dict[str, Any]]:
        """Poll for keyboard and mouse events.

        Returns unified event dictionaries that abstract backend differences.

        Returns:
            List of event dicts with keys:
            - 'type': 'keydown', 'keyup', 'quit', 'mousebuttondown', etc.
            - 'key': key name string (for keyboard events)
            - 'unicode': unicode character (for keyboard events)
            - 'pos': (x, y) tuple (for mouse events)
            - 'button': button number (for mouse events)

        """

    @abstractmethod
    def fill(self, color: tuple[int, int, int]) -> None:
        """Fill entire window with specified RGB color.

        Args:
            color: RGB tuple (0-255, 0-255, 0-255)

        Example:
            display.fill((128, 128, 128))  # Gray background

        """

    @abstractmethod
    def clear(self) -> None:
        """Clear window to black.

        Convenience method equivalent to fill((0, 0, 0)).
        """

    @abstractmethod
    def get_size(self) -> tuple[int, int]:
        """Get window dimensions.

        Returns:
            (width, height) in pixels

        """

    @abstractmethod
    def draw_text(
        self,
        text: str,
        pos: tuple[int, int] | None = None,
        center: bool = False,
        size: int = 24,
        color: tuple[int, int, int] = (255, 255, 255),
    ) -> None:
        """Draw text on window.

        Args:
            text: Text string to display
            pos: (x, y) position in pixels, None if center=True
            center: If True, center text on screen (ignores pos)
            size: Font size in points
            color: RGB color tuple (0-255, 0-255, 0-255)

        Example:
            display.draw_text("Fixate +", center=True, size=48)
            display.draw_text("Press SPACE", pos=(100, 100))

        """

    @abstractmethod
    def draw_image(
        self,
        image_path: str | Path,
        pos: tuple[int, int] | None = None,
        center: bool = False,
        scale: float | None = None,
    ) -> None:
        """Draw image on window.

        Args:
            image_path: Path to image file
            pos: (x, y) position in pixels, None if center=True
            center: If True, center image on screen (ignores pos)
            scale: Scale factor (1.0 = original size, 2.0 = double size, etc.)

        Example:
            display.draw_image("stimulus.png", center=True)
            display.draw_image("cue.png", pos=(100, 100), scale=0.5)

        """

    def wait_for_key(self, key: str | None = None, timeout: float | None = None) -> str | None:
        """Wait for keyboard input.

        Helper method that polls events until key pressed or timeout.

        Args:
            key: Specific key to wait for (e.g., 'space', 'return'), or None for any key
            timeout: Maximum time to wait in seconds, or None to wait indefinitely

        Returns:
            Key name that was pressed, or None if timeout

        """
        start_time = time.time()

        while True:
            events = self.get_events()

            for event in events:
                if event.get("type") == "keydown":
                    pressed_key = event.get("key", "")
                    if key is None or pressed_key.lower() == key.lower():
                        return pressed_key

            if timeout is not None and (time.time() - start_time) > timeout:
                return None

            time.sleep(0.001)

    def wait(self, duration: float) -> None:
        """Wait for specified duration while handling events.

        Prevents event queue buildup during delays.

        Args:
            duration: Time to wait in seconds

        """
        start_time = time.time()

        while time.time() - start_time < duration:
            self.get_events()
            time.sleep(0.001)
