from django.conf.urls import include, patterns, url


from publicweb import views

urlpatterns = patterns('',
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page' : '/', 'redirect_field_name' : '/'}),
    url(r'^accounts/profile/$', views.profile, name='profile'),
    (r'^accounts/', include('registration.backends.default.urls')),
    url(r'^$', views.index, name='index'),
)
