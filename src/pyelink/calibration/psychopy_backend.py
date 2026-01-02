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

    def __init__(self, settings: object, tracker: object, mode: str = "normal") -> None:
        """Initialize PsychoPy calibration display.

        Args:
            settings: Settings object with configuration
            tracker: EyeLink tracker instance (with display.window attribute)
            mode: Calibration mode - "normal", "calibration-only", or "validation-only"

        """
        super().__init__(settings, tracker, mode)
        self.settings = settings

        # Get PsychoPy window from tracker
        self.window = tracker.display.window
        self.window.flip(clearBuffer=True)
        self.mouse = None
        self.width, self.height = self.window.size

        # Store original background color and set calibration colors
        # Convert RGB (0-255) to PsychoPy range (-1 to 1)
        self.original_color = self.window.color
        rgb = settings.cal_background_color
        self.backcolor = [(c / 255.0) * 2 - 1 for c in rgb]
        text_rgb = settings.calibration_text_color
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

        # Overlay drawing variables
        self.overlay_lines = []
        self.overlay_rects = []

    def setup_cal_display(self) -> None:
        """Initialize calibration display with instructions."""
        # Use custom callback if provided
        if self.settings.calibration_instruction_page_callback:
            self.settings.calibration_instruction_page_callback(self.window)
            return

        # Draw instruction text centered on screen (if not empty)
        if self.settings.calibration_instruction_text:
            instr_stim = visual.TextStim(
                self.window,
                self.settings.calibration_instruction_text,
                pos=(0, 0),
                color=tuple(self.txtcol),
                units="pix",
                height=self.settings.calibration_text_font_size,
                font=self.settings.calibration_text_font_name,
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

    def get_input_key(self) -> list:
        """Get keyboard input and convert to pylink key codes.

        Filters 'c' and 'v' keys based on calibration mode:
        - "normal": both 'c' and 'v' enabled
        - "calibration-only": only 'c' enabled, 'v' disabled
        - "validation-only": only 'v' enabled, 'c' disabled

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
            "space": ord(" "),  # PsychoPy might return "space" instead of " "
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
                char, mods = key_info
            else:
                char = key_info
                mods = {}

            # Handle Ctrl+C for graceful shutdown
            if char == "c" and mods.get("ctrl", False):
                self.tracker.display.shutdown_handler(None, None)
                return ky

            # Skip other keys with Ctrl modifier
            if mods.get("ctrl", False):
                continue

            # Filter 'c' and 'v' keys based on mode
            if char == "c" and self.mode in {"validation-only", "camera-setup"}:
                continue  # Skip 'c' in validation-only and camera-setup modes
            if char == "v" and self.mode in {"calibration-only", "camera-setup"}:
                continue  # Skip 'v' in calibration-only and camera-setup modes

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

        # Draw all overlays
        for overlay_line in self.overlay_lines:
            overlay_line.draw()
        for overlay_rect in self.overlay_rects:
            overlay_rect.draw()

        # Draw title text
        if self.image_title_text:
            self._draw_title()

        # Display
        self.window.flip()

        # Clear overlays for next frame
        self.overlay_lines = []
        self.overlay_rects = []

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

    def _eyelink_to_psychopy(self, x: float, y: float) -> tuple[float, float]:
        """Convert EyeLink camera image coordinates to PsychoPy screen coordinates.

        Args:
            x: X coordinate in camera image space (top-left origin, 0 to size[0])
            y: Y coordinate in camera image space (top-left origin, 0 to size[1])

        Returns:
            tuple: (x, y) in PsychoPy space (center origin, positive Y up)

        """
        if self.size is None or self.imgstim_size is None:
            return (0.0, 0.0)

        # Scale from camera image space to display size
        scale_x = self.imgstim_size[0] / self.size[0]
        scale_y = self.imgstim_size[1] / self.size[1]

        x_scaled = x * scale_x
        y_scaled = y * scale_y

        # Convert from top-left origin to center origin
        # Camera image is centered at (0, 0) in PsychoPy
        x_psycho = x_scaled - (self.imgstim_size[0] / 2)
        y_psycho = -y_scaled + (self.imgstim_size[1] / 2)  # Flip Y axis

        return x_psycho, y_psycho

    def draw_line(self, x1: float, y1: float, x2: float, y2: float, colorindex: int) -> None:
        """Draw line on camera image.

        Args:
            x1: X coordinate of start point
            y1: Y coordinate of start point
            x2: X coordinate of end point
            y2: Y coordinate of end point
            colorindex: Pylink color constant

        """
        x1_psycho, y1_psycho = self._eyelink_to_psychopy(x1, y1)
        x2_psycho, y2_psycho = self._eyelink_to_psychopy(x2, y2)
        color = self.getColorFromIndex(colorindex)

        line = visual.Line(
            self.window,
            start=(x1_psycho, y1_psycho),
            end=(x2_psycho, y2_psycho),
            lineColor=color,
            units="pix",
        )
        self.overlay_lines.append(line)

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

        # Scale width and height from camera image space to display size
        scale_x = self.imgstim_size[0] / self.size[0]
        scale_y = self.imgstim_size[1] / self.size[1]

        width_scaled = width * scale_x
        height_scaled = height * scale_y

        # Convert top-left corner to center position for PsychoPy
        center_x = x + width / 2
        center_y = y + height / 2
        center_x_psycho, center_y_psycho = self._eyelink_to_psychopy(center_x, center_y)
        color = self.getColorFromIndex(colorindex)

        rect = visual.Rect(
            self.window,
            width=width_scaled,
            height=height_scaled,
            pos=(center_x_psycho, center_y_psycho),
            lineColor=color,
            fillColor=None,
            units="pix",
        )
        self.overlay_rects.append(rect)

    def _draw_title(self) -> None:
        """Draw title text on camera image."""
        if not self.image_title_text:
            return

        title_stim = visual.TextStim(
            self.window,
            text=self.image_title_text,
            pos=(0, self.height // 2 - 20),
            height=18,
            color=self.txtcol,
            units="pix",
            font="Arial",
        )
        title_stim.draw()

    def dummynote(self) -> None:
        """Display message for dummy mode (no hardware connection)."""
        # Draw Text
        visual.TextStim(
            self.window,
            text="Dummy Connection with EyeLink - Press SPACE to continue",
            color=self.txtcol,
            font="Arial",
        ).draw()
        self.window.flip()

        # Wait for spacebar press (use display backend to handle Ctrl+C)
        waiting = True
        while waiting:
            events = self.tracker.display.get_events()
            for evt in events:
                if evt.get("type") == "keydown" and evt.get("key") == "space":
                    waiting = False
        self.window.flip()
