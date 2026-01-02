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

    def __init__(self, settings: object, tracker: object, mode: str = "normal") -> None:
        """Initialize pyglet calibration display.

        Args:
            settings: Settings object with configuration
            tracker: EyeLink tracker instance (with display.window attribute)
            mode: Calibration mode - "normal", "calibration-only", or "validation-only"

        """
        super().__init__(settings, tracker, mode)
        self.settings = settings

        # Get pyglet window from tracker
        self.window = tracker.display.window
        self.width = self.window.width
        self.height = self.window.height

        # Create batch for efficient rendering
        self.batch = pyglet.graphics.Batch()

        # Colors (RGBA)
        self.backcolor = (*settings.cal_background_color, 255)
        self.forecolor = (*settings.calibration_text_color, 255)

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
        self.img_x = 0  # Image position on screen (set in draw_image_line)
        self.img_y = 0

        # Overlay drawing variables
        self.overlay_batch = pyglet.graphics.Batch()
        self.overlay_shapes = []

        # Store tracker reference to access display events
        self.tracker = tracker

    def _clear_window(self) -> None:
        """Clear the window with background color."""
        pyglet.gl.glClearColor(self.backcolor[0] / 255.0, self.backcolor[1] / 255.0, self.backcolor[2] / 255.0, 1.0)
        self.window.clear()

    def setup_cal_display(self) -> None:
        """Initialize calibration display with instructions."""
        # Use custom callback if provided
        if self.settings.calibration_instruction_page_callback:
            self.settings.calibration_instruction_page_callback(self.window)
            return

        self._clear_window()

        # Draw instruction text centered on screen (if not empty)
        if self.settings.calibration_instruction_text:
            instructions = pyglet.text.Label(
                self.settings.calibration_instruction_text,
                font_name=self.settings.calibration_text_font_name,
                font_size=self.settings.calibration_text_font_size,
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

        Filters 'c' and 'v' keys based on calibration mode:
        - "normal": both 'c' and 'v' enabled
        - "calibration-only": only 'c' enabled, 'v' disabled
        - "validation-only": only 'v' enabled, 'c' disabled

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

                # Filter 'c' and 'v' keys based on mode
                if key_name == "c" and self.mode in {"validation-only", "camera-setup"}:
                    continue  # Skip 'c' in validation-only and camera-setup modes
                if key_name == "v" and self.mode in {"calibration-only", "camera-setup"}:
                    continue  # Skip 'v' in calibration-only and camera-setup modes

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

        # Store image position for overlays
        self.img_x = (self.width - imgstim_size[0]) // 2
        self.img_y = (self.height - imgstim_size[1]) // 2

        # Convert PIL image to pyglet image
        # Flip vertically because pyglet uses bottom-left origin
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        raw_data = image.tobytes()
        pyglet_image = pyglet.image.ImageData(image.width, image.height, "RGB", raw_data, pitch=image.width * 3)

        # Clear window and draw image
        self._clear_window()
        pyglet_image.blit(self.img_x, self.img_y)

        # Draw all overlay shapes
        self.overlay_batch.draw()

        # Draw title text
        if self.image_title_text:
            self._draw_title()

        self.window.flip()

        # Clear overlays for next frame
        self.overlay_shapes = []
        self.overlay_batch = pyglet.graphics.Batch()

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

    def draw_line(self, x1: float, y1: float, x2: float, y2: float, colorindex: int) -> None:
        """Draw line on camera image.

        Args:
            x1: X coordinate of start point
            y1: Y coordinate of start point
            x2: X coordinate of end point
            y2: Y coordinate of end point
            colorindex: Pylink color constant

        """
        if self.size is None or self.imgstim_size is None:
            return

        color = self.getColorFromIndex(colorindex)
        color_rgba = (*color, 255)

        # Scale from camera image space to display size
        scale_x = self.imgstim_size[0] / self.size[0]
        scale_y = self.imgstim_size[1] / self.size[1]

        x1_scaled = x1 * scale_x
        y1_scaled = y1 * scale_y
        x2_scaled = x2 * scale_x
        y2_scaled = y2 * scale_y

        # Convert to pyglet coordinates (bottom-left origin) and add image offset
        y1_pyglet = self.img_y + (self.imgstim_size[1] - y1_scaled)
        y2_pyglet = self.img_y + (self.imgstim_size[1] - y2_scaled)
        x1_offset = self.img_x + x1_scaled
        x2_offset = self.img_x + x2_scaled

        line = pyglet.shapes.Line(
            x1_offset, y1_pyglet, x2_offset, y2_pyglet, thickness=2, color=color_rgba, batch=self.overlay_batch
        )
        self.overlay_shapes.append(line)

    def draw_lozenge(self, x: float, y: float, width: float, height: float, colorindex: int) -> None:
        """Draw rectangle on camera image.

        Args:
            x: X coordinate of top-left corner
            y: Y coordinate of top-left corner
            width: Width of rectangle
            height: Height of rectangle
            colorindex: Pylink color constant

        """
        if self.size is None or self.imgstim_size is None:
            return

        color = self.getColorFromIndex(colorindex)
        color_rgba = (*color, 255)

        # Scale from camera image space to display size
        scale_x = self.imgstim_size[0] / self.size[0]
        scale_y = self.imgstim_size[1] / self.size[1]

        x_scaled = x * scale_x
        y_scaled = y * scale_y
        width_scaled = width * scale_x
        height_scaled = height * scale_y

        # Convert to pyglet coordinates (bottom-left origin) and add image offset
        y_pyglet = self.img_y + (self.imgstim_size[1] - y_scaled - height_scaled)
        x_offset = self.img_x + x_scaled

        # Draw rectangle as 4 lines (pyglet shapes.Rectangle is filled)
        # Top line
        line1 = pyglet.shapes.Line(
            x_offset,
            y_pyglet + height_scaled,
            x_offset + width_scaled,
            y_pyglet + height_scaled,
            thickness=3,
            color=color_rgba,
            batch=self.overlay_batch,
        )
        # Bottom line
        line2 = pyglet.shapes.Line(
            x_offset,
            y_pyglet,
            x_offset + width_scaled,
            y_pyglet,
            thickness=3,
            color=color_rgba,
            batch=self.overlay_batch,
        )
        # Left line
        line3 = pyglet.shapes.Line(
            x_offset,
            y_pyglet,
            x_offset,
            y_pyglet + height_scaled,
            thickness=3,
            color=color_rgba,
            batch=self.overlay_batch,
        )
        # Right line
        line4 = pyglet.shapes.Line(
            x_offset + width_scaled,
            y_pyglet,
            x_offset + width_scaled,
            y_pyglet + height_scaled,
            thickness=3,
            color=color_rgba,
            batch=self.overlay_batch,
        )

        self.overlay_shapes.extend([line1, line2, line3, line4])

    def _draw_title(self) -> None:
        """Draw title text at top center of screen."""
        if not self.image_title_text:
            return

        label = pyglet.text.Label(
            self.image_title_text,
            font_name="Arial",
            font_size=16,
            x=self.width // 2,
            y=self.height - 20,
            anchor_x="center",
            anchor_y="top",
            color=self.forecolor,
        )
        label.draw()

    def dummynote(self) -> None:
        """Display message for dummy mode (no hardware connection)."""
        self._clear_window()

        label = pyglet.text.Label(
            "Dummy Connection with EyeLink - Press SPACE to continue",
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

        # Wait for spacebar press using display backend events
        while True:
            events = self.tracker.display.get_events()
            for event in events:
                if event.get("type") == "keydown" and event.get("key") == "space":
                    self._clear_window()
                    self.window.flip()
                    return
