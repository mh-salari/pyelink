"""Target-position helpers for calibration / validation layouts."""

from __future__ import annotations


def hv9_target_positions(
    screen_res: tuple[int, int],
    area_proportion: tuple[float, float] = (0.88, 0.83),
    corner_scaling: float = 1.0,
) -> list[tuple[int, int]]:
    """Return the 9 HV9 target positions ordered ``centre, TC, BC, LC, RC, TL, TR, BL, BR``.

    Args:
        screen_res: ``(width, height)`` of the display in pixels.
        area_proportion: Fraction of screen width and height bounded by the
            outer targets. EyeLink default is ``(0.88, 0.83)``.
        corner_scaling: Distance of the four diagonal corner targets from the
            display centre, as a fraction of ``area_proportion``. EyeLink
            default is ``1.0`` (corners at the full area-proportion
            rectangle). Values < 1.0 pull the corner targets toward the
            centre — same semantics as the ``calibration_corner_scaling`` /
            ``validation_corner_scaling`` Host PC parameters. The four
            cardinal targets (TC/BC/LC/RC) and the centre are unaffected.

    Returns:
        Nine ``(x, y)`` pixel coordinates with top-left origin.

    """
    w, h = screen_res
    cx, cy = w // 2, h // 2
    ax = int(area_proportion[0] * w / 2)
    ay = int(area_proportion[1] * h / 2)
    cax = int(corner_scaling * ax)
    cay = int(corner_scaling * ay)
    return [
        (cx, cy),
        (cx, cy - ay),
        (cx, cy + ay),
        (cx - ax, cy),
        (cx + ax, cy),
        (cx - cax, cy - cay),
        (cx + cax, cy - cay),
        (cx - cax, cy + cay),
        (cx + cax, cy + cay),
    ]
