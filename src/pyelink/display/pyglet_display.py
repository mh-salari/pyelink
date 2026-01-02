"""Pyglet display backend implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pyglet

from .base import BaseDisplay

if TYPE_CHECKING:
    from pathlib import Path


class PygletDisplay(BaseDisplay):
    """Pyglet implementation of display window management.

    Manages pyglet Window creation, event handling, and drawing operations.
    Provides both direct access to pyglet.window.Window and backend-agnostic helpers.
    """

    def __init__(self, settings: object, shutdown_handler: object = None) -> None:
        """Initialize pyglet display.

        Args:
            settings: Settings object with display configuration
            shutdown_handler: Callable for graceful shutdown (optional)

        """
        super().__init__(settings, shutdown_handler=shutdown_handler)
        self._event_queue = []
        self._setup_event_handlers()

    @property
    def backend_name(self) -> str:
        """Get backend identifier."""
        return "pyglet"

    def _create_window(self, settings: object) -> pyglet.window.Window:  # noqa: PLR6301
        """Create pyglet window.

        Args:
            settings: Settings object with SCREEN_RES, FULLSCREEN, DISPLAY_INDEX

        Returns:
            pyglet.window.Window object

        """
        display = pyglet.display.get_display()
        screens = display.get_screens()

        screen = screens[0] if len(screens) <= settings.display_index else screens[settings.display_index]

        window = pyglet.window.Window(
            width=settings.screen_res[0],
            height=settings.screen_res[1],
            fullscreen=settings.fullscreen,
            screen=screen,
            caption="PyELink - Pyglet Backend",
        )

        return window

    def _setup_event_handlers(self) -> None:
        """Setup pyglet event handlers to capture events."""

        @self._window.event
        def on_key_press(symbol: int, modifiers: int) -> None:
            """Handle key press events."""
            # Check for Ctrl+C (when window has focus, SIGINT won't fire)
            if symbol == pyglet.window.key.C and (modifiers & pyglet.window.key.MOD_CTRL):
                # Call shutdown handler directly
                if self.shutdown_handler:
                    self.shutdown_handler(None, None)
                return

            key_name = pyglet.window.key.symbol_string(symbol).lower().replace("_", "")
            self._event_queue.append({
                "type": "keydown",
                "key": key_name,
                "unicode": chr(symbol) if 32 <= symbol < 127 else "",
                "mod": modifiers,
            })

        @self._window.event
        def on_key_release(symbol: int, modifiers: int) -> None:
            """Handle key release events."""
            key_name = pyglet.window.key.symbol_string(symbol).lower().replace("_", "")
            self._event_queue.append({"type": "keyup", "key": key_name, "mod": modifiers})

        @self._window.event
        def on_mouse_press(x: int, y: int, button: int, modifiers: int) -> None:  # noqa: ARG001
            """Handle mouse button press events."""
            self._event_queue.append({"type": "mousebuttondown", "pos": (x, y), "button": button})

        @self._window.event
        def on_mouse_release(x: int, y: int, button: int, modifiers: int) -> None:  # noqa: ARG001
            """Handle mouse button release events."""
            self._event_queue.append({"type": "mousebuttonup", "pos": (x, y), "button": button})

        @self._window.event
        def on_close() -> None:
            """Handle window close event."""
            self._event_queue.append({"type": "quit"})

    def flip(self) -> None:
        """Update display."""
        self._window.flip()

    def close(self) -> None:
        """Close pyglet window."""
        # Exit fullscreen mode first
        if self._window.fullscreen:
            self._window.set_fullscreen(False)
        self._window.close()

    def get_events(self) -> list[dict[str, Any]]:
        """Get pyglet events as unified dicts.

        Returns:
            List of event dicts with unified keys

        """
        self._window.dispatch_events()

        events = self._event_queue.copy()
        self._event_queue.clear()

        return events

    def fill(self, color: tuple[int, int, int]) -> None:
        """Fill window with color.

        Args:
            color: RGB tuple (0-255, 0-255, 0-255)

        """
        self._window.clear()
        pyglet.gl.glClearColor(color[0] / 255.0, color[1] / 255.0, color[2] / 255.0, 1.0)
        pyglet.gl.glClear(pyglet.gl.GL_COLOR_BUFFER_BIT)

    def clear(self) -> None:
        """Clear window to black."""
        self._window.clear()

    def get_size(self) -> tuple[int, int]:
        """Get window dimensions.

        Returns:
            (width, height) in pixels

        """
        return (self._window.width, self._window.height)

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
            color: RGB color tuple

        """
        if center:
            text_pos = (self._window.width // 2, self._window.height // 2)
            anchor_x = "center"
            anchor_y = "center"
        else:
            text_pos = pos
            anchor_x = "left"
            anchor_y = "bottom"

        label = pyglet.text.Label(
            text,
            font_name="Arial",
            font_size=size,
            x=text_pos[0],
            y=text_pos[1],
            anchor_x=anchor_x,
            anchor_y=anchor_y,
            color=(*color, 255),
        )

        label.draw()

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
        image = pyglet.image.load(str(image_path))

        if scale is not None:
            image.width = int(image.width * scale)
            image.height = int(image.height * scale)

        if center:
            image.anchor_x = image.width // 2
            image.anchor_y = image.height // 2
            sprite_pos = (self._window.width // 2, self._window.height // 2)
        else:
            sprite_pos = pos

        sprite = pyglet.sprite.Sprite(image, x=sprite_pos[0], y=sprite_pos[1])
        sprite.draw()
