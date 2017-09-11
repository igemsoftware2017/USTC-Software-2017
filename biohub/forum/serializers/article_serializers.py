from django.db import transaction
from rest_framework import serializers

from biohub.utils.rest.serializers import bind_model, ModelSerializer
from ..models import Article
from biohub.core.files.models import File


@bind_model(Article)
class ArticleSerializer(ModelSerializer):
    file_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True,
        queryset=File.objects.only('id')
    )

    class Meta:
        model = Article
        fields = ('text', 'file_ids', 'digest')
        read_only_fields = ('digest',)

    def create(self, validated_data):
        files = validated_data.pop('file_ids')
        with transaction.atomic():
            article = Article.objects.create(**validated_data)
            article.files.add(*files)
        return article

    def update(self, instance, validated_data):
        with transaction.atomic():
            if 'file_ids' in validated_data:
                files = validated_data.pop('file_ids')
                instance.files.set(File.objects.only('id').filter(pk__in=files), clear=True)
            instance.text = validated_data.get('text', instance.text)
            instance.save()
        return instance
