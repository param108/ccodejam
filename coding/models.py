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
  
def qn_upload(inst, filename):
  return "ans/"+str(inst.user)+"/"+str(inst.qn)+"/"+inst.qtype+"/"+str(inst.attempt)+"/qn.txt"

def sol_upload(inst, filename):
  return "ans/"+str(inst.user)+"/"+str(inst.qn)+"/"+inst.qtype+"/"+str(inst.attempt)+"/sol.txt"

def ans_upload(inst, filename):
  return "ans/"+str(inst.user)+"/"+str(inst.qn)+"/"+inst.qtype+"/"+str(inst.attempt)+"/ans.txt"

def code_upload(inst, filename):
  outputname = ""
  if filename.endswith(".py"):
    outputname = "code.py"
  elif filename.endswith(".c"):
    outputname = "code.c"
  else:
    outputname = "code"
  return "ans/"+str(inst.user)+"/"+str(inst.qn)+"/"+inst.qtype+"/"+str(inst.attempt)+"/"+outputname

class Ans(models.Model):
  qn = models.ForeignKey(Qns)
  user = models.ForeignKey(User)
  # the random must be used to generate the question set.
  random = models.IntegerField()
  attempt = models.IntegerField()
  # after every 3 minutes for the small solution
  # and every 8 minutes for the large solution the qn set will change for a user.
  # i.e he will not be allowed to upload a solution.
  # he will need to download a new question set.
  starttime = models.DateTimeField(auto_now_add=True) # time at which download started 
  uploadtime = models.DateTimeField(auto_now_add=True, null=True) # time at which solution was received
  qnset = models.FileField(upload_to=qn_upload)
  # solution is the system generated answerfile
  solution = models.FileField(upload_to=sol_upload)
  # ans is the user uploaded answer file
  ans = models.FileField(upload_to=ans_upload, null=True)
  codefile = models.FileField(upload_to=code_upload, null=True)
  qtype = models.CharField(max_length=10, choices=(("small", "small"),("large", "large")), default="small")
  # based on the solution diff, we will post a pass or fail.  
  result = models.CharField(max_length=12,choices=(("pass", "pass"),("fail", "fail"),("unattempted", "unattempted")), default="unattempted")
  # based on running the code they have submitted
  coderesult = models.CharField(max_length=5, choices=(("pass", "pass"),("fail", "fail")), default="fail")
