from rest_framework import pagination, response

__all__ = ['factory']


def factory(base_class_name, **options):
    """
    A factory function to conveniently create pagination class. Base class is
    specified by `base_class_name`, which will be used to locate a class in
    `rest_framework.pagination` module. Extra options will be applied as class
    members of the new pagination class.
    """

    base_cls = getattr(pagination, base_class_name, None)

    assert base_cls is not None, \
        'Cannot resolve %r into pagination class.' % base_class_name

    options.setdefault('ordering', 'id')

    return type(
        'Pagination',
        (base_cls,),
        options
    )


def paginate_queryset(queryset, view):
    """
    Uses `view`'s `paginate_queryset` method to get a page object and returns
    a response.
    """
    page = view.paginate_queryset(queryset)
    if page is not None:
        serializer = view.get_serializer(page, many=True)
        return view.get_paginated_response(serializer.data)

    serializer = view.get_serializer(queryset, many=True)
    return response.Response(serializer.data)
