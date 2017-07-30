import requests
import re
import logging
from biohub.forum.models import Brick, Experience, SeqFeature


class BrickSpider:
    base_site = 'http://parts.igem.org/'
    logger = logging.getLogger(__name__)

    def fill_from_page(self, brick_name, brick=None):
        """
        Brick: class from models.Model
        brick_name: like 'K314110'
         """
        # final URL: http://parts.igem.org/Part:BBa_K314110
        if brick is None:
            brick = Brick(name=brick_name)
        raw_response = requests.get(
            BrickSpider.base_site + 'Part:BBa_' + brick_name)
        raw_data = raw_response.text
        # fill name
        brick.name = brick_name
        # fetch Designer
        try:
            brick.designer = re.search(
                'Designed by:\s*(.*?)\s*&nbsp', raw_data).group(1)
            brick.group_name = re.search(
                'Group:\s*(.*?)\s*&nbsp', raw_data).group(1)
            brick.part_type = re.search(
                '<div style=\'.*?\'\s*title=\'Part Type\'>\s*(.*?)</div>', raw_data).group(1)
            brick.nickname = re.search(
                '<div style=\'.*?\'\s*type=\'Nickname\'>\s*(.*?)</div>', raw_data).group(1)
            raw_bioinfo = re.search(
                '<script>\s*(var\s*sequence.*?)\s*</script>', raw_data).group(1)
            brick.sequence_a = re.search(
                'String\(\'(.*?)\'\)', raw_bioinfo).group(1)
            sequence_b = ''
            for char in list(brick.sequence_a):
                if char == 'a':
                    sequence_b += 't'
                if char == 't':
                    sequence_b += 'a'
                if char == 'c':
                    sequence_b += 'g'
                if char == 'g':
                    sequence_b += 'c'
            dna_position = ''
        except Exception as e:
            self.logger.error('Error during parsing contents.')
            self.logger.error(e)
            return False
            # If errors occur during parsing contents,
            # logging and quiting rather than saving false data may be better

        # fetch raw bioinfo

        brick.sequence_a = ''

        brick.save()
        return True


class ExperienceSpider:
    """
    Before using the spider, the brick witch the experience is attached to should exist in database.
    """
    def fill_from_page(self, brick_name, experience=None):
        if experience is None:
            experience = Experience(title='Part: ' + brick_name + ': Experience',
                                    brick=Brick.objects.get(name=brick_name))

        experience.save()
        return True


class SeqFeatureSpider:
    """
    Before using the spider, the brick witch the seq_feature is attached to should exist in database.
    """
    def fill_from_page(self, brick_name, seq_feature=None):
        if seq_feature is None:
            seq_feature = SeqFeature(brick=Brick.objects.get(name=brick_name))

        seq_feature.save()
        return True
