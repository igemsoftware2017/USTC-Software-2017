from biohub.biobrick.models import Biobrick

from ._base import BiobrickTest


class TestWierd(BiobrickTest):

    def test_j3210(self):

        brick = Biobrick.objects.get(part_name='BBa_J23100')
        brick.fetch()
        self.assertEqual(
            brick.ensure_meta_exists(fetch=True).experiences.count(),
            5
        )
