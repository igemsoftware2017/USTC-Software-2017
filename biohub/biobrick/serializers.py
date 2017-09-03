import json

from django.core.cache import cache
from rest_framework import serializers
from haystack.models import SearchResult

from biohub.utils.rest.serializers import bind_model, ModelSerializer
from .models import Biobrick
from .highlighter import SimpleHighlighter

SEARCH_RESULT_TIMEOUT = None


def bbk_search_result_cache_key(pk):
    return "biobrick:search:results:%s" % pk


@bind_model(Biobrick)
class BiobrickSerializer(ModelSerializer):
    urlset = serializers.SerializerMethodField()

    class Meta:
        model = Biobrick
        fields = ('part_name', 'sequence', 'short_desc', 'description', 'uses',
                  'urlset', 'ac', 'ruler')
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

    def _set_cached_dict(self, obj):
        _getattr = lambda name: getattr(obj, name, None)  # noqa

        cached_dict = {
            'description': _getattr('description'),
            'ac': json.loads(_getattr('ac') or 'null'),
            'ruler': json.loads(_getattr('ruler') or 'null')
        }

        cache.set(self._cache_key, cached_dict, timeout=SEARCH_RESULT_TIMEOUT)
        self._cached_dict = cached_dict

    def to_representation(self, obj):
        ret = super(BiobrickSerializer, self).to_representation(obj)
        if isinstance(obj, SearchResult):

            # To get a fields dict from cache or set a new cache
            self._cache_key = bbk_search_result_cache_key(obj.pk)
            if not self._get_cached_dict():
                self._set_cached_dict(obj.object)
            ret.update(self._cached_dict)

            # To get short_desc, which is stored as text in the index
            if obj.highlighted is not None and len(obj.highlighted) > 0:
                ret['short_desc'] = obj.highlighted[0]
            else:
                ret['short_desc'] = obj.text

            # To set highlight
            querydict = self.context['request'].query_params
            if 'highlight' in querydict:
                highlighter = SimpleHighlighter(querydict.get('q', ''),
                                                html_tag='div',
                                                css_class='highlight')
                ret['part_name'] = highlighter.highlight(ret['part_name'])
        elif isinstance(obj, Biobrick):

            self._cache_key = bbk_search_result_cache_key(obj.pk)
            if not self._get_cached_dict():
                self._set_cached_dict(obj)
            ret.update(self._cached_dict)

        return ret
