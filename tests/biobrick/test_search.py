from ._base import BiobrickTest


class Test(BiobrickTest):

    def test_keyword(self):

        res = self.client.get(self.base_url + '?q=Bio')
        self.assertEqual(res.status_code, 200)

        for item in res.data['results']:
            self.assertIn('bio', item['short_desc'].lower())

    def test_name(self):

        res = self.client.get(self.base_url + '?q=n:0000')
        self.assertEqual(res.status_code, 200)

        for item in res.data['results']:
            self.assertIn('0000', item['part_name'])

    def test_type(self):

        res = self.client.get(self.base_url + '?q=t:termin')
        self.assertEqual(res.status_code, 200)

        for item in res.data['results']:
            self.assertIn('termin', item['part_type'].lower())
