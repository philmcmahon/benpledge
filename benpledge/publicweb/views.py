from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.views.generic.base import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, timedelta, date

import re, urllib, urllib2, json

from models import (Measure, Dwelling, UserProfile, HatMetaData,
    HouseIdLookup, HatResultsDatabase, Pledge, Area, PostcodeOaLookup,
    LsoaDomesticEnergyConsumption, TopTip, Organisation, HomepageCheckList, EcoEligible,
    AboutPage)
from forms import DwellingForm, PledgeForm

from postcode_parser import parse_uk_postcode

from benpledge_keys import GOOGLE_API_KEY


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
    context = {
        'measure_ids': get_measures_with_identifiers(),
        'measures1': measures1,
        'measures2': measures2,
    }
    return render(request, 'publicweb/general_measures.html', context)

def help_page(request):
    organisations = Organisation.objects.all().order_by('organisation_type', 'name')
    context = {
        'organisations': organisations,
    }
    return render(request, 'publicweb/help_page.html', context)

@login_required
def profile(request):
    measure_ids = get_measures_with_identifiers()

    userprofile = UserProfile.objects.get(user=request.user)

    if userprofile.dwelling:
        user_measures = get_user_hat_results(request.user)
    else:
        user_measures = None
        return redirect('dwelling_form')

    pledge_progress = get_pledges_with_progress(request.user)
    total_reduction = get_total_reduction(pledge_progress)
    # if not pledge_progress:
    #     pledge_progress = None

    # user_pledges['time_progress'] = datetime.now() - user_pledges['date_made']

    if userprofile.dwelling.postcode:
        eco_eligible =  get_eco_eligible(userprofile.dwelling.postcode)
    else:
        eco_eligible = 'unknown'

    # get_consumption_row_for_postcode("BS8  2DJ")
    context = {
        'measure_ids': measure_ids, 
        'user_measures': user_measures,
        'pledge_progress' : pledge_progress,
        'page_type': 'profile',
        'total_reduction': total_reduction,
        'eco_eligible': eco_eligible,
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
    
    if request.method == 'POST':
        form = DwellingForm(request.POST, instance=dwelling)
        if form.is_valid():
            updated_dwelling = form.save(commit=False)
            ##### MAKE NOT UPDATE IF UNCHANGED####
            if (updated_dwelling.street_name or updated_dwelling.area and
                updated_dwelling.street_name != current_street_name or updated_dwelling.area != current_area):
                address_string = get_address_from_street_name_or_area(updated_dwelling.street_name,
                    updated_dwelling.area)
                print address_string
                location = geocode_address(address_string)
                print location
                updated_dwelling.position.latitude = location['lat']
                updated_dwelling.position.longitude = location['lng']

            updated_house_id = get_house_id(updated_dwelling)
            if updated_house_id:
                updated_dwelling.house_id = updated_house_id
            # updated_dwelling.postcode = form.cleaned_data
            updated_dwelling.save()
            if dwelling == None:
                current_user_profile.dwelling = updated_dwelling
                current_user_profile.save()
            return redirect('profile')
        else:
            print form.errors
            return render(request, 'publicweb/dwelling_form.html', {'form': form})
    else:
        form=DwellingForm(instance=dwelling)
        return render(request, 'publicweb/dwelling_form.html', {'form': form})

@login_required
def edit_pledge(request, pledge_id):
    pledge = Pledge.objects.get(id=pledge_id)
    if request.method == 'POST':
        form = PledgeForm(request.POST, instance=pledge)

        if form.is_valid():
            form.save()
        return redirect('profile')
    else:
        form = PledgeForm(instance=pledge)
        return render(request, 'publicweb/pledge_form.html', {'form': form})

def possible_measures(request):
    measures = Measure.objects.all()
    context = {
        'measures': measures, 
    }
    return render(request, 'publicweb/measures_list.html', context)

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

@login_required
def delete_pledge(request, pledge_id):
    if request.method == 'POST':
        p = Pledge.objects.get(id=pledge_id)
        p.delete()
        return redirect('profile')
    else:
        return render(request, 'publicweb/delete_pledge.html')

def pledges_for_area(request, postcode_district):

    short_postcode = postcode_district[:3]
    spaced_postcode = space_postcode(postcode_district)
    consumption_data = get_consumption_row_for_postcode(spaced_postcode)

    area = Area.objects.get(postcode_district=short_postcode)
    dwellings_in_area = Dwelling.objects.filter(area=area)
    users_in_area = UserProfile.objects.filter(dwelling__in=dwellings_in_area)
    users_in_area = User.objects.filter(userprofile__in=users_in_area)
    pledges_in_area = Pledge.objects.filter(user__in=users_in_area, pledge_type = Pledge.PLEDGE)
    pledge_progress = pledge_results_with_progress(pledges_in_area)
    total_reduction = get_total_reduction(pledge_progress)

    context = {
        'pledge_progress': pledge_progress,
        'area': area,
        'page_type': 'area',
        'total_reduction':total_reduction,
        'consumption_data': consumption_data,
    }
    return render(request, 'publicweb/area_pledge_page.html', context)

def all_pledges(request):
    pledges = Pledge.objects.filter(pledge_type = Pledge.PLEDGE).order_by('date_made')

    most_recent_10_pledges_with_progress = pledge_results_with_progress(pledges[:10])
    pledges_with_positions = {}
    for p in pledges:
        if p.user.userprofile.dwelling and p.user.userprofile.dwelling.position.latitude != 0:
            # pjson = Pledge.objects.get(id=p.id).value()
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
                    },
                'position': {
                    'lat': str(position.latitude),
                    'lng': str(position.longitude)
                    }
            })
    context = {
        'pledges_with_positions':pledges_with_positions,
        'pledge_progress':most_recent_10_pledges_with_progress,
        'page_type': 'all_pledges',
    }
    return render(request, 'publicweb/all_pledges.html', context)

@login_required
def my_pledges(request):
    pledge_progress = get_pledges_with_progress(request.user)
    total_reduction = get_total_reduction(pledge_progress)
    context = {
        'pledge_progress': pledge_progress,
        'total_reduction': total_reduction,
        'page_type': 'profile',
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

def get_pledges_with_progress(user):
    """ Returns dict with pledges and the time details needed to display progress bar"""
    pledge_progress = {}
    # get pledges    
    user_pledges = Pledge.objects.filter(user=user)
    pledge_progress = pledge_results_with_progress(user_pledges)
    return pledge_progress

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

def get_user_hat_results(user):
    """ Returns dictionary of suitable measures for user """
    dwelling = get_dwelling(user)
    # houseid = get_house_id(dwelling)
    if dwelling.house_id:
        return {}
    measures = Measure.objects.all()
    hat_results = {}
    for m in measures:
        if m.hat_measure:
            hat_out = get_hat_results(houseid, m.hat_measure.measure_id)
            if suitable_measure(hat_out, m, dwelling.window_type):
                hat_results[m.id] = {
                'hat_results' : hat_out,
                'measure_name' : m.name,
                'payback_time_estimate': get_payback_time(hat_out),
                }
    return hat_results

def suitable_measure(hat_out, measure, window_type):
    """ Returns False if negative energy savings or measure otherwise unsuitable"""
    if not hat_out or hat_out.consumption_change <= 0 or hat_out.annual_cost_reduction <= 0:
        return False
    if window_type == Dwelling.DOUBLE_GLAZING and measure.name in ["Secondary glazing", "Double Glazing"]:
        return False
    return True

def get_payback_time(hat_info):
    if hat_info:
        return round((hat_info.approximate_installation_costs /
            hat_info.annual_cost_reduction), 1)
    else:
        return None

def get_house_id(dwelling):
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
    d = UserProfile.objects.get(user=user).dwelling
    return d

def convert_name_to_identifier(name):
    """ Replaces whitespace with underscores, decapitalises"""
    name = name.lower()
    name = name.replace(' ', '_')
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
    postcode_lookup = PostcodeOaLookup.objects.get(postcode=space_postcode(postcode))
    eco_eligible = EcoEligible.objects.filter(lsoa_code=postcode_lookup.lsoa_code).first()
    if eco_eligible:
        return True
    else:
        return False

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

def get_total_reduction(pledges_with_progress):
    """Returns the total carbon savings of all pledges in pledges_with_progress"""
    total_reduction = 0
    for k, p in pledges_with_progress.iteritems():
        if p['pledge'].pledge_type == Pledge.PLEDGE:
            pledge_energy_savings = get_pledge_energy_savings(p['pledge'])
            if pledge_energy_savings:
                total_reduction += pledge_energy_savings
    return total_reduction

def get_time_remaining(deadline):
    """ Gives the time in months and days until deadline"""
    time_remaining = datetime.combine(deadline, datetime.min.time()) - datetime.now()
    time_remaining = time_remaining.days
    days_remaining = time_remaining % 30
    months_remaining = time_remaining/30
    time_remaining = str(months_remaining) + " months, " + str(days_remaining) + " days" 
    return time_remaining

def get_pledge_energy_savings(pledge):
    if pledge.hat_results:
        return pledge.hat_results.consumption_change
    elif pledge.measure.estimated_annual_energy_savings_kwh:
        return pledge.measure.estimated_annual_energy_savings_kwh
    else:
        return None