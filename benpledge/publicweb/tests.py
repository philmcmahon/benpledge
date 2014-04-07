from django.test import TestCase
from django.test.client import Client

# from publicweb.app import Model
 # 'hathouseidlookup50.json',
 #        'hatresults50.json', 'lsoadomestic50.json',
 #         'postcodeoalookup50.json', 'ecoeligible50.json',
class PublicwebViewsTestCase(TestCase):
    fixtures = ['auth.json', 'publicweb_test_fixture.json']

    def get_admin_client():
        c = Client()
        c.login(username='testadmin', password='testadmin')
        return c

    def login_normal(self):
        if not self.client.login(username='testnormal', password='testnormal'):
            print "Error - login_normal failed."


    def test_index(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)

    def test_getstarted_returns_200(self):
        resp = self.client.get('/getstarted/')
        self.assertEqual(resp.status_code, 200)

    def test_help_returns_200(self):
        resp = self.client.get('/help/')
        self.assertEqual(resp.status_code, 200)

    def test_measures_returns_200(self):
        resp = self.client.get('/measures/')
        self.assertEqual(resp.status_code, 200)

    def test_all_pledges_returns_200(self):
        resp = self.client.get('/pledges/all/')
        self.assertEqual(resp.status_code, 200)

    def test_pledges_by_area_returns_200(self):
        resp = self.client.get('/areas/')
        self.assertEqual(resp.status_code, 200)

    def test_profile_redirects_when_not_authenticated(self):
        resp = self.client.get('/accounts/profile/')
        self.assertEqual(resp.status_code, 302)
        # self.assertRedirects(resp, '/accounts/login/', status_code=302, target_status_code=200)

    # def test_profile_200_when_authenticated(self):
    #     c = Client()
    #     c.login(username='testnormal', password='testnormal')
    #     resp = c.get('/accounts/profile/')
    #     self.assertEqual(resp.status_code, 200)
        # self.login_normal()
        # resp = self.client.get('/accounts/profile')
        # self.assertEqual(resp.status_code, 200)