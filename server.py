#!/usr/bin/env python3

from datetime import datetime
from bottle import (
    get, response, request, run, static_file,
    GeventServer, HTTPError
)
from functools import wraps
from gevent import monkey, sleep
from sh import flake8, npx

flake8(__file__)

# extended-eventsource must be bundled to work in a browser
npx(
    "esbuild",
    "source.js",
    "--bundle",
    "--main-fields=module",
    _out="bundle.js"
)


monkey.patch_all()


index_html = """
<!DOCTYPE html>
<meta charset=utf-8>
<title>Extended Event Source Demo</title>
<script src="bundle.js"></script>
<strong>“Ma'am, this is a JavaScript demo!”</strong>
"""


@get('/')
def emit_index():
    return index_html


@get('/bundle.js')
def emit_bundle_js():
    return static_file("bundle.js", root=".")


def check_credentials(authorization):
    print(f"Authorization: {authorization}")
    # Can you spot the timing vulnerability?
    if 'Bearer FooBar' == authorization:
        return True
    return False


def auth_token(check_function):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            authorization = request.headers.get('Authorization')
            if not check_function(authorization):
                error = HTTPError(401, 'Access denied')
                # error.add_header('[…]')
                return error
            return function(*args, **kwargs)
        return wrapper
    return decorator


@get('/events')
@auth_token(check_credentials)
def emit_sse():
    response.content_type = 'text/event-stream'
    i = 0
    while i < 10:
        now = datetime.now().isoformat()
        yield f"id:{i}\ndata: {now}\n\n"
        sleep(1)
        i = i + 1


if __name__ == '__main__':
    run(
        reloader=True,
        server=GeventServer,
    )
