from __future__ import unicode_literals
from django.contrib.auth.models import User 
from django.db import models

def smallscript_upload(inst, filename):
  return "qns/"+str(inst.id)+"/small.py"

def largescript_upload(inst, filename):
  return "qns/"+str(inst.id)+"/large.py"

def translatorscript_upload(inst, filename):
  return "qns/"+str(inst.id)+"/translate.py"

def directupload_upload(inst, filename):
  return "qns/"+str(inst.id)+"/qset.tgz"


# Create your models here.
class Qns(models.Model):
  title=models.CharField(unique=True, max_length=50)
  description=models.TextField()
  # smalllimits are the limits for small set
  smalllimits=models.TextField()
  # needs 2 questions if true both large and small qns will show
  # otherwise only the small details will be used.
  need2questions=models.BooleanField(default=True)
  # need a translator script 
  # does the input need to go through a translator before comparison
  # with anssets ?
  needtranslator=models.BooleanField(default=False)

  # needs dos2unix. Does the input file need to be converted to 
  # unix format ?
  needdos2unix=models.BooleanField(default=True)
  # largelimits are the limits for small set
  usesuploadedqns=models.BooleanField(default=True)
  largelimits=models.TextField(null=True)
  inputexample=models.TextField() 
  outputexample=models.TextField() 
  # utimesmall the time allowed to upload the small solution
  utimesmall=models.IntegerField() 
  # utimelarge the time allowed to upload the large solution
  utimelarge=models.IntegerField(null=True) 
  # the files need to be uploaded after the first save!!!
  smallscript=models.FileField(upload_to=smallscript_upload, null=True)
  largescript=models.FileField(upload_to=largescript_upload, null=True)
  translatorscript=models.FileField(upload_to=translatorscript_upload, null=True)
  # number of questions uploaded so far (useful for numbering when you are 
  # uploading more questions.
  numqnsuploaded=models.IntegerField(default=0)
  # directly upload qnsets
  # file should have 2 subdirectories qns and ans and the files should be
  # numbered 1.txt 2.txt etc... The files will be repeated if they dont meet
  # the number requirements. Also they will overwrite existing ones if numbers
  # match
  directupload=models.FileField(upload_to=directupload_upload, null=True)
  difficulty=models.IntegerField(default=1)
  largescore=models.IntegerField(default=5)
  smallscore=models.IntegerField(default=2) 

# Create your models here.
class CodeTests(models.Model):
  testname=models.CharField(unique=True, max_length=50)
  start=models.DateTimeField()
  end=models.DateTimeField(null=True)
  duration=models.IntegerField()
  valid=models.BooleanField(default=True)
  # whether we are presently generating answer sets
  qnsgenerated=models.IntegerField(default=0)
  # NOTSTARTED, AWAITING, STARTED, DONE, ERRORED
  generationStatus=models.CharField(max_length=20, default="NOTSTARTED")

class CodeQnsList(models.Model):
  qn=models.ForeignKey(Qns)
  testid=models.ForeignKey(CodeTests)
  seq=models.IntegerField(default=0) 


