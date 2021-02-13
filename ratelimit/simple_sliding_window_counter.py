from ratelimit.window_counter import WindowCounter
from ratelimit.window_calculations import timestamp_to_window, previous_window_portion
from threading import Lock
import time

class SimpleSlidingWindowCounter(WindowCounter):
    def __init__(self, window_size):
        """
        window_size:
            size of the window, in seconds
        """
        self.window_size = window_size
        self.current_window = 0
        self.windows  = ({}, {}) # (past, present)
        self.lock = Lock()

    def _refresh_windows(self, timestamp):
        window = timestamp_to_window(timestamp, self.window_size)
        with self.lock:
            if window > self.current_window + 1:
                self.current_window = window
                self.windows = ({}, {})
            elif window == self.current_window + 1:
                self.current_window = window
                self.windows = (self.windows[1], {})

    def notify_event(self, event: str, timestamp = None):
        timestamp = timestamp or time.time()
        self._refresh_windows(timestamp)
        with self.lock:
            try:
                self.windows[1][event] += 1
            except KeyError:
                self.windows[1][event] = 1

    def get_count(self, event: str, timestamp = None):
        """
            return an approximation of the number of logged events that matched
            exactly the string `event` during the current window of time
        """
        timestamp = timestamp or time.time()
        self._refresh_windows(timestamp)
        pwp = previous_window_portion(timestamp, self.window_size)
        with self.lock:
            return int(
                self.windows[1].get(event, 0)
                +
                pwp
                *
                self.windows[0].get(event, 0)
            )
