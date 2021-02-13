class RateLimit(object):
    def __init__(self, app, extract_user_id, max_req, window_counter):
        """
        app:
            your wsgi app

        extract_user_id:
            a function that takes the environ that is passed to the wsgi app,
            and returns a string that identifies the user (you could for example,
            pass a function that extracts the IP address of the user, or a function
            that extracts an API key from the query string)

        max_req:
            the max number of requests allowed by window of time
            When the window_counter indicates that it has received `max_req` requests
            from the same user during the last window of time, subsequent requests
            will receive a "403 Forbidden" response

        window_counter:
            an instance of WindowCounter, such as SimpleSlidingWindowCounter

        Example:
            to rate limit users proxied to a Flask app `app` to 1000 requests per hour,
            based on their IP address::

                app.wsgi_app = RateLimit(
                    app.wsgi_app,
                    (lambda: environ: environ['HTTP_X_FORWARDED_FOR']),
                    1000,
                    SimpleSlidingWindowCounter(3600)
                )
        """
        self.app = app
        self.extract_user_id = extract_user_id
        self.max_req = max_req
        self.window_counter = window_counter

    def __call__(self, environ, start_response):
        user_id = self.extract_user_id(environ)
        count_so_far = self.window_counter.get_count(user_id)
        remaining = max(self.max_req - count_so_far, 0)
        # that should actually never be less than zero unless we've stopped
        # and restarted the app with a different max_req
        x_rate_headers = [
            ('X-RateLimit-Limit', str(self.max_req))
        ]
        if remaining == 0:
            x_rate_headers.append(('X-RateLimit-Remaining', '0'))
            start_response(
                '403 Forbidden',
                x_rate_headers + [('Content-Type', 'text/plain')]
            )
            return [b'Too many requests!']
        else:
            self.window_counter.notify_event(user_id)
            x_rate_headers.append(('X-RateLimit-Remaining', str(remaining-1)))
            def new_start_response(status, headers):
                start_response(
                    status,
                    x_rate_headers + headers
                )
            return self.app(environ, new_start_response)
