"""EyeLink event processing.

This module provides the EventProcessor class for managing event retrieval
and processing from the EyeLink tracker.
"""

from __future__ import annotations

import logging
import time
from concurrent.futures import Future, ThreadPoolExecutor
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .core import EyeLink

import numpy as np

from .utils import RingBuffer

logger = logging.getLogger(__name__)


class EventProcessor:
    """Processes blink, fixation, and saccade events from EyeLink tracker.

    This class manages:
    - Event retrieval from tracker
    - Buffering events in ring buffers
    - Background thread for continuous event monitoring
    """

    def __init__(self, device: EyeLink, buffer_length: int = 0) -> None:
        """Initialize event processor.

        Args:
            device: Connected EyeLink instance
            buffer_length: Number of events to store in ring buffers (0 = no buffering)

        """
        self.device = device
        self.buffer_length = buffer_length

        # Initialize event buffers if needed
        if buffer_length != 0:
            self.fixdur_buf = RingBuffer(maxlen=buffer_length)
            self.blinkdur_buf = RingBuffer(maxlen=buffer_length)
            self.pupsize_buf = RingBuffer(maxlen=buffer_length)

        # Thread pool executor for background event processing
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="EventProcessor")
        self._event_future: Future | None = None
        self._event_stop = True

    def get_event(self) -> tuple[str | None, list]:
        """Get the latest blink or fixation event over the link.

        The link must have been activated first: tracker.startRecording(0, 0, 1, 1)
        If both eyes are used, the left one is chosen by default.

        Eye indices:
            0 - left eye
            1 - right eye
            2 - binocular

        Data type constants from pylink:
            4 - ENDBLINK event
            8 - ENDFIX (fixation end) event
            200 - Sample data
            0x3F/0 - No data available

        Returns:
            tuple: (event_type, event_prop)
                - event_type: 'blink', 'fixation', or None
                - event_prop: List of event properties

        """
        # Use these values if nothing else is produced
        event_type = None
        event_prop = []

        if self.device.realconnect:
            # Keep getting samples until a new sample is found
            timeout = 0.010  # Don't wait for new samples longer than 10 ms
            t0 = time.time()
            while (time.time() - t0) < timeout:
                data_type = self.device.get_next_data()
                if data_type == 4:  # ENDBLINK event
                    event_type = "blink"
                    blink_event = self.device.get_float_data()
                    if blink_event is not None:
                        event_prop.append(blink_event.getEndTime() - blink_event.getStartTime())
                elif data_type == 8:  # ENDFIX (fixation end) event
                    event_type = "fixation"
                    fix_event = self.device.get_float_data()
                    if fix_event is not None:
                        event_prop.extend([
                            fix_event.getEndTime() - fix_event.getStartTime(),
                            fix_event.getAveragePupilSize(),
                        ])
                elif data_type in {0x3F, 0}:  # No data available
                    break
                else:
                    continue
        return event_type, event_prop

    def start_event_thread(self) -> None:
        """Start event buffer thread."""
        if self.buffer_length == 0:
            logger.warning("Cannot start event thread: buffer_length is 0")
            return

        if self._event_future is not None and not self._event_future.done():
            logger.warning("Event thread already running")
            return

        # First clear buffers from old data
        self.fixdur_buf.clear()
        self.pupsize_buf.clear()
        self.blinkdur_buf.clear()

        # Start the thread
        self._event_stop = False
        self._event_future = self._executor.submit(self._event_loop)
        logger.info("Event thread started")

    def _event_loop(self) -> None:
        """Continuously read events into the ring buffer (called by event thread)."""
        k = 0
        while True:
            if self._event_stop:
                break

            event_type, event_prop = self.get_event()

            # If an actual event happened, write to buffer
            if event_type:
                # Take different action depending on what event it is
                if "blink" in event_type:
                    self.blinkdur_buf.append(event_prop[0])
                elif "fixation" in event_type:
                    self.fixdur_buf.append(event_prop[0])
                    self.pupsize_buf.append(event_prop[1])

            if np.mod(k, 10) == 0:
                time.sleep(0.001)
            k += 1

    def stop_event_thread(self) -> None:
        """Stop event thread and wait for it to finish."""
        if self._event_future is None:
            return

        self._event_stop = True

        # Wait for thread to finish gracefully (up to 5 seconds)
        try:
            self._event_future.result(timeout=5.0)
        except TimeoutError:
            logger.warning("Event thread did not stop within timeout")
        except Exception:
            logger.exception("Exception in event thread")

    def shutdown(self) -> None:
        """Shutdown the thread pool executor gracefully."""
        self.stop_event_thread()
        self._executor.shutdown(wait=True, cancel_futures=True)
        logger.info("EventProcessor executor shutdown complete")

    def flush_events(self) -> None:
        """Clear the event buffers."""
        if self.buffer_length != 0:
            self.fixdur_buf.clear()
            self.pupsize_buf.clear()
            self.blinkdur_buf.clear()
