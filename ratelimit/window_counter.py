class WindowCounter(object):
    def notify_event(self, event: str, timestamp = None):
        raise NotImplementedError

    def get_count(self, event: str, timestamp = None):
        """
            should return the number (or an approximation of the number ) of
            logged events that matched exactly the string `event` during the
            last window of time
        """
        raise NotImplementedError
