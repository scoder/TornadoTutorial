"""
Backend web-service implementation.

See data.py for the data part.
"""

import asyncio
import json
import logging
import os.path
import time

import tornado.ioloop
import tornado.web

from tornado.options import options, define
from tornado.web import RequestHandler

from .data import download, download_interleaved

_logger = logging.getLogger(__name__)


define("port", default=8880, type=int,
       help="The TCP port that this application should listen on")


class WebApplication(tornado.web.Application):
    _data = None
    _downloading = None

    async def read_data(self, interleaved=False):
        if not self._data:
            start_time = None
            # join parallel download requests into one
            if self._downloading is None:
                start_time = time.time()
                # Need a Task here since coroutines are not awaitable more than once.
                self._downloading = asyncio.create_task(
                    download_interleaved() if interleaved else download())
            self._data = await self._downloading
            if start_time is not None:
                _logger.info("Downloaded data files in %.2f seconds", time.time() - start_time)
            self._downloading = None

        return self._data


class FortuneListHandler(RequestHandler):
    async def get(self):
        data = await self.application.read_data(interleaved=True)
        await self.render("list.html", fortune_lists=data, build_link=self._build_link)

    def _build_link(self, key, file_format='html'):
        return "/fortunes/{}/{}/{}{format}".format(
            *key, format='.' + file_format.lstrip('.') if file_format else '')


class FortuneHandler(RequestHandler):
    async def get(self, owner, repo, path, format):
        data = await self.application.read_data(interleaved=True)
        result = data.get((owner, repo, path))
        if not result:
            self.send_error(404)
            return

        # Make the request take a bit longer.
        await asyncio.sleep(1)

        if format == 'json':
            self.set_header('Content-Type', 'application/json')
            await self.finish(json.dumps(result))
        else:
            await self.render("fortune.html", data=result)


def main(port=None):
    routes = [
        (r"/fortunes/(?P<owner>[^/]+)/(?P<repo>[^/]+)/(?P<path>[^.]+)(?:\.(?P<format>json|html))?",
         FortuneHandler),
        (r"/",
         FortuneListHandler),
    ]
    application = WebApplication(
        routes,
        template_path=os.path.join(os.path.dirname(__file__), 'templates'),
        #debug=True,
    )

    if port is None:
        port = options.port
    _logger.info("Listening on port %d", port)
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    import sys
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    main()
