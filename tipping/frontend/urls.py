from django.conf.urls import include, url
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    url('^accounts/', include('registration.backends.simple.urls')),
    #url('^login', auth_views.login, name="login"),
    url('^$', views.base)
]