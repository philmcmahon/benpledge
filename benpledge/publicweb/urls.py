from django.conf.urls import include, patterns, url


from publicweb import views

urlpatterns = patterns('',
    url(r'^pledges/(?P<postcode_district>\w+)/', views.pledges_for_area, name='pledges_for_area'),
    url(r'^areas/', views.area_list, name='area_list'),
    url(r'^accounts/myhome/$', views.dwelling_form, name='dwelling_form'),
    url(r'^accounts/possible_measures/$', views.possible_measures, name='possible_measures'),
    url(r'^accounts/makepledge/$', views.make_pledge, name='make_pledge'),
    url(r'^pledges/edit/(?P<pledge_id>\d+)/', views.edit_pledge, name='edit_pledge'),
    url(r'^pledges/delete/(?P<pledge_id>\d+)/', views.delete_pledge, name='delete_pledge'),
    url(r'^measures/(?P<measure_id>\d+)/', views.measure, name='measure'),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page' : '/', 'redirect_field_name' : '/'}),
    url(r'^accounts/profile/$', views.profile, name='profile'),
    (r'^accounts/', include('registration.backends.default.urls')),
    # (r'^media/', name='media')
    url(r'^$', views.index, name='index'),
)
