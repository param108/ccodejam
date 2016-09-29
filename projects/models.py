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
  judgingopen=models.BooleanField(default=False)

class ReadOut(models.Model):
  start=models.DateField(auto_now_add=True)
  batch=models.ForeignKey(Batch)
  isopen=models.BooleanField(default=True)

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

# have only one scorecard per batch
class ScoreCard(models.Model):
  batch = models.ForeignKey(Batch)

# links scorecard, readout and user
# only one per user-readout-project
class ScoreCardUser(models.Model):
  project=models.ForeignKey(Project,null=True)
  readout=models.ForeignKey(ReadOut)
  user=models.ForeignKey(User)
  scorecard=models.ForeignKey(ScoreCard)


class ScoreQn(models.Model):
  qn = models.CharField(max_length=200, unique=True)
  subqn = models.CharField(max_length=200, default="")
  type = models.CharField(max_length=20)
  weight = models.IntegerField(default=1)

class ScoreCardLink(models.Model):
  # added nullable for migration
  scorecard=models.ForeignKey(ScoreCard,null=True)
  qn = models.ForeignKey(ScoreQn)
  seq = models.IntegerField()

class ScoreAns(models.Model):
  scorecarduser = models.ForeignKey(ScoreCardUser,null=True)
  user = models.ForeignKey(User)
  link = models.ForeignKey(ScoreCardLink)
  ansint = models.IntegerField(null=True)
  anschar = models.CharField(max_length=1000, null=True)

class Judges(models.Model):
  batch= models.ForeignKey(Batch)
  username= models.CharField(max_length=100,unique=True)
