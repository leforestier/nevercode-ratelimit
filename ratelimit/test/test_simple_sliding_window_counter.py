import unittest
from ratelimit.simple_sliding_window_counter import SimpleSlidingWindowCounter
from ratelimit.test import window_counters

MyTest = window_counters.build_test_case_class(SimpleSlidingWindowCounter)

if __name__ == '__main__':
    unittest.main()
