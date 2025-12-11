"""PsychoPy backend for EyeLink calibration display.

This module provides PsychoPy-based visualization for EyeLink calibration and validation.
"""

import logging
import tempfile
from pathlib import Path

import numpy as np
import pylink
from psychopy import event, visual

from .base import CalibrationDisplay
from .targets import generate_target

logger = logging.getLogger(__name__)


class PsychopyCalibrationDisplay(CalibrationDisplay):
    """PsychoPy implementation of EyeLink calibration display."""

    def __init__(self, settings: object, tracker: object) -> None:
        """Initialize PsychoPy calibration display.

        Args:
            settings: Settings object with configuration
            tracker: EyeLink tracker instance (with display.window attribute)

        """
        super().__init__(settings, tracker)
        self.settings = settings

        # Get PsychoPy window from tracker
        self.window = tracker.display.window
        self.window.flip(clearBuffer=True)
        self.mouse = None
        self.width, self.height = self.window.size

        # Store original background color and set calibration colors
        # Convert RGB (0-255) to PsychoPy range (-1 to 1)
        self.original_color = self.window.color
        rgb = settings.CAL_BACKGROUND_COLOR
        self.backcolor = [(c / 255.0) * 2 - 1 for c in rgb]
        text_rgb = settings.CALIBRATION_TEXT_COLOR
        self.txtcol = [(c / 255.0) * 2 - 1 for c in text_rgb]

        # Set window to calibration background color
        self.window.color = self.backcolor

        # Generate target image (pass PIL image directly - PsychoPy handles it properly)
        pil_image = generate_target(settings)
        self.target_image = visual.ImageStim(
            self.window,
            image=pil_image,  # PIL image, not numpy array
            units="pix",
        )

        # Image drawing variables (used for camera display)
        self.rgb_index_array = None
        self.rgb_pallete = None
        self.image_title_text = ""
        self.imgstim_size = None
        self.eye_image = None
        self.lineob = None
        self.loz = None

    def setup_cal_display(self) -> None:
        """Initialize calibration display with instructions."""
        # Draw instruction text centered on screen (if not empty)
        if self.settings.CALIBRATION_INSTRUCTION_TEXT:
            instr_stim = visual.TextStim(
                self.window,
                self.settings.CALIBRATION_INSTRUCTION_TEXT,
                pos=(0, 0),
                color=tuple(self.txtcol),
                units="pix",
                height=18,
                font="Arial",
            )
            instr_stim.draw()

        self.window.flip()

    def exit_cal_display(self) -> None:
        """Clean up calibration display and restore original window color."""
        # Restore original window background color
        self.window.color = self.original_color
        self.window.flip(clearBuffer=True)

    def close_window(self) -> None:
        """Close the psychopy window."""
        self.window.close()

    def clear_cal_display(self) -> None:
        """Clear calibration display."""
        self.setup_cal_display()

    def erase_cal_target(self) -> None:
        """Remove calibration target from display."""
        self.window.flip()

    def draw_cal_target(self, x: float, y: float) -> None:
        """Draw calibration target at position (x, y).

        Args:
            x: X coordinate in EyeLink coordinates (top-left origin)
            y: Y coordinate in EyeLink coordinates (top-left origin)

        """
        # Convert to PsychoPy coordinates (center origin, positive Y up)
        x -= self.sres[0] / 2
        y = -(y - (self.sres[1] / 2))

        self.target_image.pos = (x, y)
        self.target_image.draw()
        self.window.flip()

    def get_input_key(self) -> list:  # noqa: PLR6301
        """Get keyboard input and convert to pylink key codes.

        Returns:
            list: List of pylink.KeyInput objects

        """
        ky = []
        v = event.getKeys(modifiers=True)

        # Map PsychoPy key names to pylink key constants
        key_map = {
            "escape": pylink.ESC_KEY,
            "return": pylink.ENTER_KEY,
            " ": ord(" "),
            "c": ord("c"),
            "v": ord("v"),
            "a": ord("a"),
            "pageup": pylink.PAGE_UP,
            "pagedown": pylink.PAGE_DOWN,
            "-": ord("-"),
            "=": ord("="),
            "up": pylink.CURS_UP,
            "down": pylink.CURS_DOWN,
            "left": pylink.CURS_LEFT,
            "right": pylink.CURS_RIGHT,
        }

        for key_info in v:
            # key_info is (key_name, modifiers_dict) or just key_name
            if isinstance(key_info, tuple):
                char, _mods = key_info
            else:
                char = key_info

            # Lookup key in the general key map
            pylink_key = key_map.get(char)
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
        self.last_mouse_state = -1

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

        """
        # Accumulate image lines
        if not self._accumulate_image_line(width, line, totlines, buff):
            return  # Not all lines received yet

        # Build and scale RGB image
        image, imgstim_size = self._get_processed_pil_image()

        # Save image as a temporary file
        tfile = Path(tempfile.gettempdir()) / "_eleye.png"
        image.save(str(tfile), "PNG")

        # Need this for target distance to show up
        self.__img__ = image
        self.draw_cross_hair()
        self.__img__ = None

        # Create or update eye image
        if self.eye_image is None:
            self.eye_image = visual.ImageStim(self.window, tfile, size=imgstim_size, units="pix")
        else:
            self.eye_image.setImage(tfile)

        # Redraw the Camera Setup Mode graphics
        self.eye_image.draw()
        if self.image_title_text:
            title_stim = visual.TextStim(
                self.window,
                text=self.image_title_text,
                pos=(0, self.height // 2 - 15),
                height=18,
                color=self.txtcol,
                units="pix",
                font="Arial",
            )
            title_stim.draw()

        # Display
        self.window.flip()

    def set_image_palette(self, r: object, g: object, b: object) -> None:
        """Set color palette for camera image.

        Args:
            r: Red channel values
            g: Green channel values
            b: Blue channel values

        """
        # Call parent implementation
        super().set_image_palette(r, g, b)
        # PsychoPy-specific: clear display when palette is set
        self.clear_cal_display()

    def exit_image_display(self) -> None:
        """Clean up camera image display."""
        self.clear_cal_display()

    def getColorFromIndex(self, colorindex: int) -> tuple:  # noqa: N802, PLR6301
        """Map pylink color constants to PsychoPy color values.

        Args:
            colorindex: Pylink color constant

        Returns:
            tuple: (R, G, B) in PsychoPy color space (-1 to 1)

        """
        if colorindex in {pylink.CR_HAIR_COLOR, pylink.PUPIL_HAIR_COLOR}:
            return (1, 1, 1)
        if colorindex == pylink.PUPIL_BOX_COLOR:
            return (-1, 1, -1)
        if colorindex in {pylink.SEARCH_LIMIT_BOX_COLOR, pylink.MOUSE_CURSOR_COLOR}:
            return (1, -1, -1)
        return (-1, -1, -1)

    def get_mouse_state(self) -> tuple | None:
        """Get mouse position and button state."""
        if self.mouse is None:
            self.mouse = event.Mouse(win=self.window)

        pos = self.mouse.getPos()
        buttons = self.mouse.getPressed()

        x = int(pos[0] + (self.sres[0] / 2))
        y = int(pos[1] + (self.sres[1] / 2))

        button_state = 1 if any(buttons) else 0

        return ((x, y), button_state)

    def dummynote(self) -> None:
        """Display message for dummy mode (no hardware connection)."""
        # Draw Text
        visual.TextStim(self.window, text="Dummy Connection with EyeLink", color=self.txtcol, font="Arial").draw()
        self.window.flip()

        # Wait for key press
        event.waitKeys()
        self.window.flip()
