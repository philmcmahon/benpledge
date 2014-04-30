import re, urllib, urllib2, json
from datetime import datetime

from django.db.models import Count

from models import (Pledge, Measure, Dwelling, HouseIdLookup,
    HatResultsDatabase, PostcodeOaLookup, LsoaDomesticEnergyConsumption,
    EcoEligible, UserProfile, Area)

from benpledge_keys import GOOGLE_API_KEY

##### helper functions #####
def get_measures_with_identifiers():
    """ Returns dict of measure ids with name converted from Loft Insulation to loft_insulation"""
    measures = Measure.objects.all()
    measure_ids = {}
    for m in measures:
        measure_ids[convert_name_to_identifier(m.name)] = m.id
    return measure_ids

def pledge_results_with_progress(pledges):
    """Takes a list of pledges and returns a dict containing progress details"""
    pledge_progress = {}
    for p in pledges:
        if p.pledge_type == Pledge.PLEDGE:
            time_progress = Pledge.time_progress(p)
        else:
            time_progress = None
        pledge_progress[p.id] = {
            'pledge' : p,
            'time_progress': time_progress,
            'savings': get_pledge_energy_savings(p),
        }
    return pledge_progress

def get_dwelling_hat_results(dwelling):
    """ Returns dictionary of suitable measures for dwelling. """
    if not dwelling.house_id:
        return None
    measures = Measure.objects.all()
    hat_results = {}
    for m in measures:
        if m.hat_measure:
            hat_out = get_hat_results(dwelling.house_id, m.hat_measure.measure_id)
            if suitable_measure(hat_out, m, dwelling.window_type):
                hat_results[m.id] = {
                    'hat_results' : hat_out,
                    'measure_name' : m.name,
                    'payback_time_estimate': get_payback_time(hat_out),
                    'percentage_return_on_investment': get_percentage_return_on_investment(hat_out)
                }
    return hat_results

def suitable_measure(hat_out, measure, window_type):
    """ Returns False if negative energy savings or measure otherwise unsuitable"""
    if not hat_out or hat_out.consumption_change <= 0 or hat_out.annual_cost_reduction <= 0:
        return False
    if window_type == Dwelling.DOUBLE_GLAZING and measure.name in ["Secondary glazing", "Double Glazing"]:
        return False
    # False if payback time greater than 50 years
    if get_payback_time(hat_out) > 50:
        return False
    return True

def get_payback_time(hat_info):
    if hat_info:
        return round((hat_info.approximate_installation_costs /
            hat_info.annual_cost_reduction), 1)
    else:
        return None

def get_percentage_return_on_investment(hat_info):
    if hat_info:
        return round((hat_info.annual_cost_reduction * 100 /
            hat_info.approximate_installation_costs), 1) 
    else:
        return None    

def get_house_id(dwelling):
    """ Takes the HAT details of a dwelling and converts them into a houseid"""
    metadata_properties = ([dwelling.dwelling_type, dwelling.property_age,
        dwelling.number_of_bedrooms, dwelling.heating_fuel,
        dwelling.heating_type, dwelling.loft_insulation, dwelling.wall_type])
    combined_info = ''
    for field in metadata_properties:
        if not field:
            return 0
        else:
            combined_info += str(field.value)
    house_id_lookup_row = HouseIdLookup.objects.filter(index_id=combined_info).first()
    if house_id_lookup_row:
        return house_id_lookup_row.house_id
    else:
        return None

def get_hat_results(houseid, measureid):
    if not houseid or not measureid:
        return None
    hat_index = str(houseid) + "0000" + str(measureid)
    result = HatResultsDatabase.objects.filter(index=hat_index).first()
    return result

def get_dwelling(user):
    up = UserProfile.objects.filter(user=user).first()
    if up:
        return up.dwelling
    else:
        return None

def convert_name_to_identifier(name):
    """ Converts name into a valid identifier"""
    name = name.lower()
    # remove whitespace
    name = name.replace(' ', '_')
    # remove invalid characters
    name = re.sub('[^0-9a-zA-Z_]', '', name)
    # remove leading numbers
    # regex from http://stackoverflow.com/questions/3303312/how-do-i-convert-a-string-to-a-valid-variable-name-in-python
    name = re.sub('^[^a-zA-Z_]+', '', name)
    return name

def get_consumption_row_for_postcode(postcode):
    """ Gets energy consumption information for postcode"""
    postcode_lookup = PostcodeOaLookup.objects.filter(postcode=postcode).first()
    if postcode_lookup:
        consumption_lookup = LsoaDomesticEnergyConsumption.objects.filter(lsoa_code=postcode_lookup.lsoa_code).first()
        return consumption_lookup
    else:
        return None

def get_eco_eligible(postcode):
    """Returns true if postcode is eligible for ECO funding"""
    postcode_lookup = PostcodeOaLookup.objects.filter(postcode=space_postcode(postcode)).first()
    if postcode_lookup:
        eco_eligible = EcoEligible.objects.filter(lsoa_code=postcode_lookup.lsoa_code).first()
        if eco_eligible:
            return True
        else:
            return False
    else:
        return 'unknown'

def space_postcode(non_spaced_postcode_postcode):
    """Adds  correct spacing to separate outward, inward sections of postcode"""
    spaced_postcode = ""
    if len(non_spaced_postcode_postcode) > 4:
        for i, c in enumerate(non_spaced_postcode_postcode[::-1]):
            if i == 3:
                if len(non_spaced_postcode_postcode) == 6:
                    spaced_postcode += "  "
                elif len(non_spaced_postcode_postcode) == 7:
                    spaced_postcode += " "
            spaced_postcode += c
    return spaced_postcode[::-1]

# def get_total_reduction_pledges(pledges_with_progress):
#     """Returns the total carbon savings of all pledges in pledges_with_progress"""
#     total_reduction = 0
#     for k, p in pledges_with_progress.iteritems():
#         if p['pledge'].pledge_type == Pledge.PLEDGE:
#             pledge_energy_savings = get_pledge_energy_savings(p['pledge'])
#             if pledge_energy_savings:
#                 total_reduction += pledge_energy_savings
#     return total_reduction

def get_total_reduction(pledges):
    total_reduction = 0
    for p in pledges:
        pledge_energy_savings = get_pledge_energy_savings(p)
        if pledge_energy_savings:
            total_reduction += pledge_energy_savings
    return total_reduction


def get_time_remaining(deadline):
    """ Gives the time in months and days until deadline"""
    if deadline:
        if datetime.combine(deadline, datetime.min.time()) < datetime.now():
            return "Deadline has been passed."
        time_remaining = datetime.combine(deadline, datetime.min.time()) - datetime.now()
        time_remaining = time_remaining.days
        days_remaining = time_remaining % 30
        months_remaining = time_remaining/30
        time_remaining = str(months_remaining) + " months, " + str(days_remaining) + " days" 
        return time_remaining
    else:
        return None


def get_pledge_energy_savings(pledge):
    if pledge.hat_results:
        return pledge.hat_results.consumption_change
    elif pledge.measure.estimated_annual_energy_savings_kwh:
        return pledge.measure.estimated_annual_energy_savings_kwh
    else:
        return None

def get_pledge_financial_savings(pledge):
    if pledge.hat_results:
        return pledge.hat_results.post_measure_energy_costs
    else:
        return None

def get_map_initial(latitude, longitude, zoom=13):
    return dict(latitude=str(latitude), longitude=str(longitude), zoom=zoom)

def get_pledges_with_positions(pledges):
    pledges_with_positions = {}
    for p in pledges:
        if p.user.userprofile.dwelling and p.user.userprofile.dwelling.position.latitude != 0:
            position = p.user.userprofile.dwelling.position
            pledge_energy_savings = get_pledge_energy_savings(p)
            if pledge_energy_savings:
                savings = str(pledge_energy_savings)
            else:
                savings = 'unknown'

            pledge_money_savings = get_pledge_financial_savings(p)
            if pledge_money_savings:
                money_savings = str(pledge_money_savings)
            else:
                money_savings = 'unknown'
            pledges_with_positions[str(p.id)] = ({
                'pledge': {
                    'measure': str(p.measure),
                    'user':str(p.user),
                    'date_made':str(p.date_made.date()),
                    'deadline':str(p.deadline),
                    'time_remaining':get_time_remaining(p.deadline),
                    'savings': savings,
                    'complete': str(p.complete),
                    },
                'position': {
                    'lat': float(position.latitude),
                    'lng': float(position.longitude)
                    }
            })
    return pledges_with_positions


def get_areas_with_total_pledges():
    return Area.objects.annotate(pledge_count=Count('dwelling__userprofile__user__pledge')).order_by('-pledge_count')


def get_area_ranking(area, areas_with_total_pledges):
    for i, a in enumerate(areas_with_total_pledges, start=1):
        if a == area:
            return i
    return None

def get_ranking_details(area, total_pledges):
    area_pledge_counts = get_areas_with_total_pledges()
    area_ranking = get_area_ranking(area, area_pledge_counts)
    if area_ranking > 1:
        area_above = area_pledge_counts[area_ranking-2]
        pledge_difference_with_area_above = area_above.pledge_count - total_pledges
        if pledge_difference_with_area_above == 0:
            pledge_difference_with_area_above = 1
        top = False
    else:
        area_above = None
        pledge_difference_with_area_above = None
        top = True
    if area_ranking  < len(area_pledge_counts):
        area_below = area_pledge_counts[area_ranking]
        pledge_difference_with_area_below = total_pledges - area_below.pledge_count
        if pledge_difference_with_area_below == 0:
            pledge_difference_with_area_below = 1
        bottom = False
    else:
        area_below = None
        pledge_difference_with_area_below = None
        bottom = True
    ranking_details = {
        'area_pledge_counts':area_pledge_counts,
        'area_ranking':area_ranking,
        'area_above':area_above,
        'pledge_difference_with_area_above':pledge_difference_with_area_above,
        'area_below':area_below,
        'pledge_difference_with_area_below':pledge_difference_with_area_below,
        'top': top,
        'bottom': bottom,
    }
    return ranking_details

def geocode_address(address):
    url = "https://maps.googleapis.com/maps/api/geocode/json?address=%s,UK&sensor=false&key=%s" % (urllib.quote_plus(address), GOOGLE_API_KEY)
    # print url
    response = urllib.urlopen(url).read()
    # print response
    response_dict = json.loads(response)
    return response_dict['results'][0]['geometry']['location']

def get_address_from_street_name_or_area(street_name, area):
    if street_name:
        if area:
            address_string = street_name + ', ' + area.postcode_district
        else:
            address_string = street_name + ', Bristol'
    else:
        address_string = area.postcode_district
    return address_string