from django.test import TestCase
from biohub.forum.models import Brick
from biohub.forum import spiders
import tempfile
import os


class BrickSpiderTests(TestCase):
    ''' test with some parts on igem websites '''

    def test1(self):
        ''' test with page: http://parts.igem.org/Part:BBa_I718017  '''
        brickspider = spiders.BrickSpider()
        brickspider.fill_from_page(brick_name='BBa_I718017')
        brick = Brick.objects.get(name='BBa_I718017')
        self.assertEqual(brick.designer, 'Eimad Shotar')
        self.assertEqual(brick.group_name, 'iGEM07_Paris')
        self.assertEqual(brick.part_type, 'DNA')
        self.assertEqual(brick.nickname, 'lox71')
        self.assertEqual(brick.part_status, 'Released HQ 2013')
        self.assertEqual(brick.sample_status, 'Sample In stock')
        self.assertEqual(brick.experience_status, '1 Registry Star')
        self.assertEqual(brick.use_num, 14)
        self.assertEqual(brick.twin_num, 2)
        # examine assembly_compatibility, subparts, parameters, categories

    def test2(self):
        ''' test with page: http://parts.igem.org/Part:BBa_B0015'''
        brickspider = spiders.BrickSpider()
        brickspider.fill_from_page(brick_name='BBa_B0015')
        brick = Brick.objects.get(name='BBa_B0015')
        self.assertEqual(brick.designer, 'Reshma Shetty')
        self.assertEqual(brick.group_name, 'Antiquity')
        self.assertEqual(brick.part_type, 'Terminator')
        self.assertEqual(brick.nickname, '')
        self.assertEqual(brick.part_status, 'Released HQ 2013')
        self.assertEqual(brick.sample_status, 'Sample In stock')
        self.assertEqual(brick.experience_status, '1 Registry Star')
        self.assertEqual(brick.use_num, 3210)
        self.assertEqual(brick.twin_num, 16)

    def test3(self):
        ''' subparts test
        test with page: http://parts.igem.org/Part:BBa_I6084
        I just examine the values in debug mode.
        '''
        brickspider = spiders.BrickSpider()
        brickspider.fill_from_page(brick_name='BBa_I6084')
        Brick.objects.get(name='BBa_I6084')

    def test4(self):
        ''' test with page: BBa_K314110'''
        spiders.BrickSpider().fill_from_page(brick_name='BBa_K314110')
        ''' test a page with no sequence feature panel'''
        spiders.BrickSpider().fill_from_page(brick_name='BBa_B1003')
        Brick.objects.get(name='BBa_B1003')
        spiders.BrickSpider().fill_from_page(brick_name='BBa_J23106')
        pass


class ExperienceSpiderTests(TestCase):
    ''' test with some parts on igem websites '''

    def test1(self):
        ''' test with page: http://parts.igem.org/Part:BBa_B0015:Experience '''
        brickspider = spiders.BrickSpider()
        brickspider.fill_from_page(brick_name='BBa_B0015')
        experiencespider = spiders.ExperienceSpider()
        experiencespider.fill_from_page(brick_name='BBa_B0015')
        brick = Brick.objects.get(name='BBa_B0015')
        experiences = brick.experience_set.all()
        for experience in experiences:
            markdown = experience.content.text
            with open(os.path.join(tempfile.gettempdir(), 'exp' + experience.author_name + '.md'), 'w') as f:
                f.write(markdown)
                # examine manually whether the experiences are rendered properly.
                # the output files can be found at Biohub-Server/. remove them after checking.
        pass
