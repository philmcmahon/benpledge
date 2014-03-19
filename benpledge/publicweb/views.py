from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.views.generic.base import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, timedelta, date

from models import Measure, Dwelling, UserProfile, HatMetaData, HouseIdLookup, HatResultsDatabase, Pledge, Area
from forms import DwellingForm, PledgeForm


def index(request):
    return render(request, 'publicweb/index.html')

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
        if pledge:
            time_remaining = datetime.combine(pledge.deadline, datetime.min.time()) - datetime.now()
            time_remaining = time_remaining.days
            days_remaining = time_remaining % 30
            months_remaining = time_remaining/30
            time_remaining = str(months_remaining) + " months, " + str(days_remaining) + " days" 

    context = {
        'measure': m,
        'hat_info': hat_info,
        'payback_time_estimate' : payback_time_estimate,
        'pledge' : pledge,
        'time_remaining': time_remaining,
    }
    return render(request, 'publicweb/measure.html', context)

@login_required
def dwelling_form(request):
    dwelling = get_dwelling(request.user)
    if request.method == 'POST':
        form = DwellingForm(request.POST, instance=dwelling)

        print form.instance
        updated_dwelling = form.save(commit=False)
        updated_dwelling.house_id = get_house_id(updated_dwelling)
        updated_dwelling.save()

        if form.is_valid():
            if dwelling == None:
                current_user_profile.save()
            return profile(request)
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
        return profile(request)
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
        hat_results = HatResultsDatabase.objects.get(id=hat_results_id)
        print Pledge.objects.filter(measure=measure, user=request.user)
        if len(Pledge.objects.filter(measure=measure, user=request.user)) == 0:
            now = datetime.now()
            duration = time_period * 30 # time period is in months
            deadline = now + timedelta(days=duration)
            pledge = Pledge(measure=measure, user=request.user, deadline=deadline, hat_results=hat_results)
            pledge.save()
        else:
            # if pledge has already been made for that measure...
            pass
        # this needs to ultimately redirect to a 'my pledges' page
        return profile(request)
    else:
        print "Not a POST request"

@login_required
def delete_pledge(request, pledge_id):
    if request.method == 'POST':
        p = Pledge.objects.get(id=pledge_id)
        p.delete()
        return profile(request)
    else:
        return render(request, 'publicweb/delete_pledge.html')

def pledges_for_area(request, postcode_district):
    area = Area.objects.get(postcode_district=postcode_district)
    dwellings_in_area = Dwelling.objects.filter(area=area)
    users_in_area = UserProfile.objects.filter(dwelling__in=dwellings_in_area)
    users_in_area = User.objects.filter(userprofile__in=users_in_area)
    pledges_in_area = Pledge.objects.filter(user__in=users_in_area)
    print pledges_in_area
    print "printing area pledges"
    context = {
        'pledge_progress': pledge_results_with_progress(pledges_in_area),
        'area': area,
    }
    return render(request, 'publicweb/area_pledge_page.html', context)

def area_list(request):
    context = {
        'areas': Area.objects.all()
    }
    return render(request, 'publicweb/area_list.html', context)



@login_required
def profile(request):
    measures = Measure.objects.all()
    measure_ids = {}
    for m in measures:
        measure_ids[convert_name_to_identifier(m.name)] = m.id

    user_measures = get_user_hat_results(request.user)

    pledge_progress = get_pledges_with_progress(request.user)
    # if not pledge_progress:
    #     pledge_progress = None

    # user_pledges['time_progress'] = datetime.now() - user_pledges['date_made']
    context = {
        'measure_ids': measure_ids, 
        'user_measures': user_measures,
        'pledge_progress' : pledge_progress,
        'area': None
    }
    return render(request, 'publicweb/base_profile.html', context)

##### helper functions #####
def get_pledges_with_progress(user):
    pledge_progress = {}
    # get pledges    
    user_pledges = Pledge.objects.filter(user=user)
    pledge_progress = pledge_results_with_progress(user_pledges)
    return pledge_progress

def pledge_results_with_progress(pledges):
    pledge_progress = {}
    for p in pledges:
        time_progress = Pledge.time_progress(p)
        pledge_progress[p.id] = {
            'pledge' : p,
            'time_progress': Pledge.time_progress(p)
        }
    return pledge_progress

def get_user_hat_results(user):
    """ Returns dictionary of suitable measures for user """
    dwelling = get_dwelling(user)
    houseid = get_house_id(dwelling)
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
        if not field.value:
            return 0
        else:
            combined_info += str(field.value)
    house_id_lookup_row = HouseIdLookup.objects.get(index_id=combined_info)
    return house_id_lookup_row.house_id


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





