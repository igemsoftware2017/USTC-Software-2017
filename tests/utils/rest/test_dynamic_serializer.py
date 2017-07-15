from django.test import TestCase, override_settings


@override_settings(INSTALLED_APPS=[
    'tests.utils.rest'
])
class TestDynamicSerializer(TestCase):

    def test_dynamic(self):
        from tests.utils.rest.models import TestModel
        from biohub.utils.rest.serializers import ModelSerializer

        class Serializer(ModelSerializer):

            class Meta:
                model = TestModel
                fields = '__all__'

        serializer = Serializer(fields=['id'])

        self.assertNotIn('field_a', serializer.fields)
