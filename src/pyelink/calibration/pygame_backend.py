"""Pygame backend for EyeLink calibration display.

This module provides Pygame-based visualization for EyeLink calibration and validation.
"""

import logging

import numpy as np
import pygame
import pylink

from .base import CalibrationDisplay
from .targets import generate_target

logger = logging.getLogger(__name__)


class PygameCalibrationDisplay(CalibrationDisplay):
    """Pygame implementation of EyeLink calibration display."""

    def __init__(self, settings: object, tracker: object, mode: str = "normal") -> None:
        """Initialize pygame calibration display.

        Args:
            settings: Settings object with configuration
            tracker: EyeLink tracker instance (with display.window attribute)
            mode: Calibration mode - "normal", "calibration-only", or "validation-only"

        """
        super().__init__(settings, tracker, mode)
        self.settings = settings

        # Get pygame display surface from tracker
        self.window = tracker.display.window
        self.width, self.height = self.window.get_size()

        # Colors
        self.backcolor = settings.cal_background_color
        self.forecolor = settings.calibration_text_color
        logger.info("PygameCalibrationDisplay initialized.")

        # Generate target image
        pil_image = generate_target(settings)
        self.target_image = pygame.image.fromstring(
            pil_image.tobytes(), pil_image.size, pil_image.mode
        ).convert_alpha()

        # Image display variables
        self.rgb_index_array = None
        self.rgb_palette = None
        self.image_title_text = ""
        self.imgstim_size = None
        self.size = None
        self.__img__ = None  # Current PIL image being processed
        self.cam_img = None  # Pygame surface for camera image with overlays

        # Store overlay drawing commands to replay after image is created
        self.overlay_lines = []
        self.overlay_rects = []

        # Font for text display
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 24)
        self.small_font = pygame.font.SysFont("Arial", 18)
        self.tiny_font = pygame.font.SysFont("Courier New", 11)

    def setup_cal_display(self) -> None:
        """Initialize calibration display with instructions."""
        # Use custom callback if provided
        if self.settings.calibration_instruction_page_callback:
            self.settings.calibration_instruction_page_callback(self.window)
            return

        self.window.fill(self.backcolor)

        # Draw instruction text centered on screen (if not empty)
        if self.settings.calibration_instruction_text:
            font = pygame.font.SysFont(
                self.settings.calibration_text_font_name,
                self.settings.calibration_text_font_size,
            )
            instr_surface = font.render(self.settings.calibration_instruction_text, True, self.forecolor)
            instr_rect = instr_surface.get_rect(center=(self.width // 2, self.height // 2))
            self.window.blit(instr_surface, instr_rect)

        pygame.display.flip()

    def exit_cal_display(self) -> None:
        """Clean up calibration display."""
        self.clear_cal_display()

    def close_window(self) -> None:  # noqa: PLR6301
        """Close the pygame window.

        Note:
            Must be instance method to match CalibrationDisplay interface.

        """
        pygame.quit()

    def clear_cal_display(self) -> None:
        """Clear calibration display."""
        self.window.fill(self.backcolor)
        pygame.display.flip()

    def erase_cal_target(self) -> None:
        """Remove calibration target from display."""
        self.window.fill(self.backcolor)
        pygame.display.flip()

    def draw_cal_target(self, x: float, y: float) -> None:
        """Draw calibration target at position (x, y).

        Args:
            x: X coordinate in EyeLink coordinates (top-left origin)
            y: Y coordinate in EyeLink coordinates (top-left origin)

        """
        x, y = int(x), int(y)
        self.window.fill(self.backcolor)
        img_rect = self.target_image.get_rect(center=(x, y))
        self.window.blit(self.target_image, img_rect)
        pygame.display.flip()

    def get_input_key(self) -> list:
        """Get keyboard input and convert to pylink key codes.

        Filters 'c' and 'v' keys based on calibration mode:
        - "normal": both 'c' and 'v' enabled
        - "calibration-only": only 'c' enabled, 'v' disabled
        - "validation-only": only 'v' enabled, 'c' disabled

        Note:
            Must be instance method to match CalibrationDisplay interface.

        Returns:
            list: List of pylink.KeyInput objects

        """
        ky = []

        # Map pygame key constants to pylink key constants
        key_map = {
            pygame.K_ESCAPE: pylink.ESC_KEY,
            pygame.K_RETURN: pylink.ENTER_KEY,
            pygame.K_SPACE: ord(" "),
            pygame.K_c: ord("c"),
            pygame.K_v: ord("v"),
            pygame.K_a: ord("a"),
            pygame.K_PAGEUP: pylink.PAGE_UP,
            pygame.K_PAGEDOWN: pylink.PAGE_DOWN,
            pygame.K_MINUS: ord("-"),
            pygame.K_EQUALS: ord("="),
            pygame.K_UP: pylink.CURS_UP,
            pygame.K_DOWN: pylink.CURS_DOWN,
            pygame.K_LEFT: pylink.CURS_LEFT,
            pygame.K_RIGHT: pylink.CURS_RIGHT,
        }

        for event in pygame.event.get(pygame.KEYDOWN):
            # Handle Ctrl+C for graceful shutdown
            if event.key == pygame.K_c and (event.mod & pygame.KMOD_CTRL):
                self.tracker.display.shutdown_handler(None, None)
                return ky

            # Skip other keys with Ctrl modifier
            if event.mod & pygame.KMOD_CTRL:
                continue

            # Filter 'c' and 'v' keys based on mode
            if event.key == pygame.K_c and self.mode in {"validation-only", "camera-setup"}:
                continue  # Skip 'c' in validation-only and camera-setup modes
            if event.key == pygame.K_v and self.mode in {"calibration-only", "camera-setup"}:
                continue  # Skip 'v' in calibration-only and camera-setup modes

            # Lookup key in the general key map
            pylink_key = key_map.get(event.key)
            if pylink_key is not None:
                ky.append(pylink.KeyInput(pylink_key, 0))

        # Also process quit events
        for _event in pygame.event.get(pygame.QUIT):
            ky.append(pylink.KeyInput(pylink.ESC_KEY, 0))

        return ky

    def setup_image_display(self, width: int, height: int) -> None:
        """Initialize camera image display.

        Args:
            width: Image width in pixels
            height: Image height in pixels

        """
        self.size = (width, height)
        self.clear_cal_display()

        # Create array to hold image data - will be resized in draw_image_line if needed
        self.rgb_index_array = np.zeros((self.size[1], self.size[0]), dtype=np.uint8)
        self.imgstim_size = None

    def draw_image_line(self, width: int, line: int, totlines: int, buff: object) -> None:
        """Draw camera image line by line.

        The EyeLink sends the camera image line-by-line. This method receives each line and accumulates them.
        When line == totlines, the complete image is ready and overlays (crosshairs, etc.) are drawn.
        Uses base class for accumulation and overlays, then displays using pygame.

        Args:
            width: Width of the image line
            line: Current line number (1-indexed)
            totlines: Total number of lines in the image
            buff: Buffer containing pixel data for this line

        """
        # Accumulate image lines and draw overlays using base class
        image, imgstim_size = self.draw_image_line_base(width, line, totlines, buff)
        if image is None:
            return  # Not all lines received yet

        # Convert PIL image to pygame surface for display
        image_data = image.tobytes()
        mode = image.mode
        size = image.size
        if mode == "RGB":
            self.cam_img = pygame.image.fromstring(image_data, size, mode)
        else:
            image = image.convert("RGB")
            image_data = image.tobytes()
            self.cam_img = pygame.image.fromstring(image_data, size, "RGB")

        # Replay all overlay drawings on the new image
        scale_x = self.cam_img.get_width() / self.size[0]
        scale_y = self.cam_img.get_height() / self.size[1]

        # Draw all lines
        for x1, y1, x2, y2, colorindex in self.overlay_lines:
            x1_scaled = int(x1 * scale_x)
            y1_scaled = int(y1 * scale_y)
            x2_scaled = int(x2 * scale_x)
            y2_scaled = int(y2 * scale_y)
            color = self.getColorFromIndex(colorindex)
            pygame.draw.line(self.cam_img, color, (x1_scaled, y1_scaled), (x2_scaled, y2_scaled), 2)

        # Draw all rectangles
        for rect_x, rect_y, rect_width, rect_height, rect_colorindex in self.overlay_rects:
            x_scaled = int(rect_x * scale_x)
            y_scaled = int(rect_y * scale_y)
            width_scaled = int(rect_width * scale_x)
            height_scaled = int(rect_height * scale_y)
            color = self.getColorFromIndex(rect_colorindex)
            pygame.draw.rect(self.cam_img, color, (x_scaled, y_scaled, width_scaled, height_scaled), 3)

        # Clear overlay lists for next frame
        self.overlay_lines = []
        self.overlay_rects = []

        # Store image position for coordinate offset in overlays
        self.img_x = (self.width - imgstim_size[0]) // 2
        self.img_y = (self.height - imgstim_size[1]) // 2

        # Clear window and draw image centered
        self.window.fill(self.backcolor)
        self.window.blit(self.cam_img, (self.img_x, self.img_y))

        # Draw title/info text if present
        if self.image_title_text:
            self._draw_title()

        # Update display
        pygame.display.flip()

    def exit_image_display(self) -> None:
        """Clean up camera image display."""
        self.clear_cal_display()

    @staticmethod
    def get_mouse_state() -> tuple | None:
        """Get mouse position and button state.

        Returns:
            tuple: ((x, y), button_state) or None

        """
        pos = pygame.mouse.get_pos()
        buttons = pygame.mouse.get_pressed()
        return (pos, 1 if buttons[0] else 0)

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

        # Store the drawing command to replay after image is created
        self.overlay_lines.append((x1, y1, x2, y2, colorindex))

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

        # Store the drawing command to replay after image is created
        self.overlay_rects.append((x, y, width, height, colorindex))

    def _draw_title(self) -> None:
        """Draw title text at top center of screen."""
        if not self.image_title_text:
            return

        text_surface = self.small_font.render(self.image_title_text, False, self.forecolor)
        text_rect = text_surface.get_rect(center=(self.width // 2, 20))
        self.window.blit(text_surface, text_rect)

    def dummynote(self) -> None:
        """Display message for dummy mode (no hardware connection)."""
        self.window.fill(self.backcolor)
        text_surface = self.font.render(
            "Dummy Connection with EyeLink - Press SPACE to continue", True, self.forecolor
        )
        text_rect = text_surface.get_rect(center=(self.width // 2, self.height // 2))
        self.window.blit(text_surface, text_rect)
        pygame.display.flip()

        # Wait for spacebar press (use display backend to handle Ctrl+C)
        waiting = True
        while waiting:
            events = self.tracker.display.get_events()
            for event in events:
                if (event.get("type") == "keydown" and event.get("key") == "space") or event.get("type") == "quit":
                    waiting = False

        self.window.fill(self.backcolor)
        pygame.display.flip()
