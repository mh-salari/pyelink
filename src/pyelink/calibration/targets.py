"""Calibration target generation.

This module provides functions to generate calibration targets.
Supports scientific fixation targets (Thaler et al., 2013) and basic circle targets.

Target Types:
    - "A": Center dot only
    - "B": Outer ring only
    - "C": Cross only
    - "AB": Center dot + outer ring
    - "ABC": Center dot + outer ring + cross (recommended)
    - "CIRCLE": Basic concentric circles (pixel-based sizes)
"""

from fixation_target import fixation_target
from PIL import Image, ImageDraw


def generate_target(
    settings: object,
    target_type: str | None = None,
) -> Image.Image:
    """Generate a calibration target image.

    Args:
        settings: Settings object with screen configuration.
        target_type: Override for settings.target_type. One of:
            "A", "B", "C", "AB", "ABC", "CIRCLE", or "IMAGE"

    Returns:
        PIL.Image.Image: RGBA image of the target with transparent background.

    Raises:
        ValueError: If target_type is invalid or IMAGE path not provided.
        FileNotFoundError: If IMAGE path doesn't exist.

    """
    target_type = (target_type or settings.target_type).upper()

    if target_type == "IMAGE":
        return _load_image_target(settings)
    if target_type == "CIRCLE":
        return _generate_circle_target(settings)
    if target_type in {"A", "B", "C", "AB", "BC", "AC", "ABC"}:
        return _generate_fixation_target(settings, target_type)

    raise ValueError(
        f"Invalid TARGET_TYPE: {target_type!r}. Must be one of: 'A', 'B', 'C', 'AB', 'ABC', 'CIRCLE', 'IMAGE'"
    )


def _generate_fixation_target(settings: object, style: str) -> Image.Image:
    """Generate a scientific fixation target using fixation-target package.

    Args:
        settings: Settings object with screen and fixation parameters.
        style: Target style - "A", "B", "C", "AB", "ABC", etc.

    Returns:
        PIL.Image.Image: RGBA image with transparent background.

    """
    # Use RGBA colors directly from settings
    center_color = settings.fixation_center_color
    outer_color = settings.fixation_outer_color
    cross_color = settings.fixation_cross_color

    result = fixation_target(
        screen_width_mm=settings.screen_width,
        screen_height_mm=settings.screen_height,
        screen_width_px=settings.screen_res[0],
        screen_height_px=settings.screen_res[1],
        viewing_distance_mm=(settings.screen_distance_top_bottom[0] + settings.screen_distance_top_bottom[1]) / 2
        if settings.screen_distance_top_bottom
        else settings.screen_distance,
        target_type=style,
        center_diameter_in_degrees=settings.fixation_center_diameter,
        outer_diameter_in_degrees=settings.fixation_outer_diameter,
        cross_width_in_degrees=settings.fixation_cross_width,
        center_color=center_color,
        outer_color=outer_color,
        cross_color=cross_color,
        save_png=False,
        save_svg=False,
        show=False,
        log=False,
    )

    return result["image"]


def _generate_circle_target(settings: object) -> Image.Image:
    """Generate a basic concentric circles target (pixel-based).

    This is for simple targets with explicit pixel sizes,
    not based on visual angle calculations.

    Args:
        settings: Settings object with CIRCLE_* parameters.

    Returns:
        PIL.Image.Image: RGBA image with transparent background.

    """
    outer_r = settings.circle_outer_radius
    inner_r = settings.circle_inner_radius
    outer_color = settings.circle_outer_color
    inner_color = settings.circle_inner_color

    # Create image large enough for the target
    size = outer_r * 2 + 2
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    center = size // 2

    # Draw outer circle
    draw.ellipse(
        [center - outer_r, center - outer_r, center + outer_r, center + outer_r],
        fill=(*outer_color, 255),
    )

    # Draw inner circle
    draw.ellipse(
        [center - inner_r, center - inner_r, center + inner_r, center + inner_r],
        fill=(*inner_color, 255),
    )

    return img


def _load_image_target(settings: object) -> Image.Image:
    """Load a custom image target from file.

    Args:
        settings: Settings object with TARGET_IMAGE_PATH.

    Returns:
        PIL.Image.Image: RGBA image.

    Raises:
        ValueError: If TARGET_IMAGE_PATH is not set.
        FileNotFoundError: If the image file doesn't exist.

    """
    path = settings.target_image_path
    if not path:
        raise ValueError("TARGET_TYPE='IMAGE' but TARGET_IMAGE_PATH is not set")

    img = Image.open(path)
    return img.convert("RGBA")
