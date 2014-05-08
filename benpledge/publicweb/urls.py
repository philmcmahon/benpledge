from django.conf.urls import include, patterns, url


from publicweb import views

urlpatterns = patterns('',
    url(r'^getstarted/$', views.get_started, name='get_started'),
    url(r'^help/$', views.help_page, name='help_page'),
    # pledges pages
    url(r'^pledges/all/$', views.all_pledges, name='all_pledges'),
    url(r'^pledges/my_pledges/$', views.my_pledges, name='my_pledges' ),
    url(r'^pledges/complete/(?P<pledge_id>\d+)/', views.pledge_complete, name='pledge_complete'),
    url(r'^pledges/edit/(?P<pledge_id>\d+)/', views.edit_pledge, name='edit_pledge'),
    url(r'^pledges/delete/(?P<pledge_id>\d+)/', views.delete_pledge, name='delete_pledge'),

    url(r'^areas/$', views.area_list, name='area_list'),
    url(r'^areas/(?P<postcode_district>\w+)/$', views.pledges_for_area, name='pledges_for_area'),

    url(r'^accounts/myhome/$', views.dwelling_form, name='dwelling_form'),
    # url(r'^accounts/possible_measures/$', views.possible_measures, name='possible_measures'),
    url(r'^accounts/makepledge/$', views.make_pledge, name='make_pledge'),

    # Measures pages
    url(r'^all_measures/$', views.general_measures, name='general_measures'),
    url(r'^measures/(?P<measure_id>\d+)/$', views.measure, name='measure'),
    # profile
    url(r'^users/(?P<username>\w+)/$', views.profile, name='profile_registration'),
    url(r'^accounts/profile/$', views.profile, name='profile'),
    # hat filter
    url(r'^hat_filter/$', views.hat_filter, name='hat_filter'),
    # django authentication
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page' : '/', 'redirect_field_name' : '/'}),
    url(r'^accounts/password_reset/$', 'django.contrib.auth.views.password_reset', {'template_name': 'registration/password_templates/password_reset_form.html'}, name='password_reset'),
    url(r'^accounts/password_reset_done/$', 'django.contrib.auth.views.password_reset_done', {'template_name': 'registration/password_templates/password_reset_done.html'},  name='password_reset_done'),
    url(r'^accounts/password_reset_confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm', {'template_name': 'registration/password_templates/password_reset_confirm.html'},  name='password_reset_confirm'),
    url(r'^accounts/password_reset_complete/$', 'django.contrib.auth.views.password_reset_complete', {'template_name': 'registration/password_templates/password_reset_complete.html'}, name='password_reset_complete'),
    url(r'^accounts/password_change/$', 'django.contrib.auth.views.password_change', {'template_name': 'registration/password_templates/password_change_form.html'}, name='password_change'),
    url(r'^accounts/password_change_done/$', 'django.contrib.auth.views.password_change_done', {'template_name': 'registration/password_templates/password_change_done.html'}, name='password_change_done'),
    
    # admin overview pages
    url(r'^pledge_overview/$', views.pledge_admin_overview, name='pledge_admin_overview'),
    url(r'^user_overview/$', views.user_admin_overview, name='user_admin_overview'),
    url(r'^accounts/', include('registration.backends.simple.urls')),
    # access denied
    url(r'^access_denied/', views.access_denied, name='access_denied'),
    # about
    url(r'^about/$', views.about, name='about'),
    # home page
    url(r'^$', views.index, name='index'),
)
