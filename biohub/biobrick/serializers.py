from django.core.cache import cache
from rest_framework import serializers
from haystack.models import SearchResult

# Create your serializers here.
from biohub.utils.rest.serializers import bind_model, ModelSerializer
from .models import Biobrick
from .highlighter import SimpleHighlighter

SEARCH_RESULT_TIMEOUT = 240


def bbk_search_result_cache_key(pk):
    return "biobrick:search:result:%s" % pk


@bind_model(Biobrick)
class BiobrickSerializer(ModelSerializer):
    urlset = serializers.SerializerMethodField()

    class Meta:
        model = Biobrick
        fields = ('part_name', 'sequence', 'short_desc', 'description', 'uses',
                  'seq_edit_cache', 'urlset')
        read_only_fields = ['__all__']

    def get_urlset(self, obj):
        urlset = {}

        if hasattr(obj, 'part_name'):
            urlset['part'] = 'http://parts.igem.org/Part:%s' % obj.part_name
            urlset['related_parts'] = 'http://parts.igem.org/cgi/partsdb/related.cgi?part=%s' % obj.part_name
            urlset['gb_download'] = 'http://www.cambridgeigem.org/gbdownload/%s.gb' % obj.part_name

        return urlset

    def _get_cached_dict(self):
        cached_result = cache.get(self._cache_key)
        if isinstance(cached_result, dict):
            self._cached_dict = cached_result
            return True
        else:
            return False

    def _set_cached_dict(self, obj, fields):
        cached_dict = {}
        for field in fields:
            cached_dict[field] = getattr(obj, field, None)
        cache.set(self._cache_key, cached_dict, timeout=SEARCH_RESULT_TIMEOUT)
        self._cached_dict = cached_dict

    def to_representation(self, obj):
        ret = super(BiobrickSerializer, self).to_representation(obj)

        if isinstance(obj, SearchResult):

            # To get a fields dict from cache or set a new cache
            self._cache_key = bbk_search_result_cache_key(obj.pk)
            if not self._get_cached_dict():
                self._set_cached_dict(obj.object, [
                    'sequence', 'description', 'seq_edit_cache'
                ])
            ret.update(self._cached_dict)

            # To set highlight
            querydict = self.context['request'].query_params
            if 'highlight' in querydict:
                highlighter = SimpleHighlighter(querydict.get('q', ''),
                                                html_tag='div',
                                                css_class='highlight')
                ret['part_name'] = highlighter.highlight(ret['part_name'])
            if obj.highlighted is not None and len(obj.highlighted) > 0:
                ret['short_desc'] = obj.highlighted[0]

        return ret
