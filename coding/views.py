from django.shortcuts import render
from codetests.models import CodeTests,CodeQnsList
from models import TestAttempt,Answer
import os,time
from codejam import settings
import datetime
from django.utils.timezone import is_naive
import pytz
from django.http import JsonResponse
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
    smallans=Answer(testattempt=attempt, qn=qn.qn, attempt=1, qtype="small") 
    largeans=Answer(testattempt=attempt, qn=qn.qn, attempt=1, qtype="large") 
    smallans.save()
    largeans.save()
    ret[qnid].append(smallans)
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
    ret[qnid].append(largeans)
  return ret

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
    print "0 attempts"
    testattempt=TestAttempt(user=request.user, testid=thistest)
    testattempt.save()
    anslist = generate_answers(testattempt, qnlist)
  else:
    print "%d attempts"%(len(attempts))
    testattempt=attempts[0]
    anslist = get_answers(testattempt, qnlist)
  return render(request,"coding/coding_qnlist_show.html",{"base_url":settings.BASE_URL,
                                                      "anslist":anslist,
                                                      "qnlist":qnlist,
                                                      "attempt":testattempt})
                                    
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
  anslist = get_answers_from_qnid(thisattempt, qnidx) 
  if anslist[qnidx][0] == None or anslist[qnidx][1] == None:
    print("Invalid Answers")
    return HttpResponseRedirect(reverse(settings.BASE_URL+"/go/tests/")) 
    
  return render(request,"coding/coding_qn_show.html",{"base_url":settings.BASE_URL,
                                                      "anslist":anslist,
                                                      "qn":anslist[qnidx][0].qn,
                                                      "attempt":thisattempt}) 
