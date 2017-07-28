import requests
import re
from models import Brick
class BrickSpider():

    base_site = 'http://parts.igem.org/'
    def fill_from_page(self,brick=Brick(),brick_name):
        ''' 
        Brick: class from models.Model
        brick_name: like 'K314110'
         '''
        # final URL: http://parts.igem.org/Part:BBa_K314110
        raw_response = requests.get(BrickSpider.base_site+'Part:BBa_'+brick_name)
        raw_data = raw_response.text
        # fill name
        brick.name = brick_name
        # fetch Designer
        try:
            brick.designer=re.search('Designed by:\s*(.*?)\s*&nbsp',raw_data).group(1)
            brick.group_name = re.search('Group:\s*(.*?)\s*&nbsp',raw_data).group(1)
            brick.part_type = re.search('<div style=\'.*?\'\s*title=\'Part Type\'>\s*(.*?)</div>',raw_data).group(1)
            brick.nickname = re.search('<div style=\'.*?\'\s*type=\'Nickname\'>\s*(.*?)</div>',raw_data).group(1)
            raw_bioinfo = re.search('<script>\s*(var\s*sequence.*?)\s*</script>',raw_data).group(1)
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
            dna_position = 
        except Exception:
            print('Error during parsing contents\n')
        finally:
            brick.save()
        

        # fetch raw bioinfo
        
        
        brick.sequence_a = 


