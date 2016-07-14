from __future__ import unicode_literals
from django.contrib.auth.models import User 
from django.db import models

def smallscript_upload(inst, filename):
  return "qns/"+str(inst.id)+"/small.py"

def largescript_upload(inst, filename):
  return "qns/"+str(inst.id)+"/large.py"

# Create your models here.
class Qns(models.Model):
  title=models.TextField(unique=True)
  description=models.TextField()
  # smalllimits are the limits for small set
  smalllimits=models.TextField()
  # largelimits are the limits for small set
  largelimits=models.TextField()
  inputexample=models.TextField() 
  outputexample=models.TextField() 
  # utimesmall the time allowed to upload the small solution
  utimesmall=models.IntegerField() 
  # utimelarge the time allowed to upload the large solution
  utimelarge=models.IntegerField() 
  # the files need to be uploaded after the first save!!!
  smallscript=models.FileField(upload_to=smallscript_upload, null=True)
  largescript=models.FileField(upload_to=largescript_upload, null=True)
  difficulty=models.IntegerField(default=1)
  

# Create your models here.
class CodeTests(models.Model):
  testname=models.CharField(unique=True, max_length=50)
  start=models.DateTimeField()
  end=models.DateTimeField(null=True)
  duration=models.IntegerField()
  valid=models.BooleanField(default=True)

class CodeQnsList(models.Model):
  qn=models.ForeignKey(Qns)
  testid=models.ForeignKey(CodeTests)
  seq=models.IntegerField(default=0) 


