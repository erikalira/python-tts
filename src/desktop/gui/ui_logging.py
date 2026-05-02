"""Logging helpers for Desktop App GUI surfaces."""

from __future__ import annotations

import logging
import queue


class UILogHandler(logging.Handler):
    """Logging handler that forwards formatted records to a queue."""

    def __init__(self, target_queue: queue.Queue[str]):
        super().__init__()
        self._target_queue = target_queue
        self.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", "%H:%M:%S"))

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self._target_queue.put_nowait(self.format(record))
        except Exception:
            self.handleError(record)
