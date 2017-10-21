

class RelationshipBuilder:

    def __init__(self):
        from biohub.biomap.storage import storage

        self._storage = storage

    def build(self, part_name, subparts=None, force=False):

        if not force and self._storage.exists(part_name) and self._storage.exists('rev_' + part_name):
            return

        if subparts is None:
            from biohub.biobrick.models import Part

            try:
                part = Part.objects.get(part_name=part_name)
            except Part.DoesNotExist:
                return False

            subparts = part.ruler['sub_parts']

        return self._build(part_name, subparts)

    def _build(self, part_name, subparts):

        self._storage.sadd(part_name, 0)
        self._storage.sadd('rev_' + part_name, 0)

        for part in subparts:

            name = 'BBa_' + part['short_name']
            self._storage.sadd(part_name, name)
            self._storage.sadd('rev_' + name, part_name)


builder = RelationshipBuilder()
