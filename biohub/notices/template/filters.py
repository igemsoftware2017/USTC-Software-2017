from django import template

register = template.Library()


@register.filter
def url(text, url):
    return '[[{text}]](({url}))'.format(text=text, url=url)
