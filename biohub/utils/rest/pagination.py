from rest_framework import pagination

__all__ = ['factory']


def factory(base_class_name, **options):
    """
    A factory function to conveniently create pagination class. Base class is
    specified by `base_class_name`, which will be used to locate a class in
    `rest_framework.pagination` module. Extra options will be applied as class
    members of the new pagination class.
    """

    base_cls = getattr(pagination, base_class_name, 'None')

    assert base_cls is not None, \
        'Cannot resolve %r into pagination class.' % base_class_name

    options.setdefault('ordering', 'id')

    return type(
        'Pagination',
        (base_cls,),
        options
    )
