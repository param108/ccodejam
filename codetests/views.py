from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from coding.models import Qns
from forms import CodeTestForm
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

def edit(request,testid):
  if int(testid) < 0:
    return HttpResponseRedirect(reverse("tests:show")) 
  thistest = None
  try:
    thistest = CodeTests.objects.get(pk=int(testid))
  except:
    return HttpResponseRedirect(reverse("tests:show")) 
 
  qnlist = CodeQnsList.objects.filter(testid=thistest.id)
  notlist = CodeQnsList.objects.exclude(testid=thistest.id)

  if request.method == "GET":
    tform = CodeTestForm(initial={"testname":thistest.testname, "datetimefield":thistest.start, "duration":thistest.duration}) 
    return render(request, "codetests/codetests_edit.html",{"qlist": qnlist, "notqlist": notlist,
                                                            "tform": tform, "tid":testid,
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
  
  return render(request, "codetests/codetests_edit.html",{"qlist": qnlist, "notqlist": notlist,
                                                          "tform": tform, "tid":testid,
                                                          "base_url":settings.BASE_URL})


def addquestion(request, testid):
  pass
