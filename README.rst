How to run the demo?
====================

Clone the repo, cd into the created directory, and then build the Docker image by running::

    $ docker build -t demo .

Run the demo with::

    $ docker run --rm -p 5000:5000 demo <max_req> <window_secs>

where <max_req> is the maximum number of requests you want to allow for a window lasting <window_secs> seconds.
For example, to apply a rate limit of 1000 requests per hour, do::

    $ docker run --rm -p 5000:5000 demo 1000 3600


The application is running at the address http://127.0.0.1:5000 on your computer.

You can use your favorite http client to inspect the values of the ``X-RateLimit-Limit`` and ``X-RateLimit-Remaining`` headers for each request.

You can add an "apikey" parameter to the query string. In the demo, these keys are used to distinguish between users::

    $ curl -I http://127.0.0.1:5000?apikey=782


How can I use the middleware to rate limit my Flask application?
================================================================

Here we're rate limiting a basic "Hello world" Flask application to 200 requests per hour,
identifying the users by their IP adresses:

.. code-block:: python

    from flask import Flask
    from ratelimit import RateLimit, SimpleSlidingWindowCounter

    app = Flask(__name__)

    @app.route('/')
    def hello_world():
        return 'Hello, World!'

    app.wsgi = RateLimit(
        app.wsgi,
        (lambda environ: environ['REMOTE_ADDR']),
        200,
        SimpleSlidingWindowCounter(3600)
    )

The first parameter to the ``RateLimit`` constructor is the wsgi app you want to rate limit.

The second argument is a function. Indeed, you need a function to determine from what user comes each request.
This function is passed the same ``environ`` parameter that is passed to your WSGI application.
Do what you want with it to determine who is the author of the request.
Note that you can always call ``Flask.Request(environ)`` to work with a familiar *Flask* ``Request`` object.
For example:

.. code-block:: python

    app.wsgi = RateLimit(
        app.wsgi,
        (lambda environ: Request(environ).args.get('secret_key')),,
        max_req=200,
        window_counter=SimpleSlidingWindowCounter(3600)
    )

The third argument ``max_req`` is the maximum number of requests allowed by window of time.
When the ``window_counter`` (fourth argument) indicates that it has received ``max_req`` requests
from the same user during the last window of time, subsequent requests
will receive a "403 Forbidden" response.

The fourth argument should be a subclass of WindowCounter.
You have two choices here:

    - For a small application that runs a single process, you can use ``SimpleSlidingWindowCounter``
      (it's written in Python and has no dependencies).

    - However if your app is spread over multiple processes, for example if you have multiple instances of your app
      running behind a load balancer, install Redis and use the ``RedisSlidingWindowCounter``.
      You will need to pip install `redis-py <https://pypi.org/project/redis/>`_ to use that class,
      and `fakeredis <https://pypi.org/project/fakeredis/>`_ to test it.

.. code-block:: python

    from ratelimit import RateLimit, RedisSlidingWindowCounter
    from redis import StrictRedis

    ...

    app.wsgi = RateLimit(
        app.wsgi,
        (lambda environ: environ['REMOTE_ADDR']),
        200,
        RedisSlidingWindowCounter(
            3600,
            StrictRedis(
                host='redishost',
                port=6379
            )
        )
    )
