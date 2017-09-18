from biohub.biobrick.models import Biobrick

from ._base import BiobrickTest


class TestBiobrickSpider(BiobrickTest):

    def test1(self):

        brick = Biobrick.objects.get(part_name='BBa_I718017')
        self.assertFalse(brick.meta_exists)
        self.assertTrue(brick.should_fetch)
        brick.fetch()
        self.assertTrue(brick.meta_exists)
        self.assertFalse(brick.should_fetch)

        self.assertEqual(brick.author, 'Eimad Shotar')
        self.assertEqual(brick.group_name, 'iGEM07_Paris')
        self.assertEqual(brick.part_type, 'DNA')
        self.assertEqual(brick.nickname, 'lox71')
        self.assertEqual(brick.part_status, 'Released HQ 2013')
        self.assertEqual(brick.sample_status, 'In stock')
        self.assertEqual(brick.experience_status, '1 Registry Star')
        self.assertEqual(brick.uses, 14)
        self.assertEqual(brick.twin_num, 2)

    def test2(self):

        brick = Biobrick.objects.get(part_name='BBa_B0015')
        self.assertFalse(brick.meta_exists)
        self.assertTrue(brick.should_fetch)
        brick.fetch()
        self.assertTrue(brick.meta_exists)
        self.assertEqual(brick.author, 'Reshma Shetty')
        self.assertEqual(brick.group_name, 'Antiquity')
        self.assertEqual(brick.part_type, 'Terminator')
        self.assertEqual(brick.nickname, '')
        self.assertEqual(brick.part_status, 'Released HQ 2013')
        self.assertEqual(brick.sample_status, 'In stock')
        self.assertEqual(brick.experience_status, '1 Registry Star')
        self.assertEqual(brick.uses, 3210)
        self.assertEqual(brick.twin_num, 16)


class TestExperienceSpider(BiobrickTest):

    def test1(self):
        brick = Biobrick.objects.get(part_name='BBa_B0015')
        meta = brick.ensure_meta_exists(fetch=True)
        brick.fetch()

        self.assertGreater(meta.experiences.count(), 0)
