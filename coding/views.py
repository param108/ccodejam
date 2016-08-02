from django.shortcuts import render
from codetests.models import CodeTests,CodeQnsList
from models import TestAttempt,Answer,UserLock,UserLockDelete
import os,time
from codejam import settings
import time,datetime
from django.utils.timezone import is_naive
from django.core.urlresolvers import reverse
import pytz
from django.http import JsonResponse,HttpResponse,HttpResponseRedirect
from django.core.files import File
import subprocess
from forms import Solution
import random

# Use only with "with" clause!!!
class Lock(object):
  def __init__(self, user, reason):
    self.user = user
    self.reason = reason
    self.lock_status = False
    self.lid = -1

  def __enter__(self):
    print "Entering:"+self.reason
    self.lock_user()
    return self

  def __exit__(self, type, value, tb):
    print "Exiting:"+self.reason
    self.unlock_user()

  def unlock_user(self):
    if self.lid > 0:
      lid = self.lid
      self.lid= -1
      u = UserLock.objects.filter(pk=lid)
      if len(u):
        try:
          if u[0].userid == self.user.id:
            u[0].delete()
            self.lock_status = False
          else:
            print "Trying to  DELETE wrong user!!!:"+str(u[0].id)+":"+str(self.user.id)
          return
        except:
          print "FAILURE TO DELETE LOCK!!!!"
      print "FAILURE TO FIND LOCK!!!!"

  def locked(self):
    return self.lock_status
  # returns True if locked False if not locked
  # returns the lock id in lock object
  def lock_user(self):
    u = None
    ud = None
    # try and get user lock
    try:
      u = UserLock(userid=self.user.id, cause=self.reason)
      u.save()
      self.lid = u.id
      self.lock_status = True
      return True
    except Exception,e:
      print ("Failed to Lock!!!!:"+ str(e))

    #get the lock delete lock
    try:
      ud = UserLockDelete(userid=self.user.id)
      ud.save()
    except Exception,e:
      print ("Failed to get Lock Delete!!!!"+str(e))
      return False

    u = UserLock.objects.filter(userid=self.user.id)
    try:
      # check if this is a stale lock
      if len(u):
        check = datetime.datetime.now(pytz.timezone(os.environ['TZ']))
        tdelta = check - u[0].starttime 
        if tdelta.total_seconds() > 30:
          print ("Force deleting: "+u[0].cause+" by "+self.reason)
          u[0].delete()
    except Exception,e:
      print ("Failed to Delete!!!!"+str(e))
  
    # remember to unlock the delete lock
    ud.delete()

    # fail anyway!
    return False 

# Create your views here.
def testpage(request):
  os.environ['TZ']="Asia/Kolkata"
  time.tzset()
  check = datetime.datetime.now(pytz.timezone(os.environ['TZ']))
  # valid optimizes the number of records retrieved by
  # avoiding tests have ended already
  tests = CodeTests.objects.filter(end__gte=check).filter(start__lte=check);
  resume={}
  for testid in tests:
    attempts = TestAttempt.objects.filter(user=request.user).filter(testid=testid).count()
    if attempts > 0:
      resume[testid.id]="Resume"
    else:
      resume[testid.id]="Start"

  if request.method == "GET":
    return render(request, "coding/coding_tests.html",{"tests": tests, 
      "base_url":settings.BASE_URL,
      "resume":resume})
  return HttpResponseRedirect(settings.BASE_URL+"/go/tests/")

def generate_answers(attempt, qnlist):
  ret={}
  for qn in qnlist:
    qnid = qn.qn.id
    ret[qnid]=[]
    smallans=Answer(testattempt=attempt, qn=qn.qn, qtype="small") 
    smallans.save()
    ret[qnid].append(smallans)
    if qn.qn.need2questions:
      largeans=Answer(testattempt=attempt, qn=qn.qn, qtype="large") 
      largeans.save()
      ret[qnid].append(largeans)
  return ret

def get_answers(attempt, qnlist):
  ret={}
  for qn in qnlist:
    qnid = qn.qn.id
    ret[qnid]=[]
    answers = Answer.objects.filter(testattempt=attempt).filter(qn=qn.qn) 
    smallans = None
    largeans = None
    for ans in answers:
      if ans.qtype=="small":
        smallans=ans
      else:
        largeans=ans
    ret[qnid].append(smallans)
    if qn.qn.need2questions:
      ret[qnid].append(largeans)
  return ret

def get_answers_from_qnid_size(attempt, qnid, size):
  answer = Answer.objects.filter(testattempt=attempt).filter(qn_id=qnid).filter(qtype=size)
  if len(answer) == 1:
    return answer[0]
  return None

def get_answers_from_qnid(attempt, qnid):
  ret={}
  ret[qnid]=[]
  answers = Answer.objects.filter(testattempt=attempt).filter(qn_id=qnid) 
  smallans = None
  largeans = None
  for ans in answers:
    if ans.qtype=="small":
      smallans=ans
    else:
      largeans=ans
  ret[qnid].append(smallans)
  # the smallans should exist and its question is the same as the large set
  if smallans.qn.need2questions:
    ret[qnid].append(largeans)
  return ret

def starttest(request,testid):
  if int(testid) < 0:
    return HttpResponseRedirect(reverse(settings.BASE_URL+"/go/tests/")) 
  thistest = None
  try:
    thistest = CodeTests.objects.get(pk=int(testid))
  except Exception,e:
    print("Cant Find:"+str(e)) 
    return HttpResponseRedirect(reverse(settings.BASE_URL+"/go/tests/")) 


  attempts = TestAttempt.objects.filter(user=request.user).filter(testid=testid)
  testattempt = None
  qnlist=CodeQnsList.objects.filter(testid=thistest)
  anslist = None
  if len(attempts) == 0:
    with Lock(request.user,"generation") as lock:
      if not lock.locked():
        return render(request,"coding/user_locked.html", {
                                           "return":reverse("go:start",
                                                      args=[testid])}) 
      attempts = TestAttempt.objects.filter(user=request.user).filter(testid=testid)
      if len(attempts) == 0:
        testattempt=TestAttempt(user=request.user, testid=thistest)
        testattempt.save()
        anslist = generate_answers(testattempt, qnlist)
    # locked till here
  else:
    testattempt=attempts[0]
    if not updateAnsStatus(request.user, testattempt):
      return render(request,"coding/user_locked.html", {
                                           "return":reverse("go:start",
                                                      args=[testid])}) 
    anslist = get_answers(testattempt, qnlist)
  return render(request,"coding/coding_qnlist_show.html",{"base_url":settings.BASE_URL,
                                                      "anslist":anslist,
                                                      "qnlist":qnlist,
                                                      "attempt":testattempt,
                                          "return":reverse("go:tests")})
                                    
def timeremaining(request, testid):
  if int(testid) < 0:
    return  JsonResponse({"status": -1}) 
  thistest = None
  try:
    thistest = CodeTests.objects.get(pk=int(testid))
  except Exception,e:
    print("Cant Find:"+str(e)) 
    return  JsonResponse({"status": -1}) 
  check = datetime.datetime.now(pytz.timezone(os.environ['TZ']))
  if check < thistest.end:
    td = thistest.end - check
    totalsecs = td.total_seconds()
    hrs = totalsecs/3600
    secs = totalsecs%3600
    mins = secs/60
    secs = secs % 60
    timestr="%02d:%02d:%02d"%(hrs, mins, secs)
    return JsonResponse({"status":0,
                         "time":timestr});
  return  JsonResponse({"status": -1}) 

def showquestion(request, attemptid, qnid):
  qnidx = int(qnid)
  attemptidx = int(attemptid)
  if attemptidx < 0:
    return HttpResponseRedirect(reverse(settings.BASE_URL+"/go/tests/")) 
  thisattempt = None
  try:
    thisattempt = TestAttempt.objects.get(pk=attemptidx)
  except Exception,e:
    print("Cant Find:"+str(e)) 
    return HttpResponseRedirect(reverse(settings.BASE_URL+"/go/tests/")) 
  if request.user != thisattempt.user:
    print("Invalid user")
    return HttpResponseRedirect(reverse(settings.BASE_URL+"/go/tests/")) 

  if not updateAnsStatus(request.user, thisattempt):
    return render(request,"coding/user_locked.html", {
                                         "return":reverse("go:start",
                                                    args=[thisattempt.testid.id])}) 
 
  anslist = get_answers_from_qnid(thisattempt, qnidx) 
  if anslist[qnidx][0] == None:
    print("Invalid Answers")
    return HttpResponseRedirect(reverse(settings.BASE_URL+"/go/tests/")) 
  return render(request,"coding/coding_qn_show.html",{"base_url":settings.BASE_URL,
                                                      "anslist":anslist,
                                                      "qn":anslist[qnidx][0].qn,
                                                      "attempt":thisattempt,
                                           "return":reverse("go:start",
                                                      args=[thisattempt.testid.id])}) 

def get_new_sol_files(ans, num):
  # files will be 1q (qns) 1a (soln)
  # qnpath=settings.MEDIA_ROOT+"/solutions/"+str(ans.testattempt.testid.id)+"/"+str(ans.qn.id)+"/"+ans.qtype+"/"+str(num)+"q.txt"
  # solpath=settings.MEDIA_ROOT+"/solutions/"+str(ans.testattempt.testid.id)+"/"+str(ans.qn.id)+"/"+ans.qtype+"/"+str(num)+"a.txt"
  # with open(qnpath,'rb') as doc_file:
  #   ans.qnset.save("qns.txt",File(doc_file), save=True)
  # with open(solpath,'rb') as doc_file:
  #   ans.solution.save("sol.txt",File(doc_file), save=True)
  ans.solnum = num
  ans.starttime = datetime.datetime.now(pytz.timezone(os.environ['TZ']))
  td = None
  if ans.qtype == "small":
    td = datetime.timedelta(minutes=ans.qn.utimesmall)
  else:
    td = datetime.timedelta(minutes=ans.qn.utimelarge)
  ans.endtime = ans.starttime +  td
  ans.result="in-progress"
  ans.save()

def upload(request, attemptid, qnid, size):
  if size != "small" and size != "large":
    return HttpResponseRedirect(reverse(settings.BASE_URL+"/go/tests/"))
  qnidx = int(qnid)
  attemptidx = int(attemptid)
  if attemptidx < 0:
    return HttpResponseRedirect(reverse(settings.BASE_URL+"/go/tests/")) 
  thisattempt = None
  try:
    thisattempt = TestAttempt.objects.get(pk=attemptidx)
  except Exception,e:
    print("Cant Find:"+str(e)) 
    return HttpResponseRedirect(reverse(settings.BASE_URL+"/go/tests/")) 
  if request.user != thisattempt.user:
    print("Invalid user")
    return HttpResponseRedirect(reverse(settings.BASE_URL+"/go/tests/")) 
  if not updateAnsStatus(request.user, thisattempt):
    return render(request,"coding/user_locked.html", {
                                         "return":reverse("go:start",
                                                    args=[thisattempt.testid.id])}) 
  ans = get_answers_from_qnid_size(thisattempt, qnidx, size) 
  if not ans:
    return HttpResponseRedirect(reverse(settings.BASE_URL+"/go/tests/"))
  if ans.result=="pass":
    return HttpResponseRedirect(reverse("go:qn", args=[str(ans.testattempt.id),
                                                       str(ans.qn.id)])) 

  if request.method == "GET":
    return render(request, "coding/coding_upload_files.html",{"base_url": settings.BASE_URL,
                                                            "ans":ans, "form":Solution(),
                                                            "return":reverse("go:qn", 
                                                               args=[str(ans.testattempt.id),
                                                               str(ans.qn.id)])})

def dnload(request, ansid, size):
  if size != "small" and size != "large":
    return HttpResponseRedirect(reverse(settings.BASE_URL+"/go/tests/"))
  ansidx = int(ansid)
  if ansidx < 0:
    return HttpResponseRedirect(reverse(settings.BASE_URL+"/go/tests/")) 
  ans = None
  with Lock(request.user, "dnload") as lock:
    try:
      ans = Answer.objects.get(pk=ansidx)
    except Exception,e:
      print("Cant Find:"+str(e)) 
      return HttpResponseRedirect(reverse(settings.BASE_URL+"/go/tests/")) 
    if request.user != ans.testattempt.user:
      print("Invalid user")
      return HttpResponseRedirect(reverse(settings.BASE_URL+"/go/tests/")) 
    if not lock.locked():
      return render(request,"coding/user_locked.html", {
                                         "return":reverse("go:start",
                                         args=[ans.testattempt.testid.id])}) 
    check = datetime.datetime.now(pytz.timezone(os.environ['TZ']))
    if not ans.endtime or check > ans.endtime:
      ans.attempt+=1
      random.seed()
      r = random.randint(1,ans.testattempt.testid.qnsgenerated)
      get_new_sol_files(ans, r)  
    # locked till here
  qnpath=settings.MEDIA_ROOT+"/solutions/"+str(ans.testattempt.testid.id)+"/"+str(ans.qn.id)+"/"+ans.qtype+"/"+str(ans.solnum)+"q.txt"
  #ans.qnset.open()
  fp = open(qnpath,'r')
  return HttpResponse(fp.read(),content_type="text/plain")

def updateAnsStatus(user, attempt):
  for ans in Answer.objects.filter(testattempt=attempt).filter(result="in-progress"):
    with Lock(user, "updateAnsStatus") as lock:
      if lock.locked():
        answers = Answer.objects.filter(pk=ans.id)
        if len(answers):
          check = datetime.datetime.now(pytz.timezone(os.environ['TZ']))
          if not ans.endtime or check > ans.endtime:
            ans.result = "fail"
            ans.attempt += 1
            ans.endtime = None
            ans.save()
        return True
      return False
  return True
      
 
def uploadtime(request, ansid):
  ansidx = int(ansid)
  if ansidx < 0:
    return  JsonResponse({"status": -1}) 
  ans = None
  try:
    ans = Answer.objects.get(pk=ansidx)
  except Exception,e:
    print("Cant Find:"+str(e)) 
    return  JsonResponse({"status": -1}) 
  if not ans.endtime:
    return  JsonResponse({"status": -1}) 
  
  check = datetime.datetime.now(pytz.timezone(os.environ['TZ']))
  if check < ans.endtime:
    td = ans.endtime - check
    totalsecs = td.total_seconds()
    mins = totalsecs/60
    secs = totalsecs % 60
    timestr="%02d:%02d"%(mins, secs)
    return JsonResponse({"status":0,
                         "time":timestr,
                         "attemptnum":ans.attempt});
 # timeout code is 2
  return  JsonResponse({"status": 2}) 

def check_if_pass(ans):
  solpath=settings.MEDIA_ROOT+"/solutions/"+str(ans.testattempt.testid.id)+"/"+str(ans.qn.id)+"/"+ans.qtype+"/"+str(ans.solnum)+"a.txt"
  try:
    if ans.qn.needdos2unix:
      rc = subprocess.check_call([settings.PYTHON, settings.DOS2UNIX,ans.ans.path])   
    if ans.qn.needtranslator:
      rc = subprocess.check_call([settings.PYTHON, ans.qn.translatorscript.path,ans.ans.path])   
    rc = subprocess.check_call([settings.DIFF,ans.ans.path, solpath])   
  except:
    rc = 1

  if rc == 0:
    ans.result="pass"
    if ans.qtype == "small":
      ans.testattempt.score += ans.qn.smallscore
    elif ans.qtype == "large":
      ans.testattempt.score += ans.qn.largescore
    return True
  else:
    ans.result="fail"
    return False

def uploadfile(request, ansid):
  ansidx = int(ansid)
  if ansidx < 0:
    return HttpResponseRedirect(reverse(settings.BASE_URL+"/go/tests/")) 
  ans = None
  with Lock(request.user, "uploadfile") as lock:
    try:
      ans = Answer.objects.get(pk=ansidx)
    except Exception,e:
      print("Cant Find:"+str(e)) 
      return HttpResponseRedirect(reverse(settings.BASE_URL+"/go/tests/")) 
    if request.user != ans.testattempt.user:
      print("Invalid user")
      return HttpResponseRedirect(reverse(settings.BASE_URL+"/go/tests/")) 
 
    if ans.result == "pass":
      return HttpResponseRedirect(settings.BASE_URL+"/go/question/"+str(ans.testattempt.id)+"/"+str(ans.qn.id)+"/"+ans.qtype+"/")
    # need the testid for the warning page so moving it here
    if request.method == "POST":
      if not lock.locked():
        return render(request,"coding/user_locked.html", {
                                     "return":reverse("go:start",
                                     args=[ans.testattempt.testid.id])}) 
 
      check = datetime.datetime.now(pytz.timezone(os.environ['TZ']))
      if not ans.endtime or check > ans.endtime:
        solform.add_error(None,"Time Out: Please Reload and Try again. Please note the input file will change on Reload")
        return render(request, "coding/coding_upload_files.html",{"base_url": settings.BASE_URL,
                                                            "ans":ans, "form":solform,
                                                            "return":reverse("go:qn", 
                                                               args=[str(ans.testattempt.id),
                                                               str(ans.qn.id)])})
      solform = Solution(request.POST, request.FILES)
      if solform.is_valid(): 
        ans.uploadtime=check
        ans.ans = request.FILES["solution"]
        ans.codefile = request.FILES["code"]
        ans.save()
        if check_if_pass(ans):
          ans.testattempt.save()
        ans.save()
      else:
        return render(request, "coding/coding_upload_files.html",{"base_url": settings.BASE_URL,
                                                            "ans":ans, "form":solform,
                                                            "return":reverse("go:qn", 
                                                               args=[str(ans.testattempt.id),
                                                               str(ans.qn.id)])})
  return HttpResponseRedirect(settings.BASE_URL+"/go/question/"+str(ans.testattempt.id)+"/"+str(ans.qn.id)+"/"+ans.qtype+"/")



