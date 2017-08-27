from haystack.fields import CharField


class MultipleCharField(CharField):

    def prepare(self, obj):
        values = []
        current_objects = [obj]

        for attr in self.model_attr:
            attrs = attr.split('__')
            resolved = self.resolve_attributes_lookup(current_objects, attrs)
            if len(resolved) > 0 and resolved[0] is not None:
                values += resolved

        return '\n\n'.join(values)
