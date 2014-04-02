from django.conf.urls import include, patterns, url


from publicweb import views

urlpatterns = patterns('',
    url(r'^getstarted/$', views.get_started, name='get_started'),
    url(r'^help/$', views.help_page, name='help_page'),
    url(r'^pledges/all/$', views.all_pledges, name='all_pledges'),
    url(r'^pledges/(?P<postcode_district>\w+)/$', views.pledges_for_area, name='pledges_for_area'),
    url(r'^areas/$', views.area_list, name='area_list'),
    url(r'^accounts/myhome/$', views.dwelling_form, name='dwelling_form'),
    url(r'^accounts/possible_measures/$', views.possible_measures, name='possible_measures'),
    url(r'^accounts/makepledge/$', views.make_pledge, name='make_pledge'),
    url(r'^pledges/edit/(?P<pledge_id>\d+)/', views.edit_pledge, name='edit_pledge'),
    url(r'^pledges/delete/(?P<pledge_id>\d+)/', views.delete_pledge, name='delete_pledge'),
    url(r'^measures/$', views.general_measures, name='general_measures'),
    url(r'^measures/(?P<measure_id>\d+)/', views.measure, name='measure'),
    # django authentication
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page' : '/', 'redirect_field_name' : '/'}),
    url(r'^accounts/password_reset/$', 'django.contrib.auth.views.password_reset', name='password_reset'),
    url(r'^accounts/password_reset_done/$', 'django.contrib.auth.views.password_reset_done',  name='password_reset_done'),
    url(r'^accounts/password_reset_confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm',  name='password_reset_confirm'),
    url(r'^accounts/password_reset_complete/$', 'django.contrib.auth.views.password_reset_complete', name='password_reset_complete'),
    url(r'^accounts/password_change/$', 'django.contrib.auth.views.password_change', name='password_change'),
    url(r'^accounts/password_change_done/$', 'django.contrib.auth.views.password_change_done', name='password_change_done'),
    url(r'^accounts/profile/$', views.profile, name='profile'),
    url(r'^accounts/', include('registration.backends.default.urls')),
    # (r'^media/', name='media')
    url(r'^$', views.index, name='index'),
)
