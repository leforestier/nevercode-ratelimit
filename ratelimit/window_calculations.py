def timestamp_to_window(timestamp, window_size):
    return int(timestamp) // window_size

def previous_window_portion(timestamp, window_size):
    return (1 - (timestamp % window_size) / window_size)
