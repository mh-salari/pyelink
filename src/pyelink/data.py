"""EyeLink data retrieval and buffering.

This module provides the DataBuffer class for managing sample and raw data
retrieval and buffering from the EyeLink tracker.
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


class DataBuffer:
    """Handles data retrieval and buffering from EyeLink tracker.

    This class manages:
    - Sample and raw data retrieval from tracker
    - Buffering data in a ring buffer
    - Background threads for continuous data collection
    """

    def __init__(
        self,
        device: EyeLink,
        buffer_length: int = 0,
        use_buffer: bool = False,
        read_from_tracker_buffer: bool = True,
        record_raw_data: bool = False,
    ) -> None:
        """Initialize sample buffer.

        Args:
            device: Connected EyeLink instance
            buffer_length: Number of samples to store in ring buffer (0 = no buffering)
            use_buffer: Store data from tracker buffer in RingBuffer
            read_from_tracker_buffer: Use getNextData() instead of getNewestSample()
                                     (the former draws from an internal buffer and should miss fewer samples)
            record_raw_data: Whether raw pupil/CR data is being recorded

        """
        self.device = device
        self.buffer_length = buffer_length
        self.use_buffer = use_buffer
        self.read_from_tracker_buffer = read_from_tracker_buffer
        self.record_raw_data = record_raw_data

        # Eye indices
        self.left_eye = 0
        self.right_eye = 1
        self.binocular = 2

        # Timestamp tracking
        self.t_old = 0

        # Initialize ring buffer if needed
        if buffer_length != 0:
            self.buf = RingBuffer(maxlen=buffer_length)

        # Thread pool executor for background data collection
        self._executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="DataBuffer")
        self._sample_future: Future | None = None
        self._raw_future: Future | None = None
        self._sample_stop = True
        self._raw_stop = True

    def get_timestamp(self) -> float:
        """Get timestamp of latest sample.

        Returns:
            Timestamp in milliseconds, or np.nan if not connected

        """
        timestamp = np.nan
        if self.device.realconnect:
            sample = self.device.get_newest_sample()
            if sample is not None:
                # Use getRawSampleTime() if recording raw data, otherwise use getTime()
                timestamp = sample.getRawSampleTime() if self.record_raw_data else sample.getTime()

        return timestamp

    def get_sample(self, write_to_edf: bool = False) -> tuple[int | float, list | None]:
        """Get the latest gaze sample over the link.

        The link must have been activated first: tracker.startRecording(0, 0, 1, 1)
        If both eyes are used, the left one is chosen by default.

        Eye indices:
            0 - left eye
            1 - right eye
            2 - binocular (returns [lx, ly, lpupil, rx, ry, rpupil])

        Args:
            write_to_edf: Write gaze data to edf-file as messages

        Returns:
            tuple: (timestamp, sample_info)
                - timestamp: Sample timestamp or -1 if no sample
                - sample_info: List of sample data or None

        """
        # Use these values if nothing else is produced
        t = -1
        sample_info = None

        # Check which eye is being recorded
        eye_used = self.device.eye_available()

        if self.device.realconnect:
            # Keep getting samples until a new sample is found
            timeout = 0.010  # Don't wait for new samples longer than 10 ms
            t0 = time.time()
            while (time.time() - t0) < timeout:
                sample = self.device.get_newest_sample()
                if sample is not None:
                    t = sample.getTime()
                    if t != self.t_old:
                        sample_info = self._unpack_sample(t, sample, eye_used, write_to_edf)
                        break

                self.t_old = t

        return t, sample_info

    def get_sample_from_buffer(self, write_to_edf: bool = False) -> tuple[int | float, list | None]:
        """Get the latest gaze sample from the EyeLink buffer.

        Uses getNextData() which draws from an internal buffer and should miss fewer samples
        than getNewestSample().

        Data type constants from pylink:
            200 - Sample data
            4 - ENDBLINK event
            8 - ENDFIX event
            0x3F/0 - No data available

        Args:
            write_to_edf: Write gaze data to edf-file as messages

        Returns:
            tuple: (timestamp, sample_info)

        """
        # Use these values if nothing else is produced
        t = -1
        sample_info = None

        # Check which eye is being recorded
        eye_used = self.device.eye_available()

        if self.device.realconnect:
            # Keep getting samples until a new sample is found
            timeout = 0.010
            t0 = time.time()
            while (time.time() - t0) < timeout:
                data_type = self.device.get_next_data()
                if data_type == 200:  # Sample data
                    sample = self.device.get_float_data()
                    if sample is not None:
                        t = sample.getTime()
                        sample_info = self._unpack_sample(t, sample, eye_used, write_to_edf)
                        break
                elif data_type in {0x3F, 0}:  # No data available
                    break
                else:
                    continue

        return t, sample_info

    def _unpack_sample(self, t: float, sample: object, eye_used: int, write_to_edf: bool) -> list:
        """Convert sample into list format.

        Args:
            t: Sample timestamp
            sample: Sample object from tracker
            eye_used: Eye index (0=left, 1=right, 2=binocular)
            write_to_edf: Whether to write sample as message to EDF

        Returns:
            list: Sample data [x, y, pupil] or [lx, ly, lpupil, rx, ry, rpupil]

        """
        # Extract gaze positions and write as msg
        if eye_used == self.right_eye and sample.isRightSample():
            gaze_position = sample.getRightEye().getGaze()
            pupil_size = sample.getRightEye().getPupilSize()
            sample_info = [*gaze_position, pupil_size]
            sample_str = " ".join([str(t), str(gaze_position[0]), str(gaze_position[1]), str(pupil_size)])
        elif eye_used == self.left_eye and sample.isLeftSample():
            gaze_position = sample.getLeftEye().getGaze()
            pupil_size = sample.getLeftEye().getPupilSize()
            sample_info = [*gaze_position, pupil_size]
            sample_str = " ".join([str(t), str(gaze_position[0]), str(gaze_position[1]), str(pupil_size)])

        elif eye_used == self.binocular and sample.isBinocular():
            r = sample.getRightEye().getGaze()
            pr = sample.getRightEye().getPupilSize()
            l = sample.getLeftEye().getGaze()
            pl = sample.getLeftEye().getPupilSize()
            sample_info = [l[0], l[1], pl, r[0], r[1], pr]
            sample_str = " ".join([
                str(t),
                str(sample_info[0]),
                str(sample_info[1]),
                str(sample_info[2]),
                str(sample_info[3]),
                str(sample_info[4]),
                str(sample_info[5]),
            ])

        # Write to edf?
        if write_to_edf:
            self.device.send_message(sample_str)

        # Add data to buffer if activated
        if self.buffer_length != 0:
            self.buf.append([t, *sample_info])

        return sample_info

    def get_raw_sample(self, write_to_edf: bool = False) -> tuple[int | float, list | None]:
        """Get the latest raw sample over the link.

        The link must have been activated first: tracker.startRecording(0, 0, 1, 1)

        Args:
            write_to_edf: Write data to edf-file as messages

        Returns:
            tuple: (timestamp, raw_data)

        """
        # Use these values if nothing else is produced
        t = -1
        raw = None

        # Check which eye is being recorded
        eye_used = self.device.eye_available()

        if self.device.realconnect:
            # Keep getting samples until a new sample is found
            timeout = 0.010
            t0 = time.time()
            while (time.time() - t0) < timeout:
                rawsample = self.device.get_newest_sample()
                if rawsample is not None:
                    t = rawsample.getRawSampleTime()

                    # if the timestamps between old and new samples differ, it's new
                    if t != self.t_old:
                        raw = self._unpack_raw_sample(t, rawsample, eye_used, write_to_edf)
                        break

                self.t_old = t

        return t, raw

    def get_raw_sample_from_buffer(self, write_to_edf: bool = False) -> tuple[int | float, list | None]:
        """Get the latest raw sample from the EyeLink buffer.

        Data type constants from pylink:
            200 - Sample data
            0x3F/0 - No data available

        Args:
            write_to_edf: Write data to edf-file as messages

        Returns:
            tuple: (timestamp, raw_data)

        """
        # Use these values if nothing else is produced
        t = -1
        raw = None

        # Check which eye is being recorded
        eye_used = self.device.eye_available()

        if self.device.realconnect:
            # Keep getting samples until a new sample is found
            timeout = 0.010
            t0 = time.time()
            while (time.time() - t0) < timeout:
                data_type = self.device.get_next_data()
                if data_type == 200:  # Sample data
                    rawsample = self.device.get_float_data()

                    # if the timestamps between old and new samples differ, it's new
                    if rawsample is not None:
                        t = rawsample.getRawSampleTime()
                        if t != self.t_old:
                            raw = self._unpack_raw_sample(t, rawsample, eye_used, write_to_edf)
                            self.t_old = t
                            break

                elif data_type in {0x3F, 0}:  # No data available
                    break
                else:
                    continue

        return t, raw

    def _unpack_raw_sample(self, t: float, rawsample: object, eye_used: int, write_to_edf: bool) -> list:
        """Convert raw sample into message string.

        Args:
            t: Timestamp
            rawsample: Raw sample object
            eye_used: Eye index
            write_to_edf: Write to EDF file

        Returns:
            list: Raw sample data

        """
        # Extract gaze positions and write as msg
        if eye_used == self.right_eye:
            raw = [
                t,
                rawsample.getRightrRawPupil()[0],
                rawsample.getRightrRawPupil()[1],
                rawsample.getRightPupilArea(),
                rawsample.getRightPupilDimension()[0],
                rawsample.getRightPupilDimension()[1],
                rawsample.getRightRawCr()[0],
                rawsample.getRightRawCr()[1],
                rawsample.getRightCrArea(),
                rawsample.getRightRawCr2()[0],
                rawsample.getRightRawCr2()[1],
                rawsample.getRightCrArea2(),
            ]

            msg = " ".join(["R", " ".join([str(r) for r in raw])])
            if write_to_edf:
                self.device.send_message(msg)

        elif eye_used == self.left_eye:
            raw = [
                t,
                rawsample.getLeftrRawPupil()[0],
                rawsample.getLeftrRawPupil()[1],
                rawsample.getLeftPupilArea(),
                rawsample.getLeftPupilDimension()[0],
                rawsample.getLeftPupilDimension()[1],
                rawsample.getLeftRawCr()[0],
                rawsample.getLeftRawCr()[1],
                rawsample.getLeftCrArea(),
                rawsample.getLeftRawCr2()[0],
                rawsample.getLeftRawCr2()[1],
                rawsample.getLeftCrArea2(),
            ]

            msg = " ".join(["L", " ".join([str(l) for l in raw])])
            if write_to_edf:
                self.device.send_message(msg)

        elif eye_used == self.binocular:
            raw_l = [
                t,
                rawsample.getLeftrRawPupil()[0],
                rawsample.getLeftrRawPupil()[1],
                rawsample.getLeftPupilArea(),
                rawsample.getLeftPupilDimension()[0],
                rawsample.getLeftPupilDimension()[1],
                rawsample.getLeftRawCr()[0],
                rawsample.getLeftRawCr()[1],
                rawsample.getLeftCrArea(),
                rawsample.getLeftRawCr2()[0],
                rawsample.getLeftRawCr2()[1],
                rawsample.getLeftCrArea2(),
            ]

            raw_r = [
                rawsample.getRightrRawPupil()[0],
                rawsample.getRightrRawPupil()[1],
                rawsample.getRightPupilArea(),
                rawsample.getRightPupilDimension()[0],
                rawsample.getRightPupilDimension()[1],
                rawsample.getRightRawCr()[0],
                rawsample.getRightRawCr()[1],
                rawsample.getRightCrArea(),
                rawsample.getRightRawCr2()[0],
                rawsample.getRightRawCr2()[1],
                rawsample.getRightCrArea2(),
            ]
            raw = raw_l + raw_r
            msg = " ".join([
                "L",
                " ".join([str(lraw) for lraw in raw_l]),
                "R",
                " ".join([str(rraw) for rraw in raw_r]),
            ])
            if write_to_edf:
                self.device.send_message(msg)

            # Add data to buffer if activated
            if self.buffer_length != 0:
                self.buf.append(raw)

        else:
            logger.error("Something went wrong...")

        return raw

    def start_sample_thread(self) -> None:
        """Start the sample thread for continuous sampling."""
        if self._sample_future is not None and not self._sample_future.done():
            logger.warning("Sample thread already running")
            return

        self._sample_stop = False
        self._sample_future = self._executor.submit(self._sample_loop)
        logger.info("Sample thread started")

    def _sample_loop(self) -> None:
        """Continuously read raw data into the ring buffer (called by sample thread)."""
        k = 0
        while True:
            if self._sample_stop:
                break
            if self.read_from_tracker_buffer:
                self.get_sample_from_buffer(write_to_edf=False)
            else:
                self.get_sample(write_to_edf=False)

            if np.mod(k, 10) == 0:
                time.sleep(0.001)
            k += 1

    def stop_sample_thread(self) -> None:
        """Stop sample thread and wait for it to finish."""
        if self._sample_future is None:
            return

        self._sample_stop = True

        # Wait for thread to finish gracefully (up to 5 seconds)
        try:
            self._sample_future.result(timeout=5.0)
        except TimeoutError:
            logger.warning("Sample thread did not stop within timeout")
        except Exception:
            logger.exception("Exception in sample thread")

    def start_raw_thread(self) -> None:
        """Start the raw thread for continuous raw data collection."""
        if self._raw_future is not None and not self._raw_future.done():
            logger.warning("Raw thread already running")
            return

        self._raw_stop = False
        self._raw_future = self._executor.submit(self._raw_loop)
        logger.info("Raw thread started")

    def _raw_loop(self) -> None:
        """Continuously read raw data into the ring buffer (called by raw thread)."""
        k = 0
        while True:
            if self._raw_stop:
                break
            if self.read_from_tracker_buffer:
                self.get_raw_sample_from_buffer(write_to_edf=True)
            else:
                self.get_raw_sample(write_to_edf=True)

            if np.mod(k, 10) == 0:
                time.sleep(0.001)
            k += 1

    def stop_raw_thread(self) -> None:
        """Stop raw thread and wait for it to finish."""
        if self._raw_future is None:
            return

        self._raw_stop = True

        # Wait for thread to finish gracefully (up to 5 seconds)
        try:
            self._raw_future.result(timeout=5.0)
        except TimeoutError:
            logger.warning("Raw thread did not stop within timeout")
        except Exception:
            logger.exception("Exception in raw thread")

    def shutdown(self) -> None:
        """Shutdown the thread pool executor gracefully."""
        self.stop_sample_thread()
        self.stop_raw_thread()
        self._executor.shutdown(wait=True, cancel_futures=True)
        logger.info("DataBuffer executor shutdown complete")

    def flush_samples(self) -> None:
        """Clear the sample buffer."""
        if hasattr(self, "buf"):
            self.buf.clear()
