from ratelimit.window_counter import WindowCounter
from ratelimit.window_calculations import timestamp_to_window, previous_window_portion
import time

class RedisSlidingWindowCounter(WindowCounter):
    def __init__(self, window_size, r = None):
        """
        window_size: in seconds
        r: redis connection pool (redis.Redis instance)
        """
        self.window_size = window_size
        if r:
            self.r = r
        else:
            import redis
            self.r = redis.Redis()

    def notify_event(self, event: str, timestamp = None):
        timestamp = timestamp or time.time()
        current_window = timestamp_to_window(timestamp, self.window_size)
        key = "%s:%s" % (current_window, event)
        self.r.incr(key)
        self.r.expire(key, 2*self.window_size)

    def get_count(self, event, timestamp = None):
        timestamp = timestamp or time.time()
        current_window = timestamp_to_window(timestamp, self.window_size)
        previous_window = current_window - 1
        current_key = "%s:%s" % (current_window, event)
        previous_key = "%s:%s" % (previous_window, event)
        current_window_count = int(self.r.get(current_key) or 0)
        previous_window_count = int(self.r.get(previous_key) or 0)
        pwp = previous_window_portion(timestamp, self.window_size)
        return current_window_count + pwp*previous_window_count
