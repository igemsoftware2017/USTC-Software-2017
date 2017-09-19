import logging
import re

import requests
from requests.exceptions import RequestException
import html2text
from bs4 import BeautifulSoup
from django.db import transaction
from django.utils import timezone

from biohub.forum.models import Article
from biohub.biobrick.models import BiobrickMeta, Biobrick
from biohub.biobrick.exceptions import NetworkError, ResourceNotFoundError


def safe_fetch(url, resource_name):
    try:
        response = requests.get(url)
    except RequestException as e:
        raise NetworkError(resource_name, str(e))
    else:
        if response.status_code == 404:
            raise ResourceNotFoundError(resource_name)

        return response


class BrickSpider:

    base_site = 'http://parts.igem.org/'
    registry_base_site = 'http://parts.igem.org/cgi/xml/part.cgi?'
    logger = logging.getLogger(__name__)

    basic_info_regexps = {
        'group_name': re.compile(r'Group:\s*(.*?)\s*&nbsp;'),
    }

    def fill_from_page(self, brick):

        with transaction.atomic():
            return self._fill_from_page(brick)

    def _fill_from_page(self, brick):

        # final URL: http://parts.igem.org/Part:BBa_K314110
        meta = None
        if isinstance(brick, str):
            brick_name = brick
        elif isinstance(brick, (Biobrick, BiobrickMeta)):
            brick_name = brick.part_name

            if isinstance(brick, BiobrickMeta):
                meta = brick
        else:
            raise TypeError('`brick` should be a string or a Biobrick or a BiobrickMeta, got %r.' % type(brick))

        if meta is None:
            try:
                meta = BiobrickMeta.objects.get(part_name=brick_name)
            except BiobrickMeta.DoesNotExist:
                meta = BiobrickMeta(part_name=brick_name)

        raw_response = safe_fetch(BrickSpider.base_site + 'Part:' + brick_name, brick_name)

        raw_html = raw_response.text
        soup = BeautifulSoup(raw_html, "lxml")

        # fetch Designer
        for field, exp in self.basic_info_regexps.items():
            search_result = exp.search(raw_html)
            setattr(
                meta, field,
                search_result.group(1) if search_result else ''
            )

        divs = soup.find(id='part_status_wrapper').find_all('div')
        # fetch experience status
        meta.experience_status = divs[2].text
        # fetch twin num(if exists)
        result = re.search(r"(\d+)\s*Twins.*?", divs[4].text)
        meta.twin_num = int(result.group(1)) if result is not None else 0

        # fetch parameters
        parameters = []
        div = soup.find(id='parameters')
        if div.table.tr.td.text == 'None':
            meta.parameters = ''
        else:
            for entry in div.table.find_all('tr'):
                parameters.append(
                    [element.text for element in entry.find_all('td')]
                )
            meta.parameters = parameters

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
        meta.document = article
        meta.last_fetched = timezone.now()
        meta.save(fill_shared_fields=True)

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

        meta, _ = BiobrickMeta.objects.get_or_create(part_name=brick_name)

        raw_response = safe_fetch(
            ExperienceSpider.base_site + 'Part:' + brick_name + ':Experience',
            'experiences of {}'.format(brick_name)
        )

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
                experience, _ = meta.experiences.get_or_create(
                    author_name=author_name,
                    defaults={'title': '', 'brick': meta}
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
                    experience, _ = meta.experiences.get_or_create(
                        author_name=author_name,
                        defaults={'title': '', 'brick': meta}
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
