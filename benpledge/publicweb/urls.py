from django.conf.urls import include, patterns, url


from publicweb import views

urlpatterns = patterns('',
    (r'^accounts/', include('registration.backends.default.urls')),
    url(r'^$', views.index, name='index'),
)
