"""Abstract base class for calibration display backends.

This module defines the interface that all calibration backends must implement.
Backends provide visualization during tracker calibration and validation.
"""

import logging
from abc import ABC, abstractmethod

import numpy as np
import pylink
from PIL import Image

from .. import audio

logger = logging.getLogger(__name__)


class CalibrationDisplay(pylink.EyeLinkCustomDisplay, ABC):
    """Abstract base class for EyeLink calibration displays.

    All backend implementations must inherit from this class and implement
    the required abstract methods. This class defines the interface for
    drawing calibration targets, handling input, and displaying the eye camera view.
    """

    def __init__(self, settings: object, tracker: object, mode: str = "normal") -> None:
        """Initialize calibration display.

        Args:
            settings: Settings object with configuration
            tracker: EyeLink tracker instance
            mode: Calibration mode - "normal", "calibration-only", or "validation-only"

        """
        pylink.EyeLinkCustomDisplay.__init__(self)
        self.settings = settings
        self.sres = settings.screen_res
        self.mode = mode
        self.set_tracker(tracker)

    def set_tracker(self, tracker: object) -> None:
        """Configure tracker for calibration.

        Args:
            tracker: EyeLinkDevice instance

        """
        self.tracker = tracker
        self.tracker_version = tracker.get_tracker_version()
        if self.tracker_version >= 3:
            # enable_search_limits: Enables use/display of global search limits (ON or OFF)
            # track_search_limits: Enables tracking of pupil to global search limits (ON or OFF)
            self.tracker.send_command(f"enable_search_limits={self.settings.enable_search_limits}")
            self.tracker.send_command(f"track_search_limits={self.settings.track_search_limits}")

            # autothreshold_click: Auto-threshold on mouse click on setup mode image
            # autothreshold_repeat: Allows repeat of auto-threshold if pupil not centered on first
            self.tracker.send_command(f"autothreshold_click={self.settings.autothreshold_click}")
            self.tracker.send_command(f"autothreshold_repeat={self.settings.autothreshold_repeat}")

            # enable_camera_position_detect: Allows camera position detect on click/auto-threshold in setup mode (TRUE or FALSE)
            self.tracker.send_command(f"enable_camera_position_detect={self.settings.enable_camera_position_detect}")

    @abstractmethod
    def setup_cal_display(self) -> None:
        """Initialize calibration display.

        Called when entering calibration mode. Should clear the display
        and show any initial instructions or setup.
        """

    @abstractmethod
    def exit_cal_display(self) -> None:
        """Clean up calibration display.

        Called when exiting calibration mode.
        """

    @abstractmethod
    def clear_cal_display(self) -> None:
        """Clear the calibration display.

        Typically called between calibration points.
        """

    @abstractmethod
    def draw_cal_target(self, x: float, y: float) -> None:
        """Draw calibration target at position (x, y).

        Args:
            x: X coordinate in EyeLink screen coordinates (top-left origin)
            y: Y coordinate in EyeLink screen coordinates (top-left origin)

        Note:
            Coordinates are in EyeLink space (top-left origin, positive Y down).
            Backends must convert to their native coordinate system.

        """

    @abstractmethod
    def erase_cal_target(self) -> None:
        """Remove calibration target from display.

        Called after participant has fixated the target.
        """

    @abstractmethod
    def setup_image_display(self, width: int, height: int) -> None:
        """Initialize camera image display.

        Called before displaying the eye camera feed.

        Args:
            width: Image width in pixels
            height: Image height in pixels

        """

    def image_title(self, text: str) -> None:
        """Display title/info text on camera view.

        Args:
            text: Text to display (typically pupil/CR information)

        """
        self.image_title_text = text

    def getColorFromIndex(self, colorindex: int) -> tuple[int, int, int]:  # noqa: N802, PLR6301
        """Map pylink color constants to RGB tuples.

        Args:
            colorindex: Pylink color constant

        Returns:
            tuple: (R, G, B) values in range 0-255

        """
        color_map = {
            pylink.CR_HAIR_COLOR: (255, 255, 255),  # Corneal reflection crosshair
            pylink.PUPIL_HAIR_COLOR: (255, 255, 255),  # Pupil crosshair
            pylink.PUPIL_BOX_COLOR: (0, 255, 0),  # Pupil box (green)
            pylink.SEARCH_LIMIT_BOX_COLOR: (255, 0, 0),  # Search limit box (red)
            pylink.MOUSE_CURSOR_COLOR: (255, 0, 0),  # Mouse cursor (red)
        }
        return color_map.get(colorindex, (128, 128, 128))

    def set_image_palette(self, r: object, g: object, b: object) -> None:
        """Set color palette for camera image.

        Args:
            r: Red channel values (list/array)
            g: Green channel values (list/array)
            b: Blue channel values (list/array)

        """
        sz = len(r)
        self.rgb_palette = np.zeros((sz, 3), dtype=np.uint8)
        for i in range(sz):
            self.rgb_palette[i] = (int(r[i]), int(g[i]), int(b[i]))

    def draw_image_line_base(self, width: int, line: int, totlines: int, buff: object) -> tuple:
        """The EyeLink sends the camera image line-by-line. This method receives each line and accumulates them.

        When line == totlines, the complete image is ready and overlays (crosshairs, etc.) are drawn.

        Args:
            width: Width of the image line
            line: Current line number (1-indexed)
            totlines: Total number of lines in the image
            buff: Buffer containing pixel data for this line

        Returns:
            tuple: (image, imgstim_size) if all lines received, else (None, None)

        """
        if not self._accumulate_image_line(width, line, totlines, buff):
            return None, None
        image, imgstim_size = self._get_processed_pil_image()
        self.__img__ = image
        self.draw_cross_hair()
        self.__img__ = None
        return image, imgstim_size

    def _accumulate_image_line(self, width: int, line: int, totlines: int, buff: object) -> bool:
        """Accumulate camera image line by line.

        Args:
            width: Width of the image line
            line: Current line number (1-indexed)
            totlines: Total number of lines in the image
            buff: Buffer containing pixel data for this line

        Returns:
            bool: True if all lines received, False otherwise

        """
        if self.rgb_index_array is None or self.rgb_index_array.shape != (totlines, width):
            self.size = (width, totlines)
            self.rgb_index_array = np.zeros((totlines, width), dtype=np.uint8)
            self.imgstim_size = None

        for i in range(width):
            self.rgb_index_array[line - 1, i] = buff[i]

        return line == totlines

    def _build_rgb_image_from_palette(self) -> Image.Image:
        """Convert indexed image array to RGB using palette.

        Returns:
            PIL.Image.Image: RGB image

        """
        if self.rgb_palette is not None:
            rgb_image = self.rgb_palette[self.rgb_index_array]
            return Image.fromarray(rgb_image.astype(np.uint8), "RGB")
        image = Image.fromarray(self.rgb_index_array)
        return image.convert("RGB")

    def _calculate_image_display_size(self) -> tuple[int, int]:
        """Calculate display size to fit half screen width.

        Returns:
            tuple[int, int]: (width, height) for display

        """
        if self.imgstim_size is None:
            maxsz = self.sres[0] / 2
            mx = 1.0
            while (mx + 1) * self.size[0] <= maxsz:
                mx += 1.0
            self.imgstim_size = (int(self.size[0] * mx), int(self.size[1] * mx))
        return self.imgstim_size

    def _get_processed_pil_image(self) -> tuple[Image.Image, tuple[int, int]]:
        """Builds, scales, and returns the PIL image along with its display size.

        This encapsulates the common PIL image processing steps used by backends.

        Returns:
            tuple[PIL.Image.Image, tuple[int, int]]: A tuple containing the processed
            PIL Image and its calculated display size (width, height).

        """
        image = self._build_rgb_image_from_palette()
        imgstim_size = self._calculate_image_display_size()

        # Use NEAREST resampling for pixel-art like scaling
        image = image.resize(imgstim_size, Image.Resampling.NEAREST)
        return image, imgstim_size

    @abstractmethod
    def exit_image_display(self) -> None:
        """Clean up camera image display."""

    @abstractmethod
    def draw_line(self, x1: float, y1: float, x2: float, y2: float, colorindex: int) -> None:
        """Draw line on camera view.

        Called by EyeLink to draw crosshairs on pupil and corneal reflection.
        Backends should draw using their native drawing API for best performance.

        Args:
            x1: X coordinate of start point
            y1: Y coordinate of start point
            x2: X coordinate of end point
            y2: Y coordinate of end point
            colorindex: Pylink color constant

        """

    @abstractmethod
    def draw_lozenge(self, x: float, y: float, width: float, height: float, colorindex: int) -> None:
        """Draw rectangle on camera view.

        Called by EyeLink to draw pupil box and search limits.
        Backends should draw using their native drawing API for best performance.

        Args:
            x: X coordinate of top-left corner
            y: Y coordinate of top-left corner
            width: Width of lozenge
            height: Height of lozenge
            colorindex: Pylink color constant

        """

    @abstractmethod
    def get_input_key(self) -> list:
        """Get keyboard input and return list of pylink.KeyInput objects.

        Should poll for keyboard events and convert them to EyeLink key codes.
        Commonly used keys:
            - Escape: pylink.ESC_KEY
            - Enter/Return: pylink.ENTER_KEY
            - Space: ord(' ')
            - Arrow keys: pylink.CURS_UP, pylink.CURS_DOWN, pylink.CURS_LEFT, pylink.CURS_RIGHT
            - Page Up/Down: pylink.PAGE_UP, pylink.PAGE_DOWN
            - 'c': calibrate
            - 'v': validate
            - 'a': auto threshold

        Returns:
            list: List of pylink.KeyInput objects, or empty list if no input

        """

    @abstractmethod
    def get_mouse_state(self) -> tuple | None:
        """Get mouse position and button state.

        Returns:
            tuple: ((x, y), button_state) or None if not implemented
                - (x, y): Mouse position in EyeLink coordinates
                - button_state: 1 if button pressed, 0 otherwise

        """
        return None

    @staticmethod
    def play_beep(beepid: int) -> None:
        """Play audio beep for calibration feedback.

        Args:
            beepid: Beep type constant from pylink:
                - pylink.CAL_TARG_BEEP / pylink.DC_TARG_BEEP: Target appears
                - pylink.CAL_GOOD_BEEP / pylink.DC_GOOD_BEEP: Calibration point accepted
                - pylink.CAL_ERR_BEEP / pylink.DC_ERR_BEEP: Calibration point failed

        """
        if beepid in {pylink.DC_TARG_BEEP, pylink.CAL_TARG_BEEP}:
            audio.play_target_beep()
        elif beepid in {pylink.CAL_ERR_BEEP, pylink.DC_ERR_BEEP}:
            audio.play_error_beep()
        else:  # CAL_GOOD_BEEP or DC_GOOD_BEEP
            audio.play_done_beep()

    @staticmethod
    def alert_printf(msg: str) -> None:
        """Display alert message.

        Args:
            msg: Alert message to display

        """
        logger.warning("EyeLink Alert: %s", msg)

    def record_abort_hide(self) -> None:
        """Handle recording abort."""
