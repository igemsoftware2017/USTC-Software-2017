from functools import partial

from rest_framework import serializers as rest_serializers


class bind_model(object):

    """
    A decorator to bind a model with its serializer.
    """

    model_serializer_mapping = {}

    def __init__(self, model_cls, can_override=False):
        if (model_cls in self.model_serializer_mapping and
                not self.model_serializer_mapping[model_cls]['can_override']):
            raise KeyError(
                'Model %r has been bound with'
                ' serializer %r.' % (
                    model_cls,
                    self.model_serializer_mapping[model_cls]
                )
            )
        self.__model_cls = model_cls
        self.__can_override = can_override

    def __call__(self, serializer_cls):
        self.model_serializer_mapping[self.__model_cls] = {
            'serializer': serializer_cls,
            'can_override': self.__can_override
        }
        return serializer_cls

    @classmethod
    def get_model_serializer(cls, model_cls):
        """
        Obtain the serializer with provided model class.
        """
        if model_cls not in cls.model_serializer_mapping:
            raise KeyError(
                'Model %r has not been bound.' % model_cls
            )
        return cls.model_serializer_mapping[model_cls]['serializer']


get_by_model = bind_model.get_model_serializer


class DynamicSerializerMixin(object):
    """
    An enhanced serializer mixin, providing the ability to
    specify fields during runtime.
    """

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super(DynamicSerializerMixin, self).__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields.keys())

            for field_name in existing - allowed:
                self.fields.pop(field_name)

    @classmethod
    def creator(cls, *args, **kwargs):
        result = partial(cls, *args, **kwargs)

        result.creator = partial(partial, result)

        return result


class ModelSerializer(
        DynamicSerializerMixin, rest_serializers.ModelSerializer):
    pass


class HyperlinkedModelSerializer(
        DynamicSerializerMixin, rest_serializers.HyperlinkedModelSerializer):
    pass
