"""Pyglet backend for EyeLink calibration display.

This module provides Pyglet-based visualization for EyeLink calibration and validation.
"""

import io
import logging

import numpy as np
import pyglet
import pylink
from PIL import Image

from .base import CalibrationDisplay
from .targets import generate_target

logger = logging.getLogger(__name__)


class PygletCalibrationDisplay(CalibrationDisplay):
    """Pyglet implementation of EyeLink calibration display."""

    def __init__(self, settings: object, tracker: object) -> None:
        """Initialize pyglet calibration display.

        Args:
            settings: Settings object with configuration
            tracker: EyeLink tracker instance (with display.window attribute)

        """
        super().__init__(settings, tracker)
        self.settings = settings

        # Get pyglet window from tracker
        self.window = tracker.display.window
        self.width = self.window.width
        self.height = self.window.height

        # Create batch for efficient rendering
        self.batch = pyglet.graphics.Batch()

        # Colors (RGBA)
        self.backcolor = (*settings.CAL_BACKGROUND_COLOR, 255)
        self.forecolor = (*settings.CALIBRATION_TEXT_COLOR, 255)

        # Generate target image (convert to pyglet via in-memory bytes)
        pil_image = generate_target(settings)
        buffer = io.BytesIO()
        pil_image.save(buffer, format="PNG")
        buffer.seek(0)
        img = pyglet.image.load("target.png", file=buffer)
        img.anchor_x = img.width // 2
        img.anchor_y = img.height // 2
        self.target_sprite = pyglet.sprite.Sprite(img)

        # Image display variables
        self.rgb_index_array = None
        self.rgb_palette = None
        self.image_title_text = ""
        self.imgstim_size = None
        self.size = None
        self.image_sprite = None
        self.__img__ = None  # Current PIL image being processed

        # Store tracker reference to access display events
        self.tracker = tracker

    def _clear_window(self) -> None:
        """Clear the window with background color."""
        pyglet.gl.glClearColor(self.backcolor[0] / 255.0, self.backcolor[1] / 255.0, self.backcolor[2] / 255.0, 1.0)
        self.window.clear()

    def setup_cal_display(self) -> None:
        """Initialize calibration display with instructions."""
        self._clear_window()

        # Draw instruction text centered on screen (if not empty)
        if self.settings.CALIBRATION_INSTRUCTION_TEXT:
            instructions = pyglet.text.Label(
                self.settings.CALIBRATION_INSTRUCTION_TEXT,
                font_name="Arial",
                font_size=16,
                x=self.width // 2,
                y=self.height // 2,
                anchor_x="center",
                anchor_y="center",
                color=self.forecolor,
            )
            instructions.draw()

        self.window.flip()
        logger.info("Starting Pyglet calibration display.")

    def _draw_target(self, x: int, y: int) -> None:
        """Draw calibration target at given position.

        Args:
            x: X coordinate
            y: Y coordinate (pyglet uses bottom-left origin)

        """
        self.target_sprite.x = x
        self.target_sprite.y = y
        self.target_sprite.draw()

    def exit_cal_display(self) -> None:
        """Clean up calibration display."""
        self.clear_cal_display()

    def close_window(self) -> None:
        """Close the pyglet window."""
        self.window.close()

    def clear_cal_display(self) -> None:
        """Clear calibration display."""
        self._clear_window()
        self.window.flip()

    def erase_cal_target(self) -> None:
        """Remove calibration target from display."""
        self._clear_window()
        self.window.flip()

    def draw_cal_target(self, x: float, y: float) -> None:
        """Draw calibration target at position (x, y).

        Args:
            x: X coordinate in EyeLink coordinates (top-left origin)
            y: Y coordinate in EyeLink coordinates (top-left origin)

        """
        # Convert EyeLink coordinates (top-left origin) to pyglet (bottom-left origin)
        x = int(x)
        y = self.height - int(y)

        self._clear_window()
        self._draw_target(x, y)
        self.window.flip()

    def get_input_key(self) -> list:
        """Get keyboard input and convert to pylink key codes.

        Returns:
            list: List of pylink.KeyInput objects

        """
        # Get events from the display backend (which handles dispatch_events internally)
        events = self.tracker.display.get_events()

        ky = []

        # Map key names from display backend to pylink key constants
        key_name_map = {
            "escape": pylink.ESC_KEY,
            "return": pylink.ENTER_KEY,
            "enter": pylink.ENTER_KEY,
            "space": ord(" "),
            "c": ord("c"),
            "v": ord("v"),
            "a": ord("a"),
            "pageup": pylink.PAGE_UP,
            "pagedown": pylink.PAGE_DOWN,
            "minus": ord("-"),
            "equal": ord("="),
            "up": pylink.CURS_UP,
            "down": pylink.CURS_DOWN,
            "left": pylink.CURS_LEFT,
            "right": pylink.CURS_RIGHT,
        }

        for event in events:
            if event.get("type") == "keydown":
                modifiers = event.get("mod", 0)
                key_name = event.get("key", "").lower()

                # Handle Ctrl+C for graceful shutdown
                if key_name == "c" and (modifiers & pyglet.window.key.MOD_CTRL):
                    self.tracker.display.shutdown_handler(None, None)
                    return ky

                # Skip other keys with Ctrl modifier
                if modifiers & pyglet.window.key.MOD_CTRL:
                    continue

                pylink_key = key_name_map.get(key_name)
                if pylink_key is not None:
                    ky.append(pylink.KeyInput(pylink_key, 0))

        return ky

    def setup_image_display(self, width: int, height: int) -> None:
        """Initialize camera image display.

        Args:
            width: Image width in pixels
            height: Image height in pixels

        """
        self.size = (width, height)
        self.clear_cal_display()

        # Create array to hold image data - always recreate to match current size
        self.rgb_index_array = np.zeros((self.size[1], self.size[0]), dtype=np.uint8)
        self.imgstim_size = None  # Reset to recalculate display size

    def draw_image_line(self, width: int, line: int, totlines: int, buff: object) -> None:
        """Draw camera image line by line.

        Args:
            width: Width of the image line
            line: Current line number (1-indexed)
            totlines: Total number of lines in the image
            buff: Buffer containing pixel data for this line

        This method uses the base class logic for accumulating image lines and drawing overlays.
        Backend-specific code handles conversion to pyglet image and display.

        """
        # Use base class for accumulation and overlays
        image, imgstim_size = self.draw_image_line_base(width, line, totlines, buff)
        if image is None:
            return  # Not all lines received yet

        # Convert PIL image to pyglet image
        # Flip vertically because pyglet uses bottom-left origin
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        raw_data = image.tobytes()
        pyglet_image = pyglet.image.ImageData(image.width, image.height, "RGB", raw_data, pitch=image.width * 3)

        # Clear and draw
        self._clear_window()

        # Center the image
        img_x = (self.width - imgstim_size[0]) // 2
        img_y = (self.height - imgstim_size[1]) // 2
        pyglet_image.blit(img_x, img_y)

        # Draw title text
        if self.image_title_text:
            label = pyglet.text.Label(
                self.image_title_text,
                font_name="Arial",
                font_size=14,
                x=self.width // 2,
                y=self.height - 20,
                anchor_x="center",
                anchor_y="center",
                color=self.forecolor,
            )
            label.draw()

        self.window.flip()

    def exit_image_display(self) -> None:
        """Clean up camera image display."""
        self.clear_cal_display()

    def get_mouse_state(self) -> tuple | None:
        """Get mouse position and button state.

        Returns:
            tuple: ((x, y), button_state) or None

        """
        # Get mouse position from pyglet
        x, y = self.window._mouse_x, self.window._mouse_y  # noqa: SLF001
        y = self.height - y
        buttons = self.window._mouse_buttons if hasattr(self.window, "_mouse_buttons") else 0  # noqa: SLF001
        return ((int(x), int(y)), 1 if buttons else 0)

    def dummynote(self) -> None:
        """Display message for dummy mode (no hardware connection)."""
        self._clear_window()

        label = pyglet.text.Label(
            "Dummy Connection with EyeLink",
            font_name="Arial",
            font_size=24,
            x=self.width // 2,
            y=self.height // 2,
            anchor_x="center",
            anchor_y="center",
            color=self.forecolor,
        )
        label.draw()
        self.window.flip()

        # Wait for key press using display backend events
        while True:
            events = self.tracker.display.get_events()
            for event in events:
                if event.get("type") == "keydown":
                    self._clear_window()
                    self.window.flip()
                    return
