"""Utility classes and functions for eyelink-wrapper.

This module contains shared utilities used across the package, including
the RingBuffer class for efficient sample storage.
"""

import copy
from collections import deque


class RingBuffer:
    """A simple ring buffer based on the deque class."""

    def __init__(self, maxlen: int = 200) -> None:
        """Initialize ring buffer with specified maximum length.

        Args:
            maxlen: Maximum number of elements the buffer can hold

        """
        # Create que with maxlen
        self.maxlen = maxlen
        self._b = deque(maxlen=maxlen)

    def clear(self) -> None:
        """Clear all elements from the buffer."""
        return self._b.clear()

    def get_all(self) -> list:
        """Return all samples from buffer and empty the buffer.

        Returns:
            list: All samples that were in the buffer

        """
        lenb = len(self._b)
        return [self._b.popleft() for i in range(lenb)]

    def peek(self) -> list:
        """Return all samples from buffer without emptying the buffer.

        Creates a temporary copy of the buffer to read values non-destructively.

        Returns:
            list: All samples currently in the buffer

        """
        b_temp = copy.copy(self._b)
        c = []
        if len(b_temp) > 0:
            for _i in range(len(b_temp)):
                c.append(b_temp.pop())

        return c

    def peek_time_range(self, t0: float, t1: float) -> list:
        """Return samples from buffer within time range without emptying buffer.

        Assumes samples are stored with timestamp as first element: [timestamp, ...]

        Args:
            t0: Start time of range (inclusive)
            t1: End time of range (inclusive)

        Returns:
            list: Samples with timestamps between t0 and t1

        """
        b_temp = copy.copy(self._b)
        c = []
        if len(b_temp) > 0:
            for _i in range(len(b_temp)):
                sample = b_temp.pop()
                if (sample[0] >= t0) and (sample[0] <= t1):
                    c.append(sample)

        return c

    def append(self, l: list) -> None:
        """Append buffer with the most recent sample.

        Args:
            l: Sample data to append (typically a list with timestamp and values)

        """
        self._b.append(l)
