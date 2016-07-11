from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from coding.models import Qns
from forms import CodeTestForm,CodeQnForm
from models import CodeTests,CodeQnsList
import datetime
import os,time
from django.core.urlresolvers import reverse
from codejam import settings
# Create your views here.
def show(request):
  os.environ['TZ']="Asia/Kolkata"
  time.tzset()
  qns = CodeTests.objects.all();
  if request.method == "GET":
    qnform = CodeTestForm(initial={'datetimefield':datetime.datetime.now()})
    return render(request, "codetests/codetests_show.html",{"form": qnform, "tests": qns})
  qnform = CodeTestForm(request.POST) 
  if qnform.is_valid():
    try:
      newtest = CodeTests(testname = qnform.cleaned_data["testname"],
                        start = qnform.cleaned_data["datetimefield"],
                        duration = qnform.cleaned_data["duration"])
      newtest.save()
      return HttpResponseRedirect(reverse("tests:edit",args=[newtest.id])) 
    except Exception,e:
      qnform.add_error(None, "Failed to save the test"+str(e));
      pass
  return render(request, "codetests/codetests_show.html",{"form": qnform, "tests": qns,
                                                          "base_url":settings.BASE_URL})
def delete(request,testid):
  # we are going back to show to avoid an infinite redirect loop
  # to edit
  if int(testid) < 0:
    return HttpResponseRedirect(reverse("tests:show")) 
  thistest = None
  try:
    thistest = CodeTests.objects.get(pk=int(testid))
  except Exception,e:
    print("Cant Find:"+str(e)) 
    return HttpResponseRedirect(reverse("tests:show")) 
  try:
    thistest.delete()
  except Exception,e:
    print("Cant Delete:"+str(e)) 
  return HttpResponseRedirect(reverse("tests:show")) 
 
def edit(request,testid):
  if int(testid) < 0:
    return HttpResponseRedirect(reverse("tests:show")) 
  thistest = None
  try:
    thistest = CodeTests.objects.get(pk=int(testid))
  except:
    return HttpResponseRedirect(reverse("tests:show")) 
 
  if request.method == "GET":
    tform = CodeTestForm(initial={"testname":thistest.testname, "datetimefield":thistest.start, "duration":thistest.duration}) 
    return render(request, "codetests/codetests_edit.html",{ "form": tform, "tid":testid,
                                                             "base_url":settings.BASE_URL})
  # POST handling
  tform = CodeTestForm(request.POST)
  if tform.is_valid():
    thistest.testname = tform.cleaned_data["testname"]
    thistest.start = tform.cleaned_data["datetimefield"]
    thistest.duration = tform.cleaned_data["duration"]
    try:
      thistest.save()
      return HttpResponseRedirect(reverse("tests:edit",[thistest.id])) 
    except:
      pass
  
  return render(request, "codetests/codetests_edit.html",{ "tform": tform, "tid":testid,
                                                           "base_url":settings.BASE_URL})
# _f_orm _g_et
def _fg(t,k):
  return t.cleaned_data[k] 

def saveqn(qnform, t, rfiles):
  qn=Qns(title=_fg(t,"title"),
         description=_fg(t,"description"),
         smalllimits=_fg(t,"smalllimits"),
         largelimits=_fg(t,"largelimits"),
         inputexample=_fg(t,"inputexample"),
         outputexample=_fg(t,"outputexample"),
         utimesmall=_fg(t,"utimesmall"),
         utimelarge=_fg(t,"utimelarge"),
         smallscript=rfiles["smallscript"],
         largescript=rfiles["largescript"],
         difficulty=_fg(t,"difficulty"))
  return qn;
           
def addqns(request, testid):
  if int(testid) < 0:
    return HttpResponseRedirect(reverse("tests:show")) 
  thistest = None
  try:
    thistest = CodeTests.objects.get(pk=int(testid))
  except:
    return HttpResponseRedirect(reverse("tests:show")) 
 
  codeQnForm = CodeQnForm()
  if request.method == "POST":
    codeQnForm = CodeQnForm(request.POST, request.FILES)
    if codeQnForm.is_valid():
      try:
        qn = save_qn(codeQnForm,thistest, request.FILES)
        q.save()
        idx=CodeQnsList.objects.filter(testid=thistest)
        # add the new entry in the end
        qnentry = CodeQnsList(qn=qn,testid=thistest,seq=len(idx))
        qnentry.save()
        return HttpResponseRedirect(reverse("tests:addqns",[thistest.id])) 
      except Exception,e:
        codeQnForm.add_error(None,"Failed to save the form:"+str(e))
        print("Failed to save question:"+str(e))
  qnlist = CodeQnsList.objects.filter(testid=thistest.id)
  notlist = CodeQnsList.objects.exclude(testid=thistest.id)
  return render(request, "codetests/codetests_qns.html",{ "qnlist": qnlist, "notlist":notlist,
                                                          "form": codeQnForm })

