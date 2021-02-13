import unittest
import datetime
import time
import random; random.seed(42)

def build_test_case_class(window_counter_cls, setUpFunc=None, *args, **kwargs):
    """
    *args, **kwargs to be passed to the constructor of the class tested
    in addition to the window_size argument
    """
    class WindowCounterTest(unittest.TestCase):

        if setUpFunc:
            def setUp(self):
                setUpFunc(self)

        def test1(self):
            for i in range(1,6):
                s = window_counter_cls(3600, *args, **kwargs)
                start = time.mktime(
                    datetime.datetime(
                        year=2021,
                        month=2,
                        day=i,
                        minute = random.randint(0,59)
                    ).timetuple()
                )
                dts = sorted(random.randint(0, 7200) for __ in range(1000))
                for dt in dts:
                    s.notify_event('A', start + dt)
                self.assertTrue( 450 <= s.get_count('A', start + 7200) <= 550)

        def test2(self):
            for i in range(1,6):
                s = window_counter_cls(3600, *args, **kwargs)
                start = time.mktime(
                    datetime.datetime(
                        year=2028,
                        month=8,
                        day=i,
                        minute = random.randint(0,59)
                    ).timetuple()
                )
                events = sorted(
                    ((random.randint(0, 7200), random.choice(['A', 'B', 'C']))
                    for __ in range(3000)),
                    key = (lambda tpl: tpl[0])
                )
                for dt, ev in events:
                    s.notify_event(ev, start + dt)
                for ev in ('A', 'B', 'C'):
                    self.assertTrue(450 <= s.get_count(ev, start + 7200) <= 550)
    return WindowCounterTest
