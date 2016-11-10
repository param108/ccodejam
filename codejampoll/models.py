from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Votes(models.Model):
  user = models.ForeignKey(User)
  shortname = models.CharField(max_length=200)
  longname = models.CharField(max_length=200)
  tag = models.CharField(max_length=30) 
