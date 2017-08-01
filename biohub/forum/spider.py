import requests, re, json
from bs4 import BeautifulSoup
from models import Brick, SeqFeature
from biohub.utils.htm2text import html2text
class BrickSpider():

    base_site = 'http://parts.igem.org/'
    # @staticmethod
    # def content_div(tag):
    #     return (tag.name=='div' and tag.id=='mw-content-text')
    def fill_from_page(self,brick=Brick(),brick_name):
        ''' 
        Brick: class from models.Model
        brick_name: like 'K314110'
         '''
        # final URL example: http://parts.igem.org/Part:BBa_K314110
        raw_response = requests.get(BrickSpider.base_site+'Part:BBa_'+brick_name)
        raw_html = raw_response.text
        # fill name
        brick.name = brick_name
        # fetch Designer
        try:
            brick.designer=re.search('Designed by:\s*(.*?)\s*&nbsp',raw_html).group(1)
            brick.group_name = re.search('Group:\s*(.*?)\s*&nbsp',raw_html).group(1)
            brick.part_type = re.search('<div style=\'.*?\'\s*title=\'Part Type\'>\s*(.*?)</div>',raw_html).group(1)
            brick.nickname = re.search('<div style=\'.*?\'\s*type=\'Nickname\'>\s*(.*?)</div>',raw_html).group(1)
            raw_bioinfo = re.search('<script>\s*(var\s*sequence.*?)\s*</script>',raw_html).group(1)
            brick.sequence_a = re.search('String\(\'(.*?)\'\)',raw_bioinfo).group(1)
            sequence_b=''
            for char in list(brick.sequence_a):
                if(char=='a'):
                    sequence_b+='t'
                if(char=='t'):
                    sequence_b+='a'
                if(char=='c'):
                    sequence_b+='g'
                if(char=='g'):
                    sequence_b+='c'
            brick.sequence_b=sequence_b
            dna_position = re.search('new Array\(.*?\'dna\',(\d+,\d+).*?\)',raw_bioinfo).group(1)
            #add char field with the suitable validator eg: "23,435" done!
            seqFeature_data = re.search('seqFeatures.*?new Array\s*\((.+?)\)',raw_bioinfo).group(1)
            seqFeatureList = re.findall('\[\'(.*?)\'\s*,\s*(\d*)\s*,\s*(\d*)\s*,\s*\'(.*?)\'',seqFeature_data)
            for each in seqFeatureList:
                obj = SeqFeature(feature_type=each[0],start_loc=int(each[1]),end_loc=int(each[2]),name=each[3])
                brick.seqFeatures.add(obj)
            sub_parts_data = re.search('subParts.*?new Array\s*\((.+?)\)',raw_bioinfo) and re.search('subParts.*?new Array\s*\((.+?)\)',raw_bioinfo).group(1)
            if(sub_parts_data):
                sub_parts_list = re.findall('Part\(\d*,\s*\'(.*?)\'.*?\)',sub_parts_data)
                brick.sub_parts = ','.join(sub_parts_list)
            else:
                brick.sub_parts = None # for stand-alone bricks
            soup = BeautifulSoup(raw_html,"lxml")
            # fetch parameters
            parameters = []
            div = soup.find(id='parameters')
            for entry in div.table.find_all('tr'):
                parameters.append([element.text for element in entry.find_all('td')])
            brick.parameters=json.dumps(parameters)
            # fetch categories
            div = soup.find(id='categories')
            categories = re.search('(//.*?)\s*\Z',div.text,re.DOTALL).group(1)
            brick.categories=categories

            # remove scripts, panel, and compatibility infos
            scriptset=soup.find_all(name='script')
            for each in scriptset:
                each.extract()
            html_document = soup.find('div',id='mw-content-text')
            if(panel=soup.find(id='sequencePaneDiv')):
                panel.extract()
            if(compat = soup.find(class_='compatibility_div')):
                compat.parent.extract()
            # restore images by supplementing URLs
            newdoc = re.sub('=\"/(.*?\")','=\"'+base_site+r'\1',soup.prettify())
            soup2=BeautifulSoup(newdoc,"lxml")
        except Exception:
            print('Error during parsing contents\n')
        finally:
            brick.save()
        

        # fetch raw bioinfo

brick = Brick()
brick_name = 'I763007'
