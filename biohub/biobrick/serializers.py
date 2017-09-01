from rest_framework import serializers
from haystack.models import SearchResult
from haystack.utils.highlighting import Highlighter

# Create your serializers here.
from biohub.utils.rest.serializers import bind_model, ModelSerializer
from .models import Biobrick


@bind_model(Biobrick)
class BiobrickSerializer(ModelSerializer):
    urlset = serializers.SerializerMethodField()

    class Meta:
        model = Biobrick
        fields = ('part_name', 'sequence', 'short_desc', 'description', 'uses',
                  'urlset')
        read_only_fields = ['__all__']

    def get_urlset(self, obj):
        urlset = {}

        if hasattr(obj, 'part_name'):
            urlset['part'] = 'http://parts.igem.org/Part:%s' % obj.part_name
            urlset['related_parts'] = 'http://parts.igem.org/cgi/partsdb/related.cgi?part=%s' % obj.part_name
            urlset['gb_download'] = 'http://www.cambridgeigem.org/gbdownload/%s.gb' % obj.part_name

        return urlset

    def to_representation(self, obj):
        ret = super(BiobrickSerializer, self).to_representation(obj)
        if isinstance(obj, SearchResult):
            querydict = self.context['request'].query_params
            if 'highlight' in querydict:
                ret['short_desc'] = obj.highlighted[0]
                highlighter = Highlighter(querydict.get('q', ''),
                                          html_tag='div', css_class='highlight')
                ret['part_name'] = highlighter.highlight(ret['part_name'])
            else:
                ret['short_desc'] = obj.text
        return ret
