from django.test import TestCase
# from publicweb.app import Model

class PublicwebViewsTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)

    
