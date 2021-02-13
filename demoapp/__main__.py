"""
Demo app

Usage:
  demoapp <max_req> <window_secs>
"""
from ratelimit import RateLimit, SimpleSlidingWindowCounter
from flask import Flask, Request
import random

if __name__ == '__main__':
    import docopt
    args = docopt.docopt(__doc__)

    app = Flask(__name__)

    prizes = [
        "bananas",
        "apples",
        "strawberries",
        "grapes",
        "oranges",
        "watermelon",
        "lemons",
        "avocados",
        "peaches",
        "blueberries"
    ]

    @app.route('/')
    def play():
        return "You won some {}!".format(random.choice(prizes))

    def extract_user_id(environ):
        req = Request(environ)
        return req.args.get('apikey', 'anonymous')


    app.wsgi_app = RateLimit(
        app.wsgi_app,
        extract_user_id,
        int(args['<max_req>']),
        SimpleSlidingWindowCounter(int(args['<window_secs>']))
    )

    app.run(host="0.0.0.0", port=5000)
