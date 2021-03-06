import re, urllib, urllib2, json
from datetime import datetime, timedelta, date
from collections import defaultdict

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.views.generic.base import View
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count


from registration.backends.simple.views import RegistrationView
from models import (Measure, Dwelling, UserProfile,
    HouseIdLookup, HatResultsDatabase, Pledge, Area, PostcodeOaLookup,
    LsoaDomesticEnergyConsumption, TopTip, Organisation, HomepageCheckList, EcoEligible,
    AboutPage, FundingOption, Provider)
from forms import DwellingForm, PledgeForm, PledgeCompleteForm, HatFilterForm
from utils import *

from postcode_parser import parse_uk_postcode

""" Each method in this file renders a page of the application"""

def access_denied(request):
    """Curently, this page is used when a user tries to delete, edit or complete
        a pledge not belonging to them """
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

def about(request):
    """View for about page """
    about = AboutPage.objects.all().first()
    context = {
        'about':about,
    }
    return render(request, 'publicweb/about.html', context)

def general_measures(request):
    """ All Measures page"""

    small_measures = Measure.objects.filter(size=Measure.SMALL)
    medium_measures = Measure.objects.filter(size=Measure.MEDIUM)
    large_measures = Measure.objects.filter(size=Measure.LARGE)
    funding_options = FundingOption.objects.all()

    context = {
        # context for the image map on this page
        'measure_ids': get_measures_with_identifiers(),
        # funding information for side bar
        'funding_options': funding_options,
        # measure list context
        'small_measures':small_measures,
        'medium_measures': medium_measures,
        'large_measures':large_measures,
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
def hat_filter(request):
    """ View for the HAT filter page """
    # verify user has a dwelling and the dwelling has HAT results
    dwelling = Dwelling.objects.filter(userprofile__user=request.user).first()
    if not dwelling:
        return redirect('profile')
    if not dwelling.house_id:
        return redirect('profile')

    if request.method == 'POST':
        user_measures = None
        form = HatFilterForm(request.POST)
        # if form is valid, update HAT results table
        if form.is_valid():
            user_measures = get_dwelling_hat_results(dwelling, form.cleaned_data)
    else:
        form = HatFilterForm()
        user_measures = get_dwelling_hat_results(dwelling)

    context = {
        'form':form,
        'user_measures': user_measures,
    }
    return render(request, 'publicweb/hat_filter.html', context)



@login_required
def profile(request, username=None):
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
        'user_measures': user_measures,
        'eco_eligible': eco_eligible,
        'dwelling': userprofile.dwelling,
        # context for pledge_progress_list.html
        'pledge_progress' : pledge_progress,
        'page_type': 'profile',
        'total_reduction': total_reduction,
        'total_completed_reduction':total_completed_reduction,
    }
    return render(request, 'publicweb/base_profile.html', context) 


def measure(request, measure_id):
    m = Measure.objects.filter(id=measure_id).first()
    # check that the measure exists
    if not m:
        return redirect('general_measures')
    # If a user is logged in and has a dwelling with a house id
    # fetch the HAT results for that house 
    hat_info = None
    payback_time_estimate = None
    if m.hat_measure and request.user.is_authenticated():
        dwelling = get_dwelling(request.user)
        if dwelling and dwelling.house_id:
            hat_info = get_hat_results(dwelling.house_id,
                m.hat_measure.measure_id)
    if hat_info:
        payback_time_estimate = get_payback_time(hat_info)

    # Get feedback on this measure
    feedback_pledges = Pledge.objects.filter(measure=m, complete=True, display_feedback_on_measure_page=True)
    # Get top 3 providers for this measure
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
        'providers':providers,
        # pledge feedback
        'feedback_pledges':feedback_pledges,
        # context if pledge has already been made
        'pledge' : pledge,
        'time_remaining': time_remaining,
    }
    return render(request, 'publicweb/measure.html', context)

@login_required
def dwelling_form(request):
    dwelling = get_dwelling(request.user)
    current_user_profile = UserProfile.objects.get(user=request.user)

    # save these values to avoid unnecessary API requests
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
            # if so, update the house id
            updated_dwelling.house_id = get_house_id(updated_dwelling)

            updated_dwelling.save()

            if dwelling == None:
                print "updating dwelling"
                current_user_profile.dwelling = updated_dwelling
                current_user_profile.save()
            return redirect('profile')
        else:
            return render(request, 'publicweb/dwelling_form.html', {'form': form})
    else:
        form=DwellingForm(instance=dwelling)
        return render(request, 'publicweb/dwelling_form.html', {'form': form})

@login_required
def edit_pledge(request, pledge_id):
    pledge = Pledge.objects.filter(id=pledge_id).first()
    # verify pledge exists
    if not pledge:
        return redirect('profile')
    # verify pledge belongs to user
    if pledge.user != request.user:
        return redirect('access_denied')
    # update pledge
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
    # verify pledge exists
    if not pledge:
        return redirect('profile')
    # verify pledge belongs to user
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
    # verify pledge exists
    if not pledge:
        return redirect('profile')
    # verify pledge belongs to user
    if pledge.user != request.user:
        return redirect('access_denied')

    if request.method == 'POST':
        pledge.delete()
        return redirect('profile')
    else:
        return render(request, 'publicweb/delete_pledge.html')

@login_required
def make_pledge(request):
    if request.method == 'POST':
        # get hidden fields from the form
        time_period = int(request.POST['time_period'])
        measure_id = request.POST['measure_id']
        hat_results_id = request.POST['hat_results_id']
        # fetch measure from the database
        measure = Measure.objects.get(id=measure_id)

        # if hat results available for pledge, store them
        if hat_results_id:
            hat_results = HatResultsDatabase.objects.get(id=hat_results_id)
        else:
            hat_results = None

        # check pledge type
        if request.POST.get('interest_only'):
            pledge_type = Pledge.INTEREST_ONLY
        else:
            pledge_type = Pledge.PLEDGE

        # if the pledge has not already been made by this user for this measure
        # save the pledge
        if len(Pledge.objects.filter(measure=measure, user=request.user)) == 0:
            if pledge_type == Pledge.PLEDGE:
                now = datetime.now()
                duration = time_period * 30 # time period is in months
                deadline = now + timedelta(days=duration)
            else:
                deadline = None
            # create pledge
            pledge = Pledge(measure=measure, user=request.user, deadline=deadline,
                hat_results=hat_results, receive_updates=request.POST.get('receive_updates', False),
                pledge_type=pledge_type)
            pledge.save()
        else:
            # if pledge has already been made for that measure...
            pass
        return redirect('profile')
    else:
        print "Not a POST request"
        return redirect('profile')

def area_list(request):
    """List of areas page"""
    context = {
        'areas': Area.objects.all()
    }
    return render(request, 'publicweb/area_list.html', context)

def pledges_for_area(request, postcode_district):
    get_areas_with_total_pledges()

    short_postcode = postcode_district[:4]
    # for fetching lsoa energy consumption
    spaced_postcode = space_postcode(postcode_district)
    consumption_data = get_consumption_row_for_postcode(spaced_postcode)

    # collect pledge information for this area
    area = Area.objects.get(postcode_district=short_postcode)
    pledges_in_area = Pledge.objects.filter(pledge_type = Pledge.PLEDGE, user__userprofile__dwelling__area=area)
    total_pledges = pledges_in_area.count()
    pledge_progress = pledge_results_with_progress(pledges_in_area)
    total_reduction = get_total_reduction(pledges_in_area)
    total_completed_reduction = get_total_reduction(pledges_in_area.filter(complete=True))
    ranking_details = get_ranking_details(area, total_pledges)
    measure_pledge_counts = Measure.objects.filter(pledge__in=pledges_in_area).annotate(pledge_count=Count('pledge')).order_by('-pledge_count')[:10]
 
    # get_pledges_with_positions returns all pledges
    pledges_with_positions = get_pledges_with_positions(pledges_in_area)
    context = {
        # context for pledge list
        'pledge_progress': pledge_progress,
        'page_type': 'area',
        'total_reduction':total_reduction,
        'total_completed_reduction':total_completed_reduction,
        # area context
        'area': area,
        # this context is currently unused - lsoa details
        # 'consumption_data': consumption_data,
        
        # context for the pledge map
        'pledges_with_positions': pledges_with_positions,
        'map_initial': get_map_initial(area.position.latitude,
            area.position.longitude),
        # area pledge details
        'total_pledges': total_pledges,
        'measure_pledge_counts':measure_pledge_counts,
        'ranking_details': ranking_details,
    }
    return render(request, 'publicweb/area_pledge_page.html', context)

def all_pledges(request):
    # get all pledges, generate pledge statistics and counts
    pledges = Pledge.objects.filter(pledge_type = Pledge.PLEDGE).order_by('date_made')
    total_pledges = pledges.count()
    most_recent_10_pledges_with_progress = pledge_results_with_progress(pledges[:10])
    total_reduction = get_total_reduction(pledges)
    total_completed_reduction = get_total_reduction(pledges.filter(complete=True))
    measure_pledge_counts = Measure.objects.filter(pledge__in=pledges).annotate(pledge_count=Count('pledge')).order_by('-pledge_count')[:10]
    # info for map
    pledges_with_positions = get_pledges_with_positions(pledges)
    context = {
        # pledge list context
        'pledge_progress': most_recent_10_pledges_with_progress,
        'page_type': 'all_pledges',
        'total_reduction':total_reduction,
        'total_completed_reduction':total_completed_reduction,
        # map context
        'pledges_with_positions':pledges_with_positions,
        'map_initial': get_map_initial(51.4500388,
            -2.5588662),
        # pledge counts and statistics
        'measure_pledge_counts':measure_pledge_counts,
        'total_pledges': total_pledges,
    }
    return render(request, 'publicweb/all_pledges.html', context)

@login_required
def my_pledges(request):
    # fetch pledges for the current user
    pledges = Pledge.objects.filter(user=request.user)
    # get context for plotting pledges
    pledges_with_positions = get_pledges_with_positions(pledges)
    # information for pledge list
    pledge_progress = pledge_results_with_progress(pledges)
    full_pledges = pledges.filter(pledge_type=Pledge.PLEDGE)
    total_reduction = get_total_reduction(full_pledges)
    total_completed_reduction = get_total_reduction(full_pledges.filter(complete=True))

    # set initial map location to the location of the users' dwelling
    user_dwelling = get_dwelling(request.user)
    if user_dwelling and user_dwelling.position:
        map_initial = get_map_initial(user_dwelling.position.latitude,
            user_dwelling.position.longitude, 15)
    else:
        map_initial = get_map_initial(51.4500388, -2.5588662)

    context = {
        # pledge list context
        'pledge_progress': pledge_progress,
        'page_type': 'profile',
        'total_reduction': total_reduction,
        'total_completed_reduction':total_completed_reduction,
        # map context
        'pledges_with_positions':pledges_with_positions,
        'map_initial': map_initial,
    }

    return render(request, 'publicweb/my_pledges.html', context)



