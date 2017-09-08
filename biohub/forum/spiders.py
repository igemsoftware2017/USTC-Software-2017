import json
import logging
import re

import requests
import html2text
from bs4 import BeautifulSoup
from django.db import transaction

from biohub.forum.models import Brick, Article

GENE_MAP = {'a': 't', 't': 'a', 'c': 'g', 'g': 'c'}


class BrickSpider:

    base_site = 'http://parts.igem.org/'
    registry_base_site = 'http://parts.igem.org/cgi/xml/part.cgi?'
    logger = logging.getLogger(__name__)

    basic_info_regexps = {
        'designer': re.compile(r'Designed by:\s*(.*?)\s*&nbsp;'),
        'group_name': re.compile(r'Group:\s*(.*?)\s*&nbsp;'),
        'part_type': re.compile(r"<div style='.*?'\s*title='Part Type'>\s*(.*?)</div>"),
        'nickname': re.compile(r"<div style='.*?'\s*type='Nickname'>\s*(.*?)</div>")
    }

    @staticmethod
    def reverse_sequence(sequence_a):
        return ''.join(GENE_MAP.get(char, '') for char in sequence_a)

    def fill_from_page(self, brick_name, brick=None):

        with transaction.atomic():
            return self._fill_from_page(brick_name, brick)

    def _fill_from_page(self, brick_name, brick=None):
        """
        Brick: class from models.Model
        brick_name: like 'K314110'
         """
        # final URL: http://parts.igem.org/Part:BBa_K314110
        if brick is None:
            brick = Brick(name=brick_name)

        raw_response = requests.get(
            BrickSpider.base_site + 'Part:BBa_' + brick_name
        )
        if raw_response.status_code == 404:
            raise Exception('The part does not exist on iGEM\'s website')

        raw_html = raw_response.text
        soup = BeautifulSoup(raw_html, "lxml")

        # fill name
        brick.name = brick_name

        # fetch Designer
        for field, exp in self.basic_info_regexps.items():
            search_result = exp.search(raw_html)
            setattr(
                brick, field,
                search_result.group(1) if search_result else ''
            )

        sequence_result = re.search(r'<script>\s*(var\s*sequence.*?)\s*</script>', raw_html)
        if sequence_result is not None:
            raw_bioinfo = sequence_result.group(1)

            seq_a_result = re.search(r"String\('(.*?)'\)", raw_bioinfo)
            brick.sequence_a = seq_a_result.group(1) if seq_a_result is not None else ''
            brick.sequence_b = BrickSpider.reverse_sequence(brick.sequence_a)

            sub_parts_result = re.search(r"subParts.*?new Array\s*\((.+?)\);", raw_bioinfo)
            sub_parts_data = sub_parts_result.group(1) if sub_parts_result is not None else ''
            brick.sub_parts = ','.join(
                re.findall(
                    r"Part\s*\(\d*,\s*'(.*?)'.*?\)",
                    sub_parts_data
                )
            )

            result = re.search(r'seqFeatures.*?new Array\s*\((.+?)\)', raw_bioinfo)
            if result is not None:
                seqFeatureList = re.findall(
                    r"\['(.*?)'\s*,\s*(\d*)\s*,\s*(\d*)\s*,\s*'(.*?)',(\d*)\s*",
                    result.group(1)
                )
                seq_features = [
                    dict(
                        feature_type=each[0],
                        start_loc=int(each[1]),
                        end_loc=int(each[2]),
                        name=each[3],
                        reserve=bool(int(each[4] or '0')),
                    )
                    for each in seqFeatureList
                ]
            else:
                seq_features = []
        else:
            raw_response = requests.get(
                BrickSpider.registry_base_site + 'part=BBa_' + brick_name)
            _soup = BeautifulSoup(raw_response.text, "lxml-xml")
            feature_set = _soup.find_all('feature')
            seq_features = [
                dict(
                    feature_type=feature.type.text,
                    start_loc=int(feature.startpos.text),
                    end_loc=int(feature.endpos.text),
                    name=feature.title.text,
                    reserve=feature.direction.text == 'reverse',
                )
                for feature in feature_set
            ]
            brick.sequence_a = _soup.find('seq_data').text
            brick.sequence_b = BrickSpider.reverse_sequence(brick.sequence_a)
            subparts = _soup.find('deep_subparts').find_all('subpart')
            subpart_set = [subpart.name.text[4:] for subpart in subparts]
            brick.sub_parts = ','.join(subpart_set)

        # fetch assembly compatibility
        div = soup.find(class_='compatibility_div')
        if div is not None:
            brick.assembly_compatibility = json.dumps([
                'box_green' in item['class']
                for item in div.ul.find_all('li')
            ])
        else:
            brick.assembly_compatibility = ''

        divs = soup.find(id='part_status_wrapper').find_all('div')
        # fetch release status
        brick.part_status = divs[0].text
        # fetch sample status
        brick.sample_status = divs[1].text
        # fetch experience status
        brick.experience_status = divs[2].text
        # fetch use number
        result = re.search(r"(\d+)\s*", divs[3].text)
        brick.use_num = int(result.group(1)) if result is not None else 0
        # fetch twin num(if exists)
        result = re.search(r"(\d+)\s*Twins.*?", divs[4].text)
        brick.twin_num = int(result.group(1)) if result is not None else 0

        # fetch parameters
        parameters = []
        div = soup.find(id='parameters')
        if div.table.tr.td.text == 'None':
            brick.parameters = ''
        else:
            for entry in div.table.find_all('tr'):
                parameters.append(
                    [element.text for element in entry.find_all('td')]
                )
            brick.parameters = json.dumps(parameters)

        # fetch categories
        div = soup.find(id='categories')
        result = re.search(r'(//.*?)\s*\Z', div.text, re.DOTALL)
        brick.categories = result.group(1) if result is not None else ''

        soup = soup.find('div', id='mw-content-text')
        # remove scripts, panel, and compatibility infos
        scriptset = soup.find_all(name='script')
        for each in scriptset:
            each.extract()
        panel = soup.find(id='sequencePaneDiv')
        if panel:
            panel.extract()
        panel = soup.find(class_='h3bb', text='Sequence and Features')
        if panel:
            panel.extract()
        compat = soup.find(class_='compatibility_div')
        if compat:
            compat.parent.extract()

        # restore images by supplementing URLs
        newdoc = re.sub(r'="/(.*?")', '="' +
                        BrickSpider.base_site + r'\1', str(soup))
        h = html2text.HTML2Text()
        h.body_width = 1000  # must not break one line into multiple lines
        markdown = h.handle(str(newdoc))
        article = Article.objects.create(text=markdown)  # attach no files
        brick.document = article
        brick.seq_features = seq_features
        brick.save()

        return True


class ExperienceSpider:
    """
    Before using the spider, the brick witch the experience is attached to should exist in database.
    """
    base_site = 'http://parts.igem.org/'
    logger = logging.getLogger(__name__)

    def fill_from_page(self, brick_name):
        with transaction.atomic():
            return self._fill_from_page(brick_name)

    def _fill_from_page(self, brick_name):

        brick = Brick.objects.get(name=brick_name)

        raw_response = requests.get(
            ExperienceSpider.base_site + 'Part:BBa_' + brick_name + ':Experience')
        if raw_response.status_code == 404:
            raise Exception('The experience does not exist on iGEM\'s website')

        raw_html = raw_response.text
        soup = BeautifulSoup(raw_html, "lxml")
        soup = soup.find('div', id='mw-content-text')

        for rubbish in soup.find_all('p', text=re.compile('\x7fUNIQ')):
            rubbish.extract()
        # determine the structure of user reviews (there are 2 types)
        beginning = soup.find(id='User_Reviews').parent
        tables = beginning.find_next_siblings('table')
        if tables:
            # the first type
            for entry in tables:
                tds = entry.tr.find_all('td')
                author_name = re.search(
                    r'\s*(.*?)\s*$',
                    tds[0].p.text,
                    re.DOTALL
                ).group(1)
                experience, _ = brick.experience_set.get_or_create(
                    author_name=author_name,
                    defaults={'title': '', 'brick': brick}
                )
                content_html = tds[1]
                # change images' URLs to absolute ones
                restored_content = re.sub(
                    r'="/(.*?")',
                    '="' + ExperienceSpider.base_site + r'\1',
                    str(content_html)
                )
                h = html2text.HTML2Text()
                h.body_width = 1000
                markdown = h.handle(restored_content)
                if experience.content is None:
                    article = Article.objects.create(text=markdown)
                    experience.content = article
                else:
                    experience.content.text = markdown
                    experience.content.save()
                experience.save()
        else:
            content = None
            experience = None
            for para in beginning.find_next_siblings('p'):
                matched = re.match(r'\s*igem.{1,60}$', para.text, re.IGNORECASE)
                if matched:
                    # save previous collected content
                    # change images' URLs to absolute ones
                    if content and experience:
                        restored_content = re.sub(
                            r'="/(.*?")',
                            '="' + ExperienceSpider.base_site + r'\1',
                            str(content)
                        )
                        h = html2text.HTML2Text()
                        h.body_width = 1000
                        markdown = h.handle(restored_content)
                        if experience.content is None:
                            article = Article.objects.create(text=markdown)
                            experience.content = article
                        else:
                            experience.content.text = markdown
                            experience.content.save()
                        experience.save()

                    content = None
                    # create the next user review
                    author_name = matched.group(0)
                    experience, _ = brick.experience_set.get_or_create(
                        author_name=author_name,
                        defaults={'title': '', 'brick': brick}
                    )
                else:
                    if experience:  # created last time in 'if' branch
                        # collect contents
                        if content is None:
                            content = BeautifulSoup('<p></p>', "lxml")
                        content.p.append(para)
                    else:
                        # so this paragraph doesn't belong to any user reviews, skip it.
                        pass

            pass
        return True
