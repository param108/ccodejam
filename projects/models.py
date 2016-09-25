from __future__ import unicode_literals
from django.contrib.auth.models import User

from django.db import models

# Create your models here.
class Batch(models.Model):
  batchname=models.CharField(unique=True, max_length=50)
  numreadouts=models.IntegerField(default=8)
  start=models.DateField()
  # number of weeks in between
  interval=models.IntegerField(default=2)
  # last date to enter data
  inputopen=models.BooleanField(default=True)
  showdashboard=models.BooleanField(default=False)

class Project(models.Model):
  batch=models.ForeignKey(Batch)
  title=models.CharField(unique=True, max_length=200)
  
class Member(models.Model):
  loggedin = models.BooleanField(default=False)
  username = models.CharField(max_length=30)
  user = models.ForeignKey(User, null=True) 
  role = models.CharField(max_length=50)
  project = models.ForeignKey(Project)

class Milestone(models.Model):
  date = models.DateField()
  project = models.ForeignKey(Project)
  seq = models.IntegerField(default=1)

class LineItem(models.Model):
  milestone = models.ForeignKey(Milestone)
  details = models.CharField(max_length=300)
  seq = models.IntegerField(default=1)
  # NOTSTARTED, WIP, DONE
  state = models.CharField(default="NOTSTARTED", max_length=20)

class FinalOutcome(models.Model):
  details = models.CharField(max_length=500)
  project=models.OneToOneField(Project)

class ScoreCard(models.Model):
  batch = models.ForeignKey(Batch)

class ScoreQn(models.Model):
  qn = models.CharField(max_length=200, unique=True)
  type = models.CharField(max_length=20)

class ScoreCardLink(models.Model):
  scorecard = models.ForeignKey(ScoreCard)
  qn = models.ForeignKey(ScoreQn)
  seq = models.IntegerField()

class ScoreAns(models.Model):
  user = models.ForeignKey(User)
  link = models.ForeignKey(ScoreCardLink)
  ansint = models.IntegerField(null=True)
  anschar = models.CharField(max_length=200, null=True)
