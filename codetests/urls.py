"""codejam URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from codetests import views
urlpatterns = [
    url(r'^show/$', views.show, name="show"),
    url(r'^questions/$', views.questions, name="questions"),
    url(r'^edit/(?P<testid>[0-9]+)/$', views.edit, name="edit"),
    url(r'^generate/(?P<testid>[0-9]+)/$', views.generate, name="generate"),
    url(r'^clone/(?P<testid>[0-9]+)/$', views.clone, name="clone"),
    url(r'^delete/(?P<testid>[0-9]+)/$', views.delete, name="delete"),
    url(r'^addqns/(?P<testid>[0-9]+)/$', views.addqns, name="addqns"),
    url(r'^editqn/(?P<qnid>[0-9]+)/$', views.editqn),
    url(r'^linkqn/(?P<testid>[0-9]+)/$', views.linkqn),
    url(r'^unlinkqn/(?P<testid>[0-9]+)/$', views.unlinkqn),
    url(r'^viewfile/(?P<qnid>[0-9]+)/(?P<size>[a-z]+)/$', views.viewfile),
]
