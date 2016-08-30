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
from projects import views
urlpatterns = [
    url(r'^batch/my/', views.mybatches, name="batchmy"),
    url(r'^batch/show/', views.batches, name="batchshow"),
    url(r'^batch/new/', views.addBatch, name="batchadd"),
    url(r'^batch/edit/(?P<batchid>[0-9]+)/', views.editBatch, name="batchedit"),
    url(r'^batch/del/(?P<batchid>[0-9]+)/', views.delBatch, name="batchdel"),
    url(r'^add/(?P<batchid>[0-9]+)/', views.addProjects, name="projectadd"),
    url(r'^my/(?P<batchid>[0-9]+)/', views.myProjects, name="projectmy"),
    url(r'^del/(?P<batchid>[0-9]+)/(?P<projectid>[0-9]+)/', views.delProjects, name="projectdel"),
    url(r'^update/(?P<batchid>[0-9]+)/', views.updateProjects, name="projectupd"),
    url(r'^mentors/add/(?P<batchid>[0-9]+)/(?P<projectid>[0-9]+)/', views.addMentors, name="mentorsadd"),
    url(r'^mentors/update/(?P<batchid>[0-9]+)/(?P<projectid>[0-9]+)/', views.updateMentors, name="mentorsupdate"),
    url(r'^mentors/del/(?P<batchid>[0-9]+)/(?P<projectid>[0-9]+)/(?P<memberid>[0-9]+)/', views.delMentors, name="mentorsdel"),
    url(r'^milestones/add/(?P<batchid>[0-9]+)/(?P<projectid>[0-9]+)/', views.addMilestones, name="milestonesadd"),
    url(r'^milestones/update/(?P<batchid>[0-9]+)/(?P<projectid>[0-9]+)/', views.updateMilestones, name="milestonesupdate"),
    url(r'^milestones/del/(?P<batchid>[0-9]+)/(?P<projectid>[0-9]+)/(?P<lid>[0-9])/', views.delMilestones, name="milestonesdel"),
]
