from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from views import *
from utils import *
from models import Pledge

from datetime import datetime, timedelta, date

# from publicweb.app import Model

class BaseTestCase(TestCase):
    fixtures = ['publicweb_test_fixture.json', 'auth.json', 'hatresults50.json']
    # ['auth.json', 'hathouseidlookup50.json', 'hatresults50.json', 'lsoadomestic50.json', 'postcodeoalookup50.json', 'ecoeligible50.json', 'publicweb_test_fixture.json']

    def setUp(self):
        # users
        self.phil = User.objects.get(username="phil")
        self.test99 = User.objects.get(username="test99")

        #client 
        self.c = Client()
        self.c.login(username='test99', password='test99')

        # measures
        self.loft_insulation = Measure.objects.get(id=1)
        self.solar_panel_1kw = Measure.objects.get(id=13)
        self.cylinder_thermostat = Measure.objects.get(id=21)

        # times
        self.datetime_one_week_today = datetime.now() + timedelta(days=7)
        self.datetime_one_week_ago = datetime.now() + timedelta(days=-7)

        self.date_one_week_today = (datetime.now() + timedelta(days=7)).date()
        self.date_ten_days_time = (datetime.now() + timedelta(days=10)).date()

        # pledges
        self.pledge_1 = Pledge(id=1, measure=self.loft_insulation, user=self.phil, deadline=self.date_one_week_today)
        self.pledge_1.save()
        self.pledge_2 = Pledge(id=2, measure=self.solar_panel_1kw, user=self.phil, deadline=self.date_ten_days_time)
        self.pledge_3 = Pledge(id=3, measure=self.loft_insulation, user=self.test99, deadline=self.date_ten_days_time)
        self.pledge_3.save()
        self.pledges = [self.pledge_1, self.pledge_2, self.pledge_3]

        # HAT Results
        self.hat_results_1 = HatResultsDatabase.objects.get(pk=1)
        # HAT Results 1 values:
        #  {"pk": 1, "model": "publicweb.hatresultsdatabase", 
        # "fields": {"post_measure_energy_costs": "3097.33", 
        # "index": 100001, "consumption_change": 12208,
        #  "current_sap_rating": 34.74, "sap_change": 12.26, 
        #  "post_measure_energy_consumption_kwh": 45201.92, 
        #  "post_measure_sap_rating": 47.0, "annual_co2_reduction": 1775.67,
        #   "grean_deal": true, "post_measure_co2_emissions_kgco2": 12776.3, 
        #   "current_co2_emissions_kgco2": 14551.97, 
        #   "current_energy_consumption_kwh": 57409.97, "m1": 1, 
        #   "current_energy_costs": "3485.65", "eco_finance": false, 
        #   "approximate_installation_costs": "489.27",
        #  "house_id": 1, "annual_cost_reduction": "388.32"}},

class PublicwebIntegrationTests(BaseTestCase):

    
    def test_dwelling_form(self):
        resp = self.c.post('/accounts/myhome/')
        # print resp
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], 'http://testserver/accounts/profile/')
        # form_content = {
        #     'window_type':1,
        #     'dwelling_type':2,
        #     'property_age':10,
        #     'number_of_bedrooms':14,
        #     'heating_fuel':17,
        #     'heating_type':21,
        #     'loft_insulation':27,
        #     'wall_type': 30,
        # }
        resp = self.c.post(reverse('dwelling_form'), {'postcode':"AAAAAA"})
        # print resp
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "<p class=\"text-warning\">Please enter a valid postcode.</p>")
        resp = self.c.post(reverse('dwelling_form'), {'approximate_spent_on_electricity_per_month':"aaa"})
        self.assertContains(resp, "<p class=\"text-warning\">Enter a whole number.</p>")

    def test_pledge_appears_on_profile(self):
        resp = self.c.get(reverse('profile'))
        # print resp
        self.assertContains(resp, "Loft Insulation Topup by May 10, 2014  <span class=\"text-success\">( unknown  kWh)")

    def test_cannot_modify_other_pledges(self):
        resp = self.c.get('/pledges/edit/1/')
        self.assertEqual(resp.status_code, 302)
        resp = self.c.get('/pledges/delete/1/')
        self.assertEqual(resp.status_code, 302)
        resp = self.c.get('/pledges/complete/1/')
        self.assertEqual(resp.status_code, 302)


class PublicwebHelperFunctions(BaseTestCase):
    """Test functions in utils.py"""

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
        # randomly selected entry from hatresults fixture
        houseid = 1
        measureid = 19
        results = get_hat_results(houseid, measureid)
        self.assertIsNotNone(results)
        results = get_hat_results(houseid, None)
        self.assertIsNone(results)

    # def test_get_house_id(self):
    #     # test99's dwelling housid: 11995
    #     dwelling = self.test99.userprofile.dwelling
    #     print dwelling.pk
    #     result = get_house_id(dwelling)
    #     print result

    def test_get_dwelling(self):
        result = get_dwelling(self.test99)
        self.assertEqual(result.pk, 10)
        result = get_dwelling(None)
        self.assertEqual(result, None)

    def test_get_payback_time(self):
        result = get_payback_time(self.hat_results_1)
        self.assertEqual(result, 1.3)
        result = get_payback_time(None)
        self.assertIsNone(result)

    def test_get_percentage_return_on_investment(self):
        result = get_percentage_return_on_investment(self.hat_results_1)
        self.assertEqual(result, 79.4)
        result = get_payback_time(None)
        self.assertIsNone(None)

class PublicwebViewsTestCase(BaseTestCase):
    """Tests to ensure all pages of the site are working"""

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

   