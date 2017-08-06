from copy import deepcopy


class WebsocketDataDecodeError(Exception):
    pass


def encode(handler_name, data):
    """
    Combines `handler_name` and `data` to be a dict.
    """

    assert isinstance(handler_name, str), \
        ("`handler_name` should be a string, unexceptedly got `%r`."
         % type(handler_name))

    return {
        'handler': handler_name,
        'data': deepcopy(data)
    }


def decode(content):
    """
    Returns a (handler_name, data) tuple.

    This function extracts the incoming content (a dict) to more detailed
    information.
    """

    assert isinstance(content, dict), \
        ("`content` should be a dict, unexceptedly got `%r`."
         % type(content))

    missing_fields = {'handler', 'data'} - set(content)

    if missing_fields:
        raise WebsocketDataDecodeError(
            "Fields %s missing." % ', '.join(missing_fields))

    return content['handler'], content['data']
