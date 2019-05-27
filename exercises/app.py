import json
import logging
import os.path

import tornado.gen
import tornado.ioloop
import tornado.web

from tornado.httpclient import AsyncHTTPClient
from tornado.options import options
from tornado.web import RequestHandler, RedirectHandler

_logger = logging.getLogger(__name__)


PORT = 8882

# BACKEND_HOST = "http://localhost:8880/"

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')


# --- Web application boilerplate: ---

def main():
    options.parse_command_line()

    routes = [
    ]
    application = tornado.web.Application(
        routes,
        template_path=TEMPLATES_DIR,
        debug=True,
    )

    _logger.info("Listening on port %d", PORT)
    application.listen(PORT)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    import sys
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    main()
