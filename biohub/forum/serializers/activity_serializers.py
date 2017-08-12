from rest_framework import serializers
from biohub.utils.rest.serializers import bind_model,\
    ModelSerializer
from rest_framework.fields import SkipField
from rest_framework.relations import PKOnlyObject
from ..models import Activity, ActivityParam
from collections import Mapping, OrderedDict


@bind_model(ActivityParam)
class ActivityParamSerializer(ModelSerializer):

    # override from src code
    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes.
        """
        ret = OrderedDict()
        # modify Meta.exclude:
        if instance.type == 'Experience':
            self.Meta.exclude = ('type', 'score')
        elif(instance.type == 'Comment'):
            self.Meta.exclude = ('type', 'score')
        elif instance.type == 'Star':
            self.Meta.exclude = ('type', 'score')
        elif instance.type == 'Rating':
            self.Meta.exclude = ('type', 'intro')
        elif instance.type == 'Watch':
            self.Meta.exclude = ('type', 'expLink', 'score', 'intro')
        fields = self._readable_fields

        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue

            # We skip `to_representation` for `None` values so that fields do
            # not have to explicitly deal with that case.
            #
            # For related fields with `use_pk_only_optimization` we need to
            # resolve the pk value.
            check_for_none = attribute.pk if isinstance(
                attribute, PKOnlyObject) else attribute
            if check_for_none is None:
                ret[field.field_name] = None
            else:
                ret[field.field_name] = field.to_representation(attribute)

        return ret

    class Meta:
        model = ActivityParam
        exclude = ('type',)
        read_only_fields =('user','expLink','score','partName','intro')


@bind_model(Activity)
class ActivitySerializer(ModelSerializer):

    params = ActivityParamSerializer(read_only=True)
    class Meta:
        model = Activity
        exclude = ('user',)
        read_only_fields=('type','params','acttime',)
