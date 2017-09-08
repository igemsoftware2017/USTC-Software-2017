from rest_framework.fields import Field


class PackedField(Field):

    def to_representation(self, obj):
        return obj

    def to_internal_value(self, data):
        return data
