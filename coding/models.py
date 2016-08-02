from __future__ import unicode_literals
from django.contrib.auth.models import User 
from django.db import models
from codetests.models import CodeTests,Qns

class UserLock(models.Model):
  userid = models.IntegerField(unique=True)
  cause= models.CharField(max_length=50)
  starttime = models.DateTimeField(auto_now_add=True) # time at which download started 

class UserLockDelete(models.Model):
  userid = models.IntegerField(unique=True)

class TestAttempt(models.Model):
  version= models.IntegerField(default=0)
  user = models.ForeignKey(User)
  testid=models.ForeignKey(CodeTests)
  start= models.DateTimeField(auto_now_add=True)
  score= models.IntegerField(default=0)

def qn_upload(inst, filename):
  return "ans/"+str(inst.testattempt.user.id)+"/"+str(inst.id)+"/"+inst.qtype+"/"+str(inst.attempt)+"/qn.txt"

def sol_upload(inst, filename):
  return "ans/"+str(inst.testattempt.user.id)+"/"+str(inst.id)+"/"+inst.qtype+"/"+str(inst.attempt)+"/sol.txt"

def ans_upload(inst, filename):
  return "ans/"+str(inst.testattempt.user.id)+"/"+str(inst.id)+"/"+inst.qtype+"/"+str(inst.attempt)+"/ans.txt"

def code_upload(inst, filename):
  outputname = ""
  if filename.endswith(".py"):
    outputname = "code.py"
  elif filename.endswith(".c"):
    outputname = "code.c"
  else:
    outputname = "code"
  return "ans/"+str(inst.testattempt.user.id)+"/"+str(inst.id)+"/"+inst.qtype+"/"+str(inst.attempt)+"/"+outputname


class Answer(models.Model):
  testattempt=models.ForeignKey(TestAttempt)
  qn = models.ForeignKey(Qns)
  # the random must be used to generate the question set.
  #random = models.IntegerField()
  attempt = models.IntegerField(default=0)
  # after every 3 minutes for the small solution
  # and every 8 minutes for the large solution the qn set will change for a user.
  # i.e he will not be allowed to upload a solution.
  # he will need to download a new question set.
  starttime = models.DateTimeField(null=True) # time at which download started 
  endtime = models.DateTimeField(null=True) # time by which he needs to upload
  uploadtime = models.DateTimeField(null=True) # time at which solution was received
  qnset = models.FileField(upload_to=qn_upload, null=True)
  # solution is the system generated answerfile
  solution = models.FileField(upload_to=sol_upload, null=True)
  # ans is the user uploaded answer file
  ans = models.FileField(upload_to=ans_upload, null=True)
  codefile = models.FileField(upload_to=code_upload, null=True)
  qtype = models.CharField(max_length=10, choices=(("small", "small"),("large", "large")), default="small")
  # based on the solution diff, we will post a pass or fail.  
  result = models.CharField(max_length=12,choices=(("pass", "pass"),("fail", "fail"),("unattempted", "unattempted"),("in-progress","in-progress")), default="unattempted")
  # based on running the code they have submitted
  coderesult = models.CharField(max_length=12, choices=(("pass", "pass"),("fail", "fail"),("unattempted","unattempted")), default="unattempted")
  solnum = models.IntegerField(default=0)

