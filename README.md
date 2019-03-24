A Tornado 6 Tutorial
====================

This is a tutorial for the Python web framework [Tornado](http://www.tornadoweb.org/),
version 6.0 and later.
It uses the standard [asyncio](https://docs.python.org/3/library/asyncio.html#module-asyncio)
event loop, and adds support for web servers and clients, template handling, websockets,
and much more.

This tutorial shows an example of a web frontend (under ``frontend/``) and a web service
backend (under ``fortunes/``.
It reads fortune cookie files from several other github repositories and returns a combined
page (or JSON response) for them.

The examples show how to do parallel HTTP requests (``frontend/app.py``, ``fortunes/data.py``,
``getparallel.py``), how to write a simple HTTP webserver (``frontend/app.py``), and a somewhat
less simple web service backend server (``fortunes/serve.py``).
