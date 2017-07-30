from rest_framework import serializers
from biohub.utils.rest.serializers import bind_model,\
    ModelSerializer
from ..models import Article
from biohub.core.files.models import File


@bind_model(Article)
class ArticleSerializer(ModelSerializer):
    file_ids = serializers.PrimaryKeyRelatedField(many=True, write_only=True,
                                                  queryset=File.objects.all())

    class Meta:
        model = Article
        fields = ('text', 'file_ids')

    def create(self, validated_data):
        files = validated_data.pop('file_ids')
        article = Article.objects.create(**validated_data)
        for file in files:
            article.files.add(file)
        article.save()
        return article

    def update(self, instance, validated_data):
        if 'file_ids' in validated_data:
            files = validated_data.pop('file_ids')
            files_before = instance.files.all()
            ids_before = [file.id for file in files_before]
            for file in files:
                if file.id in ids_before:
                    # remove the files that will still exist,
                    # so that only the files that no longer belong to the article will be left
                    ids_before.remove(file.id)
                else:
                    instance.files.add(file)
            for file_id in ids_before:
                instance.files.remove(File.objects.get(pk=file_id))
        instance.text = validated_data.get('text', instance.text)
        instance.save()
        return instance
