import unittest
from ratelimit.middleware import RateLimit
import time
from ratelimit.simple_sliding_window_counter import SimpleSlidingWindowCounter

class MiddlewareTest(unittest.TestCase):
    def test_middleware(self):
        dct = {'status': None, 'headers': None}

        def recorded_start_response(status, headers):
            dct['status'] = status
            dct['headers'] = headers

        def app(environ, start_response):
            start_response('200 OK', [('Content-Type', 'text/plain')])
            return  [b'Very valuable information\n']

        def extract_user_id(environ):
            return environ['HTTP_X_FORWARDED_FOR']

        limited_app = RateLimit(
            app,
            extract_user_id,
            5,
            SimpleSlidingWindowCounter(2)
        ) # max 5 request / 2 sec

        limited_app(
            {'HTTP_X_FORWARDED_FOR': '10.0.0.8'},
            recorded_start_response
        )

        self.assertEqual(dct['status'], '200 OK')
        self.assertEqual(
            sorted(dct['headers']),
            sorted([
                ('X-RateLimit-Limit', '5'),
                ('X-RateLimit-Remaining', '4'),
                ('Content-Type', 'text/plain')
            ])
        )

        for i in range(6):
            time.sleep(0.1)
            limited_app(
                {'HTTP_X_FORWARDED_FOR': '10.0.0.8'},
                recorded_start_response
            )
            print(dct['status'])
            print(dct['headers'])
        self.assertEqual(dct['status'], '403 Forbidden')
        self.assertEqual(
            sorted(dct['headers']),
            sorted([
                ('X-RateLimit-Limit', '5'),
                ('X-RateLimit-Remaining', '0'),
                ('Content-Type', 'text/plain')
            ])
        )
        # a new player has entered the game
        limited_app(
            {'HTTP_X_FORWARDED_FOR': '10.0.10.10'},
            recorded_start_response
        )
        self.assertEqual(dct['status'], '200 OK')
        self.assertEqual(
            sorted(dct['headers']),
            sorted([
                ('X-RateLimit-Limit', '5'),
                ('X-RateLimit-Remaining', '4'),
                ('Content-Type', 'text/plain')
            ])
        )

        time.sleep(2)

        limited_app(
            {'HTTP_X_FORWARDED_FOR': '10.0.0.8'},
            recorded_start_response
        )

        self.assertEqual(dct['status'], '200 OK')

        self.assertTrue(
            int(dict(dct['headers'])['X-RateLimit-Remaining']) > 0
        )


if __name__ == '__main__':
    unittest.main()
