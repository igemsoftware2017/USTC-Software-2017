from django import template

register = template.Library()


@register.filter
def url(text, target):

    assert hasattr(target, 'get_router_arguments'), \
        "Target %r should define a `get_router_arguments` method." % target

    type, primary_key = target.get_router_arguments()

    return '[[{text}]](({type}))(({primary_key}))'.format(text=text, type=type, primary_key=primary_key)
