import json
import logging
import re

import requests
from bs4 import BeautifulSoup

from biohub.forum.models import Brick, Article
from biohub.utils.htm2text import html2text


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
        if raw_response.status_code == 404:
            raise Exception('The part does not exist on iGEM\'s website')
        raw_html = raw_response.text
        # fill name
        brick.name = brick_name
        # fetch Designer
        # brick.save()
        brick.designer = re.search(
            'Designed by:\s*(.*?)\s*&nbsp', raw_html).group(1)
        brick.group_name = re.search(
            'Group:\s*(.*?)\s*&nbsp', raw_html).group(1)
        brick.part_type = re.search(
            '<div style=\'.*?\'\s*title=\'Part Type\'>\s*(.*?)</div>', raw_html).group(1)
        brick.nickname = re.search(
            '<div style=\'.*?\'\s*type=\'Nickname\'>\s*(.*?)</div>', raw_html).group(1)
        # TODO: add another way of fetch sequence features
        raw_bioinfo = re.search(
            '<script>\s*(var\s*sequence.*?)\s*</script>', raw_html).group(1)
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
        brick.sequence_b = sequence_b
        # dna_position = re.search(
        #     'new Array\(.*?\'dna\',(\d+,\d+).*?\)', raw_bioinfo).group(1)
        # add char field with the suitable validator eg: "23,435" done!
        sub_parts_data = re.search('subParts.*?new Array\s*\((.+?)\);', raw_bioinfo) and re.search(
            'subParts.*?new Array\s*\((.+?)\);', raw_bioinfo).group(1)
        if sub_parts_data:
            sub_parts_list = re.findall(
                'Part\s*\(\d*,\s*\'(.*?)\'.*?\)', sub_parts_data)
            brick.sub_parts = ','.join(sub_parts_list)
        else:
            brick.sub_parts = ''  # for stand-alone bricks
        soup = BeautifulSoup(raw_html, "lxml")
        div = soup.find(id='part_status_wrapper')
        # fetch release status
        div2 = div.find_all('div')[0]
        brick.part_status = div2.text
        # fetch sample status
        div2 = div.find_all('div')[1]
        brick.sample_status = div2.text
        # fetch experience status
        div2 = div.find_all('div')[2]
        brick.experience_status = div2.text
        # fetch use number
        div2 = div.find_all('div')[3]
        if re.search('(\d+)\s*', div2.text):
            brick.use_num = int(re.search('(\d+)\s*', div2.text).group(1))
        else:
            brick.use_num = 0
        # fetch twin num(if exists)
        div2 = div.find_all('div')[4]
        if re.search('(\d+)\s*Twins.*?', div2.text):
            brick.twin_num = int(
                re.search('(\d+)\s*Twins.*?', div2.text).group(1))
        else:
            brick.twin_num = 0
        # fetch assembly compatibility
        div = soup.find(class_='compatibility_div')
        assembly_compatibility = [('box_green' in item['class'])
                                  for item in div.ul.find_all('li')]
        brick.assembly_compatibility = json.dumps(assembly_compatibility)
        # fetch parameters
        parameters = []
        div = soup.find(id='parameters')
        if div.table.tr.td.text == 'None':
            brick.parameters = ''
        else:
            print(div.table.tr.td.text)
            for entry in div.table.find_all('tr'):
                parameters.append(
                    [element.text for element in entry.find_all('td')])
            brick.parameters = json.dumps(parameters)
        # fetch categories
        div = soup.find(id='categories')
        categories = re.search(
            '(//.*?)\s*\Z', div.text, re.DOTALL).group(1)
        brick.categories = categories
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
        newdoc = re.sub('=\"/(.*?\")', '=\"' +
                        BrickSpider.base_site + r'\1', str(soup))
        soup2 = BeautifulSoup(newdoc, "lxml")
        h = html2text.HTML2Text()
        h.body_width = 1000  # must not break one line into multiple lines
        markdown = h.handle(str(soup2))
        article = Article.objects.create(text=markdown)  # attach no files
        brick.document = article
        brick.save()
    # this must be executed after the brick has been saved
        if(re.search(
                'seqFeatures.*?new Array\s*\((.+?)\)', raw_bioinfo)):
            seqFeature_data = re.search(
                'seqFeatures.*?new Array\s*\((.+?)\)', raw_bioinfo).group(1)
            seqFeatureList = re.findall(
                '\[\'(.*?)\'\s*,\s*(\d*)\s*,\s*(\d*)\s*,\s*\'(.*?)\',(\d*)\s*', seqFeature_data)
            for each in seqFeatureList:
                brick.seqFeatures.create(feature_type=each[0], start_loc=int(
                    each[1]), end_loc=int(each[2]), name=each[3], reserve=bool(each[4]))
        # except Exception as e:
        #     self.logger.error('Error during parsing contents.')
        #     self.logger.error(e)
        #     return False
            # If errors occur during parsing contents,
            # logging and quiting rather than saving false data may be better

        return True


class ExperienceSpider:
    """
    Before using the spider, the brick witch the experience is attached to should exist in database.
    """
    base_site = 'http://parts.igem.org/'
    logger = logging.getLogger(__name__)

    def fill_from_page(self, brick_name):
        
        brick = Brick.objects.get(name=brick_name)
        # if experience is None:
        #     experience = Experience(title='Part: ' + brick_name + ': Experience',
        #                             brick=Brick.objects.get(name=brick_name))
        raw_response = requests.get(
            ExperienceSpider.base_site + 'Part:BBa_' + brick_name + ':Experience')
        if raw_response.status_code == 404:
            raise Exception('The experience does not exist on iGEM\'s website')
        raw_html = raw_response.text
        soup = BeautifulSoup(raw_html, "lxml")
        soup = soup.find('div', id='mw-content-text')
        for rubbish in soup.find_all('p', text=re.compile('UNIQ')):
            rubbish.extract()
        # determine the structure of user reviews (there are 2 types)
        beginning = soup.find(id='User_Reviews').parent
        if beginning.find_next_siblings('table'):
            # the first type
            for entry in beginning.find_next_siblings('table'):
                author_name = entry.tr.find_all('td')[0].p.text
                author_name = re.search(
                    '\s*(.*?)\s*$', author_name, re.DOTALL).group(1)
                experience = brick.experience_set.get_or_create(
                    author_name=author_name, defaults={'title': '', 'brick': brick})[0]
                content_html = entry.tr.find_all('td')[1]
                # change images' URLs to absolute ones
                restored_content = re.sub('=\"/(.*?\")', '=\"' +
                                          ExperienceSpider.base_site + r'\1', str(content_html))
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
                if re.match('\s*igem.{1,60}$',para.text,re.IGNORECASE):
                # save previous collected content
                    # change images' URLs to absolute ones
                    if content and experience:
                        restored_content = re.sub('=\"/(.*?\")', '=\"' +
                            ExperienceSpider.base_site + r'\1', str(content))
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
                    author_name = re.match('\s*igem.{1,60}$',para.text,re.IGNORECASE).group(0)
                    experience = brick.experience_set.get_or_create(
                        author_name=author_name, defaults={'title': '', 'brick': brick})[0]
                else:
                    if experience: # created last time in 'if' branch
                        # collect contents
                        if content is None:
                            content = BeautifulSoup('<p></p>',"lxml")
                        content.p.append(para)
                    else:
                        # so this paragraph doesn't belong to any user reviews, skip it.
                        pass


            pass
        return True


# class SeqFeatureSpider:
#     """
#     Before using the spider, the brick witch the seq_feature is attached to should exist in database.
#     """

#     def fill_from_page(self, brick_name, seq_feature=None):
#         if seq_feature is None:
#             seq_feature = SeqFeature(brick=Brick.objects.get(name=brick_name))

#         seq_feature.save()
#         return True
