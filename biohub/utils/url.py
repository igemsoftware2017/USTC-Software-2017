import urllib.parse as parse


def add_params(url, **params):
    """
    Append or replace query params in `url` using `params`.
    """
    url = parse.unquote(url)
    parsed = parse.urlparse(url)
    existing = dict(parse.parse_qsl(parsed.query))
    existing.update(params)
    return parse.urlunparse(
        parse.ParseResult(
            scheme=parsed.scheme,
            netloc=parsed.netloc,
            path=parsed.path,
            params=parsed.params,
            query=parse.urlencode(existing),
            fragment=parsed.fragment
        )
    )


def get_params(url):
    """
    Extract query parameters from url, and return as a dict.
    """
    url = parse.unquote(url)
    parsed = parse.urlparse(url)
    return dict(parse.parse_qsl(parsed.query))
