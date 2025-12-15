"""PsychoPy display backend implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pyglet
from psychopy import event, visual

from .base import BaseDisplay

if TYPE_CHECKING:
    from pathlib import Path


class PsychopyDisplay(BaseDisplay):
    """PsychoPy implementation of display window management.

    Manages PsychoPy Window creation, event handling, and drawing operations.
    Provides both direct access to visual.Window and backend-agnostic helpers.
    """

    @property
    def backend_name(self) -> str:
        """Get backend identifier."""
        return "psychopy"

    def _create_window(self, settings: object) -> visual.Window:  # noqa: PLR6301
        """Create PsychoPy window.

        Args:
            settings: Settings object with SCREEN_RES, FULLSCREEN, DISPLAY_INDEX

        Returns:
            psychopy.visual.Window object

        """
        display = pyglet.canvas.get_display()
        screens = display.get_screens()

        screen_index = 0 if len(screens) <= settings.display_index else settings.display_index

        window = visual.Window(
            size=settings.screen_res,
            fullscr=settings.fullscreen,
            screen=screen_index,
            units="pix",
            color=[0, 0, 0],
            allowGUI=False,
        )

        return window

    def flip(self) -> None:
        """Update display."""
        self._window.flip()

    def close(self) -> None:
        """Close PsychoPy window."""
        self._window.close()

    def get_events(self) -> list[dict[str, Any]]:
        """Get PsychoPy events as unified dicts.

        Returns:
            List of event dicts with unified keys

        """
        events = []
        keys = event.getKeys(timeStamped=False, modifiers=True)

        for key_info in keys:
            # key_info is tuple (key_name, modifiers_dict) when modifiers=True
            key_name = key_info[0] if isinstance(key_info, tuple) else key_info
            modifiers = key_info[1] if isinstance(key_info, tuple) and len(key_info) > 1 else {}

            # Check for Ctrl+C (when window has focus, SIGINT won't fire)
            if key_name == "c" and modifiers.get("ctrl", False):
                if self.shutdown_handler:
                    self.shutdown_handler(None, None)  # Call signal handler directly
                return events  # Return immediately after shutdown initiated

            event_dict = {
                "type": "keydown",
                "key": key_name,
                "unicode": key_name if len(key_name) == 1 else "",
            }
            events.append(event_dict)

        return events

    def fill(self, color: tuple[int, int, int]) -> None:
        """Fill window with color.

        PsychoPy uses normalized RGB (-1 to 1), so we convert from 0-255.

        Args:
            color: RGB tuple (0-255, 0-255, 0-255)

        """
        normalized_color = [(c / 255.0) * 2 - 1 for c in color]
        self._window.color = normalized_color
        self._window.flip()

    def clear(self) -> None:
        """Clear window to black."""
        self._window.color = [-1, -1, -1]
        self._window.flip()

    def get_size(self) -> tuple[int, int]:
        """Get window dimensions.

        Returns:
            (width, height) in pixels

        """
        return tuple(self._window.size)

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
            pos: (x, y) position in pixels
            center: If True, center text on screen
            size: Font size in points
            color: RGB color tuple (0-255, 0-255, 0-255)

        """
        normalized_color = [(c / 255.0) * 2 - 1 for c in color]

        text_pos = (0, 0) if center else pos

        text_stim = visual.TextStim(
            self._window,
            text=text,
            pos=text_pos,
            height=size,
            color=normalized_color,
            units="pix",
        )

        text_stim.draw()

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
            pos: (x, y) position in pixels
            center: If True, center image on screen
            scale: Scale factor for image size

        """
        image_pos = (0, 0) if center else pos

        image_stim = visual.ImageStim(self._window, image=str(image_path), pos=image_pos, units="pix")

        if scale is not None:
            original_size = image_stim.size
            image_stim.size = (original_size[0] * scale, original_size[1] * scale)

        image_stim.draw()
