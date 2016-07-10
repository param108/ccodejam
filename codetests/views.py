from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from coding.models import Qns
from forms import CodeTestForm
from models import CodeTests
# Create your views here.
def show(request):
  if request.method == "GET":
    qns = CodeTests.objects.all();
    qnform = CodeTestForm() 
    return render(request, "codetests/codetests_show.html",{"form": qnform, "tests": qns})
  qnform = CodeTestForm(request.POST) 
  if qnform.is_valid():
    try:
      newtest = CodeTests(testname = qnform.cleaned_data["testname"],
                        datetimefield = qnform.cleaned_data["datetimefield"],
                        duration = qnform.cleaned_data["duration"])
      newtest.save()
      return HttpResponseRedirect(reverse("codetests:edit",[newtest.id])) 
    except:
      qnform.add_error(None, "Failed to save the test");
      pass
  return render(request, "codetests/codetests_show.html",{"form": qnform, "tests": qns})

def edit(request,testid):
  if int(testid) < 0:
    return HttpResponseRedirect(reverse("codetests:show")) 
  thistest = None
  try:
    thistest = CodeTests.objects.get(pk=int(testid))
  except:
    return HttpResponseRedirect(reverse("codetests:show")) 
 
  qnlist = CodeQnsList.objects.filter(testid=thistest.id)
  notlist = CodeQnsList.objects.exclude(testid=thistest.id)

  if request.method == "GET":
    tform = CodeTestForm(initial={"testname":thistest.testname, "datetimefield":thistest.datetimefield, "duration":this.test.duration}) 
    return render(request, "codetests/codetests_edit.html",{"qlist": qnlist, "notqlist": notlist,
                                                            "tform": tform, "tid":testid})
  # POST handling
  tform = CodeTestForm(request.POST)
  if tform.is_valid():
    thistest.testname = tform.cleaned_data["testname"]
    thistest.datetimefield = tform.cleaned_data["datetimefield"]
    thistest.duration = tform.cleaned_data["duration"]
    try:
      thistest.save()
      return HttpResponseRedirect(reverse("codetests:edit",[thistest.id])) 
    except:
      pass
  
  return render(request, "codetests/codetests_edit.html",{"qlist": qnlist, "notqlist": notlist,
                                                          "tform": tform, "tid":testid})


def addquestion(request, testid):
  pass
