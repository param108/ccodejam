from django.shortcuts import render
from codetests.models import CodeTests,CodeQnsList
from models import TestAttempt,Answer
import os,time
from codejam import settings
import datetime
from django.utils.timezone import is_naive
import pytz
from django.http import JsonResponse,HttpResponse
from django.core.files import File
import subprocess
from forms import Solution
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
    largeans=Answer(testattempt=attempt, qn=qn.qn, qtype="large") 
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

def get_answers_from_qnid_size(attempt, qnid, size):
  answer = Answer.objects.filter(testattempt=attempt).filter(qn_id=qnid).filter(qtype=size)
  return answer[0]

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

def get_sol_files(ans, num):
  # files will be 1q (qns) 1a (soln)
  qnpath=settings.MEDIA_ROOT+"/solutions/"+str(ans.qn.id)+"/"+ans.qtype+"/"+str(num)+"q.txt"
  solpath=settings.MEDIA_ROOT+"/solutions/"+str(ans.qn.id)+"/"+ans.qtype+"/"+str(num)+"a.txt"
  with open(qnpath,'rb') as doc_file:
    ans.qnset.save("qns.txt",File(doc_file), save=True)
  with open(solpath,'rb') as doc_file:
    ans.solution.save("sol.txt",File(doc_file), save=True)
  ans.starttime = datetime.datetime.now(pytz.timezone(os.environ['TZ']))
  td = None
  if ans.qtype == "small":
    td = datetime.timedelta(minutes=ans.qn.utimesmall)
  else:
    td = datetime.timedelta(minutes=ans.qn.utimelarge)
  ans.endtime = ans.starttime +  td
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
  ans = get_answers_from_qnid_size(thisattempt, qnidx, size) 
  #get_sol_files(ans)  
  return render(request, "coding/coding_upload_files.html",{"base_url": settings.BASE_URL,
                                                            "ans":ans, "form":Solution()})

def dnload(request, ansid, size):
  if size != "small" and size != "large":
    return HttpResponseRedirect(reverse(settings.BASE_URL+"/go/tests/"))
  ansidx = int(ansid)
  if ansidx < 0:
    return HttpResponseRedirect(reverse(settings.BASE_URL+"/go/tests/")) 
  ans = None
  try:
    ans = Answer.objects.get(pk=ansidx)
  except Exception,e:
    print("Cant Find:"+str(e)) 
    return HttpResponseRedirect(reverse(settings.BASE_URL+"/go/tests/")) 
  if request.user != ans.testattempt.user:
    print("Invalid user")
    return HttpResponseRedirect(reverse(settings.BASE_URL+"/go/tests/")) 
  # FIXME should actually be a random number
  check = datetime.datetime.now(pytz.timezone(os.environ['TZ']))
  if not ans.endtime or check > ans.endtime:
    ans.attempt+=1
    get_sol_files(ans, 1)  
  ans.qnset.open()
  return HttpResponse(ans.qnset.read(),content_type="text/plain")

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
  ans.endtime= None
  ans.save()
  # timeout code is 2
  return  JsonResponse({"status": 2}) 

def check_if_pass(ans):
  rc = subprocess.check_call([setting.DIFF,ans.ans.path, ans.solution.path])   
  if rc == 0:
    ans.result="pass"
    ans.testattempt.score += 1
  else:
    ans.result="fail"

def uploadfile(request, ansid):
  ansidx = int(ansid)
  if ansidx < 0:
    return HttpResponseRedirect(reverse(settings.BASE_URL+"/go/tests/")) 
  ans = None
  try:
    ans = Answer.objects.get(pk=ansidx)
  except Exception,e:
    print("Cant Find:"+str(e)) 
    return HttpResponseRedirect(reverse(settings.BASE_URL+"/go/tests/")) 
  if request.user != ans.testattempt.user:
    print("Invalid user")
    return HttpResponseRedirect(reverse(settings.BASE_URL+"/go/tests/")) 
  # FIXME should actually be a random number
  check = datetime.datetime.now(pytz.timezone(os.environ['TZ']))
  if not ans.endtime or check > ans.endtime:
    return HttpResponseRedirect(settings.BASE_URL+"/go/uploadsolution/"+str(ans.testattempt.id)+"/"+str(ans.qn.id)+"/"+ans.qtype+"/")
  if request.method == "POST":
    solform = Solution(request.POST, request.FILES)
    if solform.is_valid(): 
      ans.ans = request.FILES["solution"]
      ans.codefile = request.FILES["code"]
      ans.save()
      check_if_pass(ans)
      ans.save()
  return HttpResponseRedirect(settings.BASE_URL+"/go/question/"+str(ans.testattempt.id)+"/"+str(ans.qn.id)+"/"+ans.qtype+"/")



