from django.test import TestCase
from biohub.forum.models import Brick
from biohub.forum import spiders

class BrickSpiderTests(TestCase):
    ''' test with some parts on igem websites '''
    def test1(self):
        ''' test with page: http://parts.igem.org/Part:BBa_I718017  '''
        brickspider=spiders.BrickSpider()
        brick_id = brickspider.fill_from_page(brick_name='I718017')
        brick = Brick.objects.get(name='I718017')
        self.assertEqual(brick.designer,'Eimad Shotar')
        self.assertEqual(brick.group_name,'iGEM07_Paris')
        self.assertEqual(brick.part_type,'DNA')
        self.assertEqual(brick.nickname,'lox71')
        self.assertEqual(brick.part_status,'Released HQ 2013')
        self.assertEqual(brick.sample_status,'Sample In stock')
        self.assertEqual(brick.experience_status,'1 Registry Star')
        self.assertEqual(brick.use_num,14)
        self.assertEqual(brick.twin_num,2)
        # examine assembly_compatibility, subparts, parameters, categories