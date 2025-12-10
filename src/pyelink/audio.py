"""Cross-platform audio playback using sounddevice and numpy.

This module provides reliable audio playback that works regardless of which
display backend (pygame, pyglet, psychopy) is being used. It uses sounddevice
and numpy for lightweight, backend-independent audio.

Usage:
    from pyelink.audio import AudioPlayer

    # Create player
    player = AudioPlayer()

    # Play beeps
    player.beep_target()   # 800 Hz
    player.beep_done()     # 1200 Hz
    player.beep_error()    # 400 Hz
"""

import numpy as np
import sounddevice as sd


class AudioPlayer:
    """Audio player using sounddevice and numpy for cross-platform beeps."""

    def __init__(self, frequency: int = 22050) -> None:
        """Initialize the audio player.

        Args:
            frequency: Sample rate in Hz (default 22050)

        """
        self._sample_rate = frequency
        # Pre-generate calibration beeps
        self._beep_target = self.generate_tone(800, duration=0.1)
        self._beep_done = self.generate_tone(1200, duration=0.1)
        self._beep_error = self.generate_tone(400, duration=0.1)

    def generate_tone(self, frequency: float, duration: float = 0.1, volume: float = 1.0) -> np.ndarray:
        """Generate a sine wave tone.

        Args:
            frequency: Tone frequency in Hz
            duration: Duration in seconds
            volume: Volume from 0.0 to 1.0

        Returns:
            np.ndarray: The generated waveform.

        """
        n_samples = int(self._sample_rate * duration)
        t = np.linspace(0, duration, n_samples, dtype=np.float32)
        wave = np.sin(2 * np.pi * frequency * t) * volume
        return wave.astype(np.float32)

    def beep_target(self) -> None:
        """Play the target acquisition beep (800 Hz)."""
        sd.play(self._beep_target, self._sample_rate)

    def beep_done(self) -> None:
        """Play the calibration done beep (1200 Hz)."""
        sd.play(self._beep_done, self._sample_rate)

    def beep_error(self) -> None:
        """Play the error beep (400 Hz)."""
        sd.play(self._beep_error, self._sample_rate)


def get_player() -> AudioPlayer:
    """Get a shared AudioPlayer instance."""
    if not hasattr(get_player, "player"):
        get_player.player = AudioPlayer()
    return get_player.player


def play_target_beep() -> None:
    """Play the target acquisition beep (800 Hz)."""
    get_player().beep_target()


def play_done_beep() -> None:
    """Play the calibration done beep (1200 Hz)."""
    get_player().beep_done()


def play_error_beep() -> None:
    """Play the error beep (400 Hz)."""
    get_player().beep_error()
