from rest_framework.test import APIClient, APITestCase
from django.test import TestCase
from biohub.accounts.models import User
from biohub.forum.models import Brick, Article
import json


class BrickFetchTest(TestCase):
    def test_fetch_from_iGEM(self):
        self.client
        c= APIClient()
        # I just examine the behaviours in debug mode
        response = c.get('/api/forum/bricks/fetch/?name=B0015')
        # test if the data will be fetched from local
        response = c.get('/api/forum/bricks/fetch/?name=B0015')
        # test an entry that doesn't exist
        response = c.get('/api/forum/bricks/fetch/?name=E0025')