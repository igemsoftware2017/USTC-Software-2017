from rest_framework.test import APITestCase


class Test(APITestCase):

    def test_analyzer(self):

        from biohub.biomap.analyzer import Analyzer

        a = Analyzer()
        result = a.analyze('BBa_I3521')  # noqa

    def test_reverse(self):

        from biohub.biomap.analyzer import Analyzer

        a = Analyzer()
        result = a.analyze_reverse('BBa_B0034')  # noqa
