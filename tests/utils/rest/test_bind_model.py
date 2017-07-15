from django.test import TestCase, override_settings


@override_settings(INSTALLED_APPS=['tests.utils.rest'])
class TestBindModel(TestCase):

    def setUp(self):
        import imp
        import biohub.utils.rest.serializers as bs
        self.old = (
            bs.bind_model.model_serializer_mapping)
        imp.reload(bs)

    def tearDown(self):
        import biohub.utils.rest.serializers as bs
        bs.bind_model.model_serializer_mapping = self.old

    def test_override(self):
        from biohub.utils.rest.serializers import bind_model, get_by_model
        from rest_framework.serializers import ModelSerializer
        from tests.utils.rest.models import TestModel

        @bind_model(TestModel, can_override=True)
        class SerializerA(ModelSerializer):

            class Meta:
                model = TestModel

        @bind_model(TestModel)
        class SerializerB(ModelSerializer):

            class Meta:
                model = TestModel

        self.assertIs(get_by_model(TestModel), SerializerB)

    def test_bind(self):
        from biohub.utils.rest.serializers import bind_model, get_by_model
        from rest_framework.serializers import ModelSerializer
        from tests.utils.rest.models import TestModel

        @bind_model(TestModel)
        class TestModelSerializer(ModelSerializer):

            class Meta:
                model = TestModel

        self.assertIs(
            get_by_model(TestModel),
            TestModelSerializer
        )

        with self.assertRaises(KeyError) as cm:
            @bind_model(TestModel)
            class AnotherTestSerializer(ModelSerializer):

                class Meta:
                    model = TestModel

        self.assertIn('bound', str(cm.exception))
