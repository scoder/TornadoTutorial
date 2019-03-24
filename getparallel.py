"""
Send parallel requests to the (running) frontend server.
"""

import asyncio

from tornado.gen import multi
from tornado.httpclient import AsyncHTTPClient

URL = "http://localhost:8882/fortunes"


async def send_requests(url, request_count):
    client = AsyncHTTPClient()
    requests = [
        client.fetch(url)
        for _ in range(request_count)
    ]
    await multi(requests)


def run_requests(url, request_count):
    asyncio.run(send_requests(url, request_count))


def main():
    import sys
    request_count = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    run_requests(URL, request_count)


if __name__ == '__main__':
    main()
