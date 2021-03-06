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
from coding import views
urlpatterns = [
    url(r'^tests/', views.testpage, name="tests"),
    url(r'^start/(?P<testid>[0-9]+)/', views.starttest, name="start"),
    url(r'^timeremaining/(?P<testid>[0-9]+)/', views.timeremaining),
    url(r'^question/(?P<attemptid>[0-9]+)/(?P<qnid>[0-9]+)/', views.showquestion, name="qn"),
    url(r'^uploadsolution/(?P<attemptid>[0-9]+)/(?P<qnid>[0-9]+)/(?P<size>[a-z]+)/', views.upload),
    url(r'^downloadqn/(?P<ansid>[0-9]+)/(?P<size>[a-z]+)/', views.dnload),
    url(r'^uploadtime/(?P<ansid>[0-9]+)/', views.uploadtime),
    url(r'^uploadfile/(?P<ansid>[0-9]+)/', views.uploadfile),
]
