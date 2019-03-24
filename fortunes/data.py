"""
Data provider for the backend server.

Reads and caches fortune cookie files from GitHub repositories.
"""

import re

from tornado.gen import multi, WaitIterator
from tornado.httpclient import AsyncHTTPClient


URLS = [
    # collected from https://github.com/search?q=fortunes
    "https://github.com/bmc/fortunes/blob/afb2fe6f0cbfa62a8b5163ecfd702c9c00212baf/fortunes",
    "https://github.com/ruanyf/fortunes/blob/beaa45f036026e74498982c11f417f3c3ab6b571/data/fortunes",
    "https://github.com/arrjay/fortunes/blob/8cf5ceaee2acb39bd2c909ddfb31efa69f58e04b/lyrics",
    "https://github.com/arrjay/fortunes/blob/8cf5ceaee2acb39bd2c909ddfb31efa69f58e04b/breaksys",
    "https://github.com/arrjay/fortunes/blob/8cf5ceaee2acb39bd2c909ddfb31efa69f58e04b/puppet",
    "https://github.com/mmmonk/fortunes/blob/73bc1553e99790b2bbf95fccf0d4c22b197b0d79/mysli_zebrane",
    "https://github.com/sund/fortunes/blob/5168725975b40b4a2e3789d65364f16cf2f79d2e/futurama",
    "https://github.com/sund/fortunes/blob/5168725975b40b4a2e3789d65364f16cf2f79d2e/hitchhiker",
    "https://github.com/sund/fortunes/blob/5168725975b40b4a2e3789d65364f16cf2f79d2e/startrek",
    "https://github.com/sund/fortunes/blob/5168725975b40b4a2e3789d65364f16cf2f79d2e/starwars",
    "https://github.com/sund/fortunes/blob/5168725975b40b4a2e3789d65364f16cf2f79d2e/deepthoughts",
    "https://github.com/sund/fortunes/blob/5168725975b40b4a2e3789d65364f16cf2f79d2e/firefly",
]


parse_github_url = re.compile(
    r'^https?://(?:www\.)?github.com/'
    r'(?P<owner>[^/]+)/'
    r'(?P<repo>[^/]+)/'
    r'blob/(?P<branch>[^/]+)/'
    r'(?P<path>.+)',
    re.I).match

build_raw_download_url = "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}".format


def raw_url(github_url):
    """
    >>> raw_url('https://github.com/arrjay/fortunes/blob/master/lyrics')
    (('arrjay', 'fortunes', 'lyrics'), 'https://raw.githubusercontent.com/arrjay/fortunes/master/lyrics')
    """
    parts = parse_github_url(github_url)
    if not parts:
        raise ValueError("Invalid github URL found")
    parts = parts.groupdict()
    return (
        (parts['owner'], parts['repo'], parts['path']),
        build_raw_download_url(**parts)
    )


def parse_response(response):
    data = response.body
    # assume it's UTF-8, unless it's not
    try:
        data = data.decode('utf8')
    except UnicodeDecodeError:
        data = data.decode('latin1')
    # 'parse' fortune file format by splitting the entries
    return re.split(r'\s*%\s+', data)


async def download(urls=URLS):
    """
    Download and parse the given URLs.
    """
    result = {}

    # download all files in parallel and wait for all results
    http_client = AsyncHTTPClient()
    files = await multi({
        key: http_client.fetch(url)
        for key, url in map(raw_url, urls)
    })

    # process all downloaded files sequentially
    for key, response in files.items():
        result[key] = parse_response(response)

    return result


async def download_interleaved(urls=URLS):
    """
    Download and parse the given URLs.
    Processes responses as they come in to minimise the overall latency.
    """
    keys = {
        url: key
        for key, url in map(raw_url, urls)
    }

    # download all files in parallel and process them as they come in
    http_client = AsyncHTTPClient()
    futures = [
        http_client.fetch(url)
        for url in keys
    ]

    result = {
        keys[response.request.url]: parse_response(response)
        async for response in WaitIterator(*futures)
    }

    return result
