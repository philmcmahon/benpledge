from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.views.generic.base import View
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count

import re, urllib, urllib2, json
from datetime import datetime, timedelta, date
from collections import defaultdict

from registration.backends.simple.views import RegistrationView
from models import (Measure, Dwelling, UserProfile, HatMetaData,
    HouseIdLookup, HatResultsDatabase, Pledge, Area, PostcodeOaLookup,
    LsoaDomesticEnergyConsumption, TopTip, Organisation, HomepageCheckList, EcoEligible,
    AboutPage, FundingOption, Provider)
from forms import DwellingForm, PledgeForm, PledgeCompleteForm

from postcode_parser import parse_uk_postcode

from benpledge_keys import GOOGLE_API_KEY

# class RegistrationView(RegistrationView):
#     def get_success_url(request, user):
#         return 'profile'

def access_denied(request):
    context = {
        'error_heading': "Access Denied",
        'error_message': "Sorry, you do not have permission to access this page.",
    }

    return render(request, 'publicweb/error_page.html', context)

def index(request):
    """Homepage"""
    checklist = HomepageCheckList.objects.all().order_by('order')
    context = {
        'checklist': checklist,
    }
    return render(request, 'publicweb/index.html', context)

def get_started(request):
    top_tips = TopTip.objects.filter(display_on_welcome_screen=True)
    context = {
        'top_tips': top_tips,
    }
    return render(request, 'publicweb/options.html', context)

def general_measures(request):
    mid_id = int(Measure.objects.latest('id').id)/2
    measures1 = Measure.objects.filter(id__lte=mid_id)
    measures2 = Measure.objects.filter(id__gt=mid_id)

    funding_options = FundingOption.objects.all()
    context = {
        'measure_ids': get_measures_with_identifiers(),
        'measures1': measures1,
        'measures2': measures2,
        'funding_options': funding_options,
    }
    return render(request, 'publicweb/general_measures.html', context)

def help_page(request):
    organisations = Organisation.objects.all().order_by('organisation_type', 'name')
    context = {
        'organisations': organisations,
    }
    return render(request, 'publicweb/help_page.html', context)

@staff_member_required
def pledge_admin_overview(request):
    pledges = Pledge.objects.all().order_by('user')
    context = {
        'pledges': pledges
    }
    return render(request, 'publicweb/pledge_admin_overview.html', context)

@staff_member_required
def user_admin_overview(request):
    users = User.objects.all()
    context = {
        'users': users
    }
    return render(request, 'publicweb/user_admin_overview.html', context)

@login_required
def profile(request, username=None):
    measure_ids = get_measures_with_identifiers()

    userprofile = UserProfile.objects.filter(user=request.user).first()

    # if the user object has no dwelling, redirect to dwelling form
    if not userprofile.dwelling:
        return redirect('dwelling_form')

    # if the dwelling has a house id, fetch the HAT results for it
    if userprofile.dwelling and userprofile.dwelling.house_id:
        user_measures = get_dwelling_hat_results(userprofile.dwelling)
    else:
        user_measures = None

    # fetch context data required for pledges list
    pledges = Pledge.objects.filter(user=request.user)
    pledge_progress = pledge_results_with_progress(pledges)
    total_reduction = get_total_reduction(pledges)
    total_completed_reduction = get_total_reduction(pledges.filter(complete=True))
    
    # if a postcode has been supplied, check to see if it's ECO eligible
    if userprofile.dwelling.postcode:
        eco_eligible =  get_eco_eligible(userprofile.dwelling.postcode)
    else:
        eco_eligible = 'postcode_unknown'

    context = {
        'measure_ids': measure_ids, 
        'user_measures': user_measures,
        'pledge_progress' : pledge_progress,
        'page_type': 'profile',
        'total_reduction': total_reduction,
        'total_completed_reduction':total_completed_reduction,
        'eco_eligible': eco_eligible,
        'dwelling': userprofile.dwelling,
    }
    return render(request, 'publicweb/base_profile.html', context) 


def measure(request, measure_id):
    m = Measure.objects.get(id=measure_id)
    hat_info = None
    payback_time_estimate = None
    if m.hat_measure and request.user.is_authenticated():
        dwelling = get_dwelling(request.user)
        if dwelling.house_id:
            hat_info = get_hat_results(dwelling.house_id,
                m.hat_measure.measure_id)
    if hat_info:
        payback_time_estimate = get_payback_time(hat_info)

    # pledge = Pledge.objects.get(user=request.user, measure=m)

    providers = Provider.objects.filter(measures=m, display_on_measure_pages=True).order_by('order')[:3]
    pledge = None
    time_remaining = None
    if request.user.is_authenticated():
        try:
            pledge = Pledge.objects.get(user=request.user, measure=m)
        except ObjectDoesNotExist:
            pledge = None
        time_remaining = None
        if pledge and pledge.pledge_type == Pledge.PLEDGE:
            time_remaining = get_time_remaining(pledge.deadline)

    context = {
        'measure': m,
        'hat_info': hat_info,
        'payback_time_estimate' : payback_time_estimate,
        'pledge' : pledge,
        'time_remaining': time_remaining,
        'providers':providers,
    }
    return render(request, 'publicweb/measure.html', context)

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


@login_required
def dwelling_form(request):
    dwelling = get_dwelling(request.user)
    current_user_profile = UserProfile.objects.get(user=request.user)

    if dwelling:
        current_street_name = dwelling.street_name
        current_area = dwelling.area
    else:
        current_street_name = None
        current_area = None
    
    if request.method == 'POST':
        form = DwellingForm(request.POST, instance=dwelling)
        if form.is_valid():
            updated_dwelling = form.save(commit=False)
            # check if street name/area has changed, if so update position
            if updated_dwelling.street_name or updated_dwelling.area:
                if (updated_dwelling.street_name or updated_dwelling.area and not dwelling or
                    updated_dwelling.street_name != current_street_name or updated_dwelling.area != current_area):
                    address_string = get_address_from_street_name_or_area(updated_dwelling.street_name,
                        updated_dwelling.area)

                    location = geocode_address(address_string)
                    updated_dwelling.position.latitude = location['lat']
                    updated_dwelling.position.longitude = location['lng']

            # check if the settings the user has provided have a match in the HAT
            # if so update the house id
            updated_house_id = get_house_id(updated_dwelling)
            if updated_house_id:
                updated_dwelling.house_id = updated_house_id
            # updated_dwelling.postcode = form.cleaned_data
            updated_dwelling.save()

            if dwelling == None:
                print "updating dwelling"
                current_user_profile.dwelling = updated_dwelling
                current_user_profile.save()
            return redirect('profile')
        else:
            # print form.errors
            return render(request, 'publicweb/dwelling_form.html', {'form': form})
    else:
        form=DwellingForm(instance=dwelling)
        return render(request, 'publicweb/dwelling_form.html', {'form': form})

@login_required
def edit_pledge(request, pledge_id):
    pledge = Pledge.objects.filter(id=pledge_id).first()
    if not pledge:
        return redirect('profile')

    if pledge.user != request.user:
        return redirect('access_denied')
    if request.method == 'POST':
        form = PledgeForm(request.POST, instance=pledge)

        if form.is_valid():
            form.save()
        return redirect('profile')
    else:
        form = PledgeForm(instance=pledge)
        return render(request, 'publicweb/pledge_form.html', {'form': form})

@login_required
def pledge_complete(request, pledge_id):
    pledge = Pledge.objects.filter(id=pledge_id).first()
    if not pledge:
        return redirect('profile')

    if pledge.user != request.user:
        return redirect('access_denied')
    if request.method == 'POST':
        form = PledgeCompleteForm(request.POST, instance=pledge)
        if form.is_valid():
            p = form.save()
            p.complete = True
            p.save()
        return redirect('profile')
    else:
        form = PledgeCompleteForm(instance=pledge)
        return render(request, 'publicweb/pledge_complete.html', {'form': form})

@login_required
def delete_pledge(request, pledge_id):
    pledge = Pledge.objects.filter(id=pledge_id).first()
    if not pledge:
        return redirect('profile')
    if pledge.user != request.user:
        return redirect('access_denied')

    if request.method == 'POST':

        pledge.delete()
        return redirect('profile')
    else:
        return render(request, 'publicweb/delete_pledge.html')

# def possible_measures(request):
#     measures = Measure.objects.all()
#     context = {
#         'measures': measures, 
#     }
#     return render(request, 'publicweb/measures_list.html', context)

@login_required
def make_pledge(request):
    if request.method == 'POST':
        time_period = int(request.POST['time_period'])
        measure_id = request.POST['measure_id']
        measure = Measure.objects.get(id=measure_id)
        hat_results_id = request.POST['hat_results_id']
        if hat_results_id:
            hat_results = HatResultsDatabase.objects.get(id=hat_results_id)
        else:
            hat_results = None

        if request.POST.get('interest_only'):
            pledge_type = Pledge.INTEREST_ONLY
        else:
            pledge_type = Pledge.PLEDGE

        # print Pledge.objects.filter(measure=measure, user=request.user)
        if len(Pledge.objects.filter(measure=measure, user=request.user)) == 0:
            if pledge_type == Pledge.PLEDGE:
                now = datetime.now()
                duration = time_period * 30 # time period is in months
                deadline = now + timedelta(days=duration)
            else:
                deadline = None
            pledge = Pledge(measure=measure, user=request.user, deadline=deadline,
                hat_results=hat_results, receive_updates=request.POST.get('receive_updates', False),
                pledge_type=pledge_type)
            pledge.save()
        else:
            # if pledge has already been made for that measure...
            pass
        # this needs to ultimately redirect to a 'my pledges' page
        return redirect('profile')
    else:
        print "Not a POST request"



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
        top = False
    else:
        area_above = None
        pledge_difference_with_area_above = None
        top = True
    if area_ranking  < len(area_pledge_counts):
        area_below = area_pledge_counts[area_ranking]
        pledge_difference_with_area_below = total_pledges - area_below.pledge_count
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


def pledges_for_area(request, postcode_district):
    get_areas_with_total_pledges()

    short_postcode = postcode_district[:4]
    spaced_postcode = space_postcode(postcode_district)
    consumption_data = get_consumption_row_for_postcode(spaced_postcode)

    area = Area.objects.get(postcode_district=short_postcode)
    pledges_in_area = Pledge.objects.filter(pledge_type = Pledge.PLEDGE, user__userprofile__dwelling__area=area)
    total_pledges = pledges_in_area.count()
    pledge_progress = pledge_results_with_progress(pledges_in_area)
    total_reduction = get_total_reduction(pledges_in_area)
    total_completed_reduction = get_total_reduction(pledges_in_area.filter(complete=True))

    measure_pledge_counts = Measure.objects.filter(pledge__in=pledges_in_area).annotate(pledge_count=Count('pledge')).order_by('-pledge_count')[:20]
 
    ranking_details = get_ranking_details(area, total_pledges)
    pledges_with_positions = get_pledges_with_positions(pledges_in_area)
    context = {
        'pledge_progress': pledge_progress,
        'area': area,
        'page_type': 'area',
        'consumption_data': consumption_data,
        'pledges_with_positions': pledges_with_positions,

        'total_reduction':total_reduction,
        'total_completed_reduction':total_completed_reduction,
        'total_pledges': total_pledges,
        'measure_pledge_counts':measure_pledge_counts,
        'ranking_details': ranking_details,
        'map_initial': get_map_initial(area.position.latitude,
            area.position.longitude),
    }
    return render(request, 'publicweb/area_pledge_page.html', context)



def all_pledges(request):
    pledges = Pledge.objects.filter(pledge_type = Pledge.PLEDGE).order_by('date_made')
    total_pledges = pledges.count()
    most_recent_10_pledges_with_progress = pledge_results_with_progress(pledges[:10])
    total_reduction = get_total_reduction(pledges)
    total_completed_reduction = get_total_reduction(pledges.filter(complete=True))
    pledges_with_positions = get_pledges_with_positions(pledges)
    measure_pledge_counts = Measure.objects.filter(pledge__in=pledges).annotate(pledge_count=Count('pledge')).order_by('-pledge_count')[:20]

    context = {
        'pledges_with_positions':pledges_with_positions,
        'pledge_progress': most_recent_10_pledges_with_progress,
        'page_type': 'all_pledges',
        'map_initial': get_map_initial(51.4500388,
            -2.5588662),
        'measure_pledge_counts':measure_pledge_counts,
        'total_pledges': total_pledges,
        'total_reduction':total_reduction,
        'total_completed_reduction':total_completed_reduction,
    }
    return render(request, 'publicweb/all_pledges.html', context)

@login_required
def my_pledges(request):
    pledges = Pledge.objects.filter(user=request.user)
    pledges_with_positions = get_pledges_with_positions(pledges)
    pledge_progress = pledge_results_with_progress(pledges)
    full_pledges = pledges.filter(pledge_type=Pledge.PLEDGE)
    total_reduction = get_total_reduction(full_pledges)
    total_completed_reduction = get_total_reduction(full_pledges.filter(complete=True))

    user_dwelling = get_dwelling(request.user)
    if user_dwelling and user_dwelling.position:
        map_initial = get_map_initial(user_dwelling.position.latitude,
            user_dwelling.position.longitude, 15)
    else:
        map_initial = get_map_initial(51.4500388, -2.5588662)

    context = {
        'pledge_progress': pledge_progress,
        'total_reduction': total_reduction,
        'total_completed_reduction':total_completed_reduction,
        'page_type': 'profile',
        'pledges_with_positions':pledges_with_positions,
        'map_initial': map_initial,
    }

    return render(request, 'publicweb/my_pledges.html', context)

def area_list(request):
    context = {
        'areas': Area.objects.all()
    }
    return render(request, 'publicweb/area_list.html', context)

def about(request):
    """Gets about page details from database, renders about page """
    about = AboutPage.objects.all().first()
    context = {
        'about':about,
    }
    return render(request, 'publicweb/about.html', context)

##### helper functions #####
def get_measures_with_identifiers():
    """ Returns dict of measure ids with name converted from Loft Insulation to loft_insulation"""
    measures = Measure.objects.all()
    measure_ids = {}
    for m in measures:
        measure_ids[convert_name_to_identifier(m.name)] = m.id
    return measure_ids

# def get_pledges_with_progress(user):
#     """ Returns dict with pledges and the time details needed to display progress bar"""
#     pledge_progress = {}
#     # get pledges    
#     user_pledges = Pledge.objects.filter(user=user)
#     pledge_progress = pledge_results_with_progress(user_pledges)
#     return pledge_progress

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