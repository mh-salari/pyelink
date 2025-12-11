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

    def __init__(self, settings: object, tracker: object) -> None:
        """Initialize pygame calibration display.

        Args:
            settings: Settings object with configuration
            tracker: EyeLink tracker instance (with display.window attribute)

        """
        super().__init__(settings, tracker)
        self.settings = settings

        # Get pygame display surface from tracker
        self.window = tracker.display.window
        self.width, self.height = self.window.get_size()

        # Colors
        self.backcolor = settings.CAL_BACKGROUND_COLOR
        self.forecolor = settings.CALIBRATION_TEXT_COLOR
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

        # Font for text display
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 24)
        self.small_font = pygame.font.SysFont("Arial", 18)

    def setup_cal_display(self) -> None:
        """Initialize calibration display with instructions."""
        self.window.fill(self.backcolor)

        # Draw instruction text centered on screen (if not empty)
        if self.settings.CALIBRATION_INSTRUCTION_TEXT:
            instr_surface = self.small_font.render(self.settings.CALIBRATION_INSTRUCTION_TEXT, True, self.forecolor)
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
            pygame_image = pygame.image.fromstring(image_data, size, mode)
        else:
            image = image.convert("RGB")
            image_data = image.tobytes()
            pygame_image = pygame.image.fromstring(image_data, size, "RGB")

        # Clear window and draw image centered
        self.window.fill(self.backcolor)
        img_x = (self.width - imgstim_size[0]) // 2
        img_y = (self.height - imgstim_size[1]) // 2
        self.window.blit(pygame_image, (img_x, img_y))

        # Draw title/info text if present
        if self.image_title_text:
            text_surface = self.small_font.render(self.image_title_text, True, self.forecolor)
            text_rect = text_surface.get_rect(center=(self.width // 2, 20))
            self.window.blit(text_surface, text_rect)

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

    def dummynote(self) -> None:
        """Display message for dummy mode (no hardware connection)."""
        self.window.fill(self.backcolor)
        text_surface = self.font.render("Dummy Connection with EyeLink", True, self.forecolor)
        text_rect = text_surface.get_rect(center=(self.width // 2, self.height // 2))
        self.window.blit(text_surface, text_rect)
        pygame.display.flip()

        # Wait for key press
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type in {pygame.KEYDOWN, pygame.QUIT}:
                    waiting = False

        self.window.fill(self.backcolor)
        pygame.display.flip()
