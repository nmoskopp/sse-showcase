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
<style>code { white-space: pre-wrap; }</style>
<h1>Server-Sent Events</h1>
<ul>
<li>Web server does not close connection, keeps sending
<li>One-way only (no client-to-server messages)
<li><code>Content-Type: text/event-stream</code>
<li>JavaScript API: <code>EventSource</code>
<li>HTTP Basic Auth works
<li>Headers can not be set
</ul>
<code>
import { EventSource } from "extended-eventsource";

// this is intended to fail (no credentials)
const eventSource_0 = new EventSource("/events");

// this works thanks to extended-eventsource
const eventSource_1 = new EventSource(
    "/events",
    {
        headers: {
            Authorization: "Bearer FooBar"
        }
    }
);

eventSource_0.onmessage = eventSource_1.onmessage = (event) => {
    console.log(`message ${event.lastEventId}: ${event.data}`);
};
</code>
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
