"""Pygame display backend implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pygame

from .base import BaseDisplay

if TYPE_CHECKING:
    from pathlib import Path


class PygameDisplay(BaseDisplay):
    """Pygame implementation of display window management.

    Manages pygame window creation, event handling, and drawing operations.
    Provides both direct access to pygame.Surface and backend-agnostic helpers.
    """

    @property
    def backend_name(self) -> str:
        """Get backend identifier."""
        return "pygame"

    def _create_window(self, settings: object) -> pygame.Surface:  # noqa: PLR6301
        """Create pygame window.

        Args:
            settings: Settings object with SCREEN_RES, FULLSCREEN, DISPLAY_INDEX

        Returns:
            pygame.Surface window object

        """
        pygame.init()

        flags = pygame.FULLSCREEN if settings.fullscreen else 0

        window = pygame.display.set_mode(
            settings.screen_res,
            flags,
            display=settings.display_index,
        )

        pygame.display.set_caption("PyELink - Pygame Backend")

        return window

    def flip(self) -> None:  # noqa: PLR6301
        """Update display."""
        pygame.display.flip()

    def close(self) -> None:  # noqa: PLR6301
        """Close pygame window and quit."""
        pygame.quit()

    def get_events(self) -> list[dict[str, Any]]:
        """Get pygame events as unified dicts.

        Returns:
            List of event dicts with unified keys

        """
        events = []

        for event in pygame.event.get():
            # Check for Ctrl+C (when window has focus, SIGINT won't fire)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_c and (event.mod & pygame.KMOD_CTRL):
                if self.shutdown_handler:
                    self.shutdown_handler(None, None)  # Call signal handler directly
                return events  # Return immediately after shutdown initiated

            event_dict = {"type": self._event_type_to_string(event.type)}

            if event.type in {pygame.KEYDOWN, pygame.KEYUP}:
                event_dict["key"] = pygame.key.name(event.key)
                event_dict["unicode"] = event.unicode if hasattr(event, "unicode") else ""
                event_dict["mod"] = event.mod

            elif event.type in {pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP}:
                event_dict["pos"] = event.pos
                event_dict["button"] = event.button

            elif event.type == pygame.MOUSEMOTION:
                event_dict["pos"] = event.pos
                event_dict["rel"] = event.rel
                event_dict["buttons"] = event.buttons

            events.append(event_dict)

        return events

    def _event_type_to_string(self, event_type: int) -> str:  # noqa: PLR6301
        """Convert pygame event type constant to string.

        Args:
            event_type: pygame event type constant

        Returns:
            Event type as string

        """
        event_map = {
            pygame.QUIT: "quit",
            pygame.KEYDOWN: "keydown",
            pygame.KEYUP: "keyup",
            pygame.MOUSEBUTTONDOWN: "mousebuttondown",
            pygame.MOUSEBUTTONUP: "mousebuttonup",
            pygame.MOUSEMOTION: "mousemotion",
        }
        return event_map.get(event_type, "unknown")

    def fill(self, color: tuple[int, int, int]) -> None:
        """Fill window with color.

        Args:
            color: RGB tuple (0-255, 0-255, 0-255)

        """
        self._window.fill(color)

    def clear(self) -> None:
        """Clear window to black."""
        self._window.fill((0, 0, 0))

    def get_size(self) -> tuple[int, int]:
        """Get window dimensions.

        Returns:
            (width, height) in pixels

        """
        return self._window.get_size()

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
        font = pygame.font.Font(None, size)
        text_surface = font.render(text, True, color)

        if center:
            text_rect = text_surface.get_rect(center=(self._window.get_width() // 2, self._window.get_height() // 2))
            self._window.blit(text_surface, text_rect)
        else:
            self._window.blit(text_surface, pos)

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
        image = pygame.image.load(str(image_path))

        if scale is not None:
            new_size = (int(image.get_width() * scale), int(image.get_height() * scale))
            image = pygame.transform.scale(image, new_size)

        if center:
            image_rect = image.get_rect(center=(self._window.get_width() // 2, self._window.get_height() // 2))
            self._window.blit(image, image_rect)
        else:
            self._window.blit(image, pos)
