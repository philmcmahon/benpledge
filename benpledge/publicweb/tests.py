from django.test import TestCase
from django.test.client import Client
from views import *
from utils import *
from models import Pledge

from datetime import datetime, timedelta, date

# from publicweb.app import Model

class BaseTestCase(TestCase):
    fixtures = ['publicweb_test_fixture.json', 'auth.json']
    # ['auth.json', 'hathouseidlookup50.json', 'hatresults50.json', 'lsoadomestic50.json', 'postcodeoalookup50.json', 'ecoeligible50.json', 'publicweb_test_fixture.json']



    def setUp(self):
        # users
        self.phil = User.objects.get(username="phil")
        self.test99 = User.objects.get(username="test99")


        # measures
        self.loft_insulation = Measure.objects.get(id=1)
        self.solar_panel_1kw = Measure.objects.get(id=13)

        # times
        self.datetime_one_week_today = datetime.now() + timedelta(days=7)
        self.datetime_one_week_ago = datetime.now() + timedelta(days=-7)

        self.date_one_week_today = (datetime.now() + timedelta(days=7)).date()
        self.date_ten_days_time = (datetime.now() + timedelta(days=10)).date()

        # pledges
        self.pledge_1 = Pledge(id=1, measure=self.loft_insulation, user=self.phil, deadline=self.date_one_week_today)
        self.pledge_2 = Pledge(id=2, measure=self.solar_panel_1kw, user=self.phil, deadline=self.date_ten_days_time)
        self.pledge_3 = Pledge(id=3, measure=self.loft_insulation, user=self.test99, deadline=self.date_ten_days_time)
        self.pledges = [self.pledge_1, self.pledge_2, self.pledge_3]




class PublicwebHelperFunctions(BaseTestCase):

    def method_tester(self, method, test_input, expected_output):
        self.assertEqual(method(test_input), expected_output)

    def test_get_map_initial(self):
        map_initial = get_map_initial(23.4567, 54.8944, 12)
        self.assertEqual(map_initial['latitude'], '23.4567')
        self.assertEqual(map_initial['zoom'], 12)
        map_initial = get_map_initial(None, None, None)
        self.assertEqual(map_initial['longitude'], 'None')
        self.assertEqual(map_initial['zoom'], None)

    def test_get_time_remaining(self):
        self.method_tester(get_time_remaining, self.datetime_one_week_today, "0 months, 6 days")
        self.method_tester(get_time_remaining, self.datetime_one_week_ago, "Deadline has been passed.")

    def test_space_postcode(self):
        self.method_tester(space_postcode, "BS81BU", "BS8  1BU")
        self.method_tester(space_postcode, "PL210AJ", "PL21 0AJ")
        self.method_tester(space_postcode, "BS8  2DJ", "BS8  2DJ")

    def test_convert_name_to_identifier(self):
        self.method_tester(convert_name_to_identifier, "Enormous Pieces of Cutlery", "enormous_pieces_of_cutlery")
        self.method_tester(convert_name_to_identifier, "1234,,asda ,%&*,, ___", "asda_____")
    
    def test_geocode_address(self):
        location = geocode_address("Alma Road, Bristol")
        self.assertEqual(location['lat'], 51.462289)
        location = geocode_address("Small street, BS1")
        self.assertEqual(location['lng'], -2.5949489)

    def test_get_pledges_with_positions(self):
        pledges_with_positions = get_pledges_with_positions(self.pledges)
        self.assertEqual(pledges_with_positions[str(self.pledge_1.id)]['position']['lat'], 51.4622043)
        self.assertEqual(pledges_with_positions[str(self.pledge_3.id)]['pledge']['deadline'], str(self.date_ten_days_time))

    def test_get_hat_results(self):
        houseid = self.phil.userprofile.dwelling.house_id
        measureid = self.loft_insulation.id
        results = get_hat_results(houseid, measureid)
        self.assertIsNotNone(results)
        results = get_hat_results(houseid, None)
        self.assertIsNone(results)



        


class PublicwebViewsTestCase(BaseTestCase):

    # def login_normal(self):
    #     if not self.client.login(username='testnormal', password='testnormal'):
    #         print "Error - login_normal failed."

    def response_test(self, url, expected_status_code, client=None):
        if not client:
            client = self.client
        resp = client.get(url)
        self.assertEqual(resp.status_code, expected_status_code)

    def test_pages_not_requiring_authentication_have_expected_status(self):
        self.response_test('/', 200)
        self.response_test('/getstarted/', 200)
        self.response_test('/help/', 200)
        self.response_test('/all_measures/', 200)
        self.response_test('/measures/1/', 200)
        self.response_test('/pledges/all/', 200)
        self.response_test('/areas/', 200)
        self.response_test('/areas/BS8/', 200)
        self.response_test('/accounts/profile/', 302)
        self.response_test('/about/', 200)
        self.response_test('/accounts/login/', 200)
        self.response_test('/accounts/password_reset/', 200)

    def test_pages_requiring_authentication_have_expected_status(self):
        c = Client()
        c.login(username='test99', password='test99')
        self.response_test('/accounts/profile/', 200, c)
        self.response_test('/pledges/my_pledges/', 200, c)
        self.response_test('/accounts/myhome/', 200, c)
        self.response_test('/users/test99/', 200, c)
        # self.response_test('/pledge_overview/', 302)

    # def test_index(self):
    #     resp = self.client.get('/')
    #     self.assertEqual(resp.status_code, 200)

    # def test_getstarted_returns_200(self):
    #     resp = self.client.get('/getstarted/')
    #     self.assertEqual(resp.status_code, 200)

    # def test_help_returns_200(self):
    #     resp = self.client.get('/help/')
    #     self.assertEqual(resp.status_code, 200)

    # def test_measures_returns_200(self):
    #     resp = self.client.get('/all_measures/')
    #     self.assertEqual(resp.status_code, 200)
    #     resp = self.client.get('/measures/1/')
    #     self.assertEqual(resp.status_code, 200)

    # def test_all_pledges_returns_200(self):
    #     resp = self.client.get('/pledges/all/')
    #     self.assertEqual(resp.status_code, 200)

    # def test_pledges_by_area_returns_200(self):
    #     resp = self.client.get('/areas/')
    #     self.assertEqual(resp.status_code, 200)
    #     resp = self.client.get('/areas/BS8/')
    #     self.assertEqual(resp.status_code, 200)

    # def test_profile_redirects_when_not_authenticated(self):
    #     resp = self.client.get('/accounts/profile/')
    #     self.assertEqual(resp.status_code, 302)
    #     # self.assertRedirects(resp, '/accounts/login/', status_code=302, target_status_code=200)

    # def test_about_returns_200(self):
    #     resp = self.client.get('/about/')
    #     self.assertEqual(resp.status_code, 200)

    # def test_authentication_returns_200(self):
    #     resp = self.client.get('/accounts/login/')
    #     self.assertEqual(resp.status_code, 200)
    #     resp = self.client.get('/accounts/password_reset/')
    #     self.assertEqual(resp.status_code, 200)





    # def test_profile_200_when_authenticated(self):
    #     c = Client()
    #     c.login(username='testnormal', password='testnormal')
    #     resp = c.get('/accounts/profile/')
    #     self.assertEqual(resp.status_code, 200)
        # self.login_normal()
        # resp = self.client.get('/accounts/profile')
        # self.assertEqual(resp.status_code, 200)