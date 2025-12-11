"""Cross-platform audio playback using PyAudio and numpy.

This module provides reliable audio playback that works regardless of which
display backend (pygame, pyglet, psychopy) is being used. It uses PyAudio
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
import pyaudio


class AudioPlayer:
    """Audio player using PyAudio for backend-independent audio playback."""

    def __init__(self, sample_rate: int = 44100) -> None:
        """Initialize the audio player with PyAudio.

        Args:
            sample_rate: Audio sample rate in Hz (default: 44100)

        """
        self._sample_rate = sample_rate
        self._pyaudio = pyaudio.PyAudio()

        # Pre-generate beep sounds
        self._beep_target = self._make_sound(800, duration=0.1)
        self._beep_done = self._make_sound(1200, duration=0.1)
        self._beep_error = self._make_sound(400, duration=0.1)

    def _make_sound(self, frequency: float, duration: float = 0.1, volume: float = 0.5) -> bytes:
        """Generate a sine wave tone as audio bytes.

        Args:
            frequency: Frequency of the tone in Hz
            duration: Duration of the tone in seconds
            volume: Volume level (0.0 to 1.0)

        Returns:
            Audio data as bytes

        """
        n_samples = int(self._sample_rate * duration)
        t = np.linspace(0, duration, n_samples, endpoint=False)
        wave = np.sin(2 * np.pi * frequency * t) * volume
        audio = (wave * 32767).astype(np.int16)
        return audio.tobytes()

    def _play_sound(self, audio_data: bytes) -> None:
        """Play audio data using PyAudio.

        Args:
            audio_data: Audio data as bytes

        """
        stream = self._pyaudio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self._sample_rate,
            output=True,
        )
        stream.write(audio_data)
        stream.stop_stream()
        stream.close()

    def beep_target(self) -> None:
        """Play the target acquisition beep (800 Hz)."""
        self._play_sound(self._beep_target)

    def beep_done(self) -> None:
        """Play the calibration done beep (1200 Hz)."""
        self._play_sound(self._beep_done)

    def beep_error(self) -> None:
        """Play the error beep (400 Hz)."""
        self._play_sound(self._beep_error)

    def __del__(self) -> None:
        """Clean up PyAudio on deletion."""
        if hasattr(self, "_pyaudio"):
            self._pyaudio.terminate()


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
