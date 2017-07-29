from rest_framework import serializers


class PluginSerializer(serializers.Serializer):

    name = serializers.CharField(read_only=True)
    author = serializers.CharField(read_only=True)
    title = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)

    class Meta:
        fields = '__all__'
