import json
import logging
import os.path

import tornado.gen
import tornado.ioloop
import tornado.web

from tornado.httpclient import AsyncHTTPClient
from tornado.options import options, define
from tornado.web import RequestHandler, RedirectHandler

_logger = logging.getLogger(__name__)


define("server_port", type=int, default=8882,
       help="The port that the web server listens on")

# BACKEND_HOST = "http://localhost:8880/"

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')


class FortuneRequestHandler(RequestHandler):
    URLS = [
        "http://localhost:8880/fortunes/arrjay/fortunes/lyrics.json",
        "http://localhost:8880/fortunes/arrjay/fortunes/breaksys.json",
        "http://localhost:8880/fortunes/arrjay/fortunes/puppet.json",
    ]

    # --- Entry point for HTTP GET requests: ---

    async def get(self):
        fortunes = await self.fetch_sequential(self.URLS)
        #fortunes = await self.fetch_and_wait(self.URLS)
        #fortunes = await self.fetch_as_they_come_asyncio(self.URLS)
        #fortunes = await self.fetch_as_they_come_tornado(self.URLS)
        #fortunes = await self.fetch_non_redundant(self.URLS)

        await self.render(
            "fortune.html",
            fortunes=fortunes,
        )

    # --- Helpers: ---

    _http_client = AsyncHTTPClient()

    def prepare_request(self, url):
        future = self._http_client.fetch(url)
        return future

    def prepare_request_list(self, urls):
        futures = [
            self.prepare_request(url)
            for url in urls
        ]
        return futures

    def parse_json_response(self, response):
        return json.loads(response.body.decode('utf8'))

    # --- Different ways to parallelise backend requests: ---

    async def fetch_sequential(self, urls):
        _logger.info("reading fortunes from backend")

        fortunes = []
        for url in urls:
            response = await self.prepare_request(url)
            data = self.parse_json_response(response)
            fortunes.extend(data)

        return fortunes

    async def fetch_and_wait(self, urls):
        futures = self.prepare_request_list(urls)

        _logger.info("reading fortunes from backend")

        from tornado.gen import multi
        responses = await multi(futures)

        fortunes = []
        for response in responses:
            data = self.parse_json_response(response)
            fortunes.extend(data)

        return fortunes

    async def fetch_as_they_come_asyncio(self, urls):
        futures = self.prepare_request_list(urls)

        _logger.info("reading fortunes from backend")

        from asyncio import as_completed

        fortunes = []
        for future in as_completed(futures):
            data = self.parse_json_response(await future)
            fortunes.extend(data)

        return fortunes

    async def fetch_as_they_come_tornado(self, urls):
        futures = self.prepare_request_list(urls)

        _logger.info("reading fortunes from backend")

        from tornado.gen import WaitIterator

        fortunes = []
        async for response in WaitIterator(*futures):
            data = self.parse_json_response(response)
            fortunes.extend(data)

        return fortunes

    # --- How to deduplicate backend requests: ---

    _running_requests = {}

    async def fetch_non_redundant(self, urls):
        futures = []
        reused = 0
        for url in urls:
            try:
                # Reuse existing Futures from currently running requests.
                future = self._running_requests[url]
                reused += 1
            except KeyError:
                future = self._running_requests[url] = self.prepare_request(url)
            futures.append(future)

        _logger.info("reading fortunes from %d backends, reusing %d", len(futures), reused)

        from tornado.gen import multi
        responses = await multi(futures)

        # All requests done, discard them.
        self._running_requests.clear()

        fortunes = []
        for response in responses:
            data = self.parse_json_response(response)
            fortunes.extend(data)

        return fortunes


# --- Web application boilerplate: ---

def main():
    options.parse_command_line()

    routes = [
        ("/", RedirectHandler, {'url': '/fortunes'}),
        ("/fortunes", FortuneRequestHandler),
    ]
    application = tornado.web.Application(
        routes,
        template_path=TEMPLATES_DIR,
        debug=True,
    )

    port = options.server_port
    _logger.info("Listening on port %d", port)
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    import sys
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    main()
