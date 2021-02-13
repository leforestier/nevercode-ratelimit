import unittest
from ratelimit.redis_sliding_window_counter import RedisSlidingWindowCounter
from ratelimit.test import window_counters
import fakeredis

r = fakeredis.FakeStrictRedis()

MyTest = window_counters.build_test_case_class(
    RedisSlidingWindowCounter,
    setUpFunc = r.flushdb,
    r = r
)

if __name__ == '__main__':
    unittest.main()
