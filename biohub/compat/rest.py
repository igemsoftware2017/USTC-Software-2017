from urllib import parse as urlparse
from rest_framework.utils import urls


def replace_query_param(url, key, val):
    """
    Hacked this function to drop scheme and netloc.
    """
    (scheme, netloc, path, query, fragment) = urlparse.urlsplit(url)
    query_dict = urlparse.parse_qs(query, keep_blank_values=True)
    query_dict[key] = [val]
    query = urlparse.urlencode(sorted(list(query_dict.items())), doseq=True)
    return urlparse.urlunsplit(('', '', path, query, fragment))


def remove_query_param(url, key):
    """
    Hacked this function to drop scheme and netloc.
    """
    (scheme, netloc, path, query, fragment) = urlparse.urlsplit(url)
    query_dict = urlparse.parse_qs(query, keep_blank_values=True)
    query_dict.pop(key, None)
    query = urlparse.urlencode(sorted(list(query_dict.items())), doseq=True)
    return urlparse.urlunsplit(('', '', path, query, fragment))


urls.replace_query_param = replace_query_param
urls.remove_query_param = remove_query_param
