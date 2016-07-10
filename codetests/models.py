from __future__ import unicode_literals
from coding.models import Qns
from django.db import models

# Create your models here.
class CodeTests(models.Model):
  testname=models.CharField(unique=True, max_length=50)
  start=models.DateTimeField()
  duration=models.IntegerField()

class CodeQnsList(models.Model):
  qn=models.ForeignKey(Qns)
  testid=models.ForeignKey(CodeTests)
  seq=models.IntegerField(default=0) 
