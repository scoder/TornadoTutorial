import os.path
import logging

import tornado.gen
import tornado.web
import tornado.ioloop

from tornado.options import options, define
from tornado.web import RequestHandler

_logger = logging.getLogger(__name__)

WEB_PORT = 8888
# BACKEND_HOST = "http://localhost:8880/"

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')


class WebApplication(tornado.web.Application):
    pass


def main():
    routes = [
    ]
    application = WebApplication(
        routes,
        template_path=TEMPLATES_DIR,
        debug=True,
    )

    port = WEB_PORT
    _logger.info("Listening on port %d", port)
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    import sys
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    main()
