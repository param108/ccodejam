from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse,HttpResponseNotFound
from coding.models import Qns
from forms import CodeTestForm,CodeQnForm
from models import CodeTests,CodeQnsList
import datetime
import os,time
from django.core.urlresolvers import reverse
from codejam import settings
from django.views.decorators.csrf import csrf_exempt
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
      print(qnform.cleaned_data["datetimefield"])
      newtest = CodeTests(testname = qnform.cleaned_data["testname"],
                        start = qnform.cleaned_data["datetimefield"],
                        duration = qnform.cleaned_data["duration"])
      newtest.end = newtest.start + datetime.timedelta(hours=newtest.duration)
      newtest.save()
      return HttpResponseRedirect(reverse("tests:edit",args=[newtest.id])) 
    except Exception,e:
      qnform.add_error(None, "Failed to save the test"+str(e));
      pass
  return render(request, "codetests/codetests_show.html",{"form": qnform, "tests": qns,
                                                          "base_url":settings.BASE_URL})

def questions(request):
  codeQnForm = CodeQnForm()
  if request.method == "POST":
    codeQnForm = CodeQnForm(request.POST, request.FILES)
    if codeQnForm.is_valid():
      try:
        qn = save_qn(codeQnForm)
        qn.save()
        qn.smallscript=request.FILES["smallscript"]
        qn.largescript=request.FILES["largescript"]
        qn.save()
        return HttpResponseRedirect(reverse("tests:questions")) 
      except Exception,e:
        if "smallscript" not  in request.FILES:
          codeQnForm.add_error(None,"both script files are mandatory")
        elif "largescript" not in request.FILES:
          codeQnForm.add_error(None,"both script files are mandatory")
        else:
          codeQnForm.add_error(None,"Failed to save the form:"+str(e))
        print("Failed to save question:"+str(e))
    else:
      print "QnForm failed"
      codeQnForm.add_error(None,"Form Has Errors"+str(e))
  qnlist = Qns.objects.all()
  return render(request, "codetests/codetests_addqn.html",{"qnlist": qnlist,
                                                          "form": codeQnForm })


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
    thistest.end = thistest.start + datetime.timedelta(hours=thistest.duration)
    try:
      thistest.save()
      return HttpResponseRedirect(reverse("tests:edit",args=[thistest.id])) 
    except:
      pass
  
  return render(request, "codetests/codetests_edit.html",{ "tform": tform, "tid":testid,
                                                           "base_url":settings.BASE_URL})
# _f_orm _g_et
def _fg(t,k):
  return t.cleaned_data[k] 
def update_qn(qn, qnform):
  qn.title=_fg(qnform,"title")
  qn.description=_fg(qnform,"description")
  qn.smalllimits=_fg(qnform,"smalllimits")
  qn.largelimits=_fg(qnform,"largelimits")
  qn.inputexample=_fg(qnform,"inputexample")
  qn.outputexample=_fg(qnform,"outputexample")
  qn.utimesmall=_fg(qnform,"utimesmall")
  qn.utimelarge=_fg(qnform,"utimelarge")
         #smallscript=rfiles["smallscript"],
         #largescript=rfiles["largescript"],
  qn.difficulty=_fg(qnform,"difficulty")
  return qn;
 
def save_qn(qnform):
  qn=Qns(title=_fg(qnform,"title"),
         description=_fg(qnform,"description"),
         smalllimits=_fg(qnform,"smalllimits"),
         largelimits=_fg(qnform,"largelimits"),
         inputexample=_fg(qnform,"inputexample"),
         outputexample=_fg(qnform,"outputexample"),
         utimesmall=_fg(qnform,"utimesmall"),
         utimelarge=_fg(qnform,"utimelarge"),
         #smallscript=rfiles["smallscript"],
         #largescript=rfiles["largescript"],
         difficulty=_fg(qnform,"difficulty"))
  return qn;
           
def copy_qn(qn):
  qn=CodeQnForm(initial={"title":qn.title,
         "description":qn.description,
         "smalllimits":qn.smalllimits,
         "largelimits":qn.largelimits,
         "inputexample":qn.inputexample,
         "outputexample":qn.outputexample,
         "utimesmall":qn.utimesmall,
         "utimelarge":qn.utimelarge,
         #smallscript:rfiles["qn.smallscript"],
         #largescript:rfiles["qn.largescript"],
         "difficulty":qn.difficulty})
  return qn
 
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
        qn = save_qn(codeQnForm)
        qn.save()
        qn.smallscript=request.FILES["smallscript"]
        qn.largescript=request.FILES["largescript"]
        qn.save()
        idx=CodeQnsList.objects.filter(testid=thistest).count()
        # add the new entry in the end
        qnentry = CodeQnsList(qn=qn,testid=thistest,seq=idx)
        qnentry.save()
        return HttpResponseRedirect(reverse("tests:addqns",args=[thistest.id])) 
      except Exception,e:
        if "smallscript" not  in request.FILES:
          codeQnForm.add_error(None,"both script files are mandatory")
        elif "largescript" not in request.FILES:
          codeQnForm.add_error(None,"both script files are mandatory")
        else:
          codeQnForm.add_error(None,"Failed to save the form:"+str(e))
        print("Failed to save question:"+str(e))
    else:
      print "QnForm failed"
      codeQnForm.add_error(None,"Form Has Errors"+str(e))
  qnlist = CodeQnsList.objects.filter(testid=thistest.id)
  notlist = Qns.objects.all()
  for qn in qnlist:
    notlist = notlist.exclude(pk=qn.qn.id)
  return render(request, "codetests/codetests_qns.html",{ "thetest": thistest, "qnlist": qnlist, "notlist":notlist,
                                                          "form": codeQnForm, "tid":thistest.id })

@csrf_exempt
def linkqn(request, testid):
  if int(testid) < 0:
    return HttpResponseRedirect(reverse("tests:show")) 
  thistest = None
  try:
    thistest = CodeTests.objects.get(pk=int(testid))
  except:
    return JsonResponse({"success":-1}) 
  qnid=0
  qn = None
  try:
    qnid = int(request.POST.get("qn"))
    qn = Qns.objects.get(pk=qnid)
  except:
    return JsonResponse({"success":-1}) 

  try:
    seq = CodeQnsList.objects.filter(testid=thistest).count()
    cqe = CodeQnsList(testid=thistest,qn=qn, seq=seq)
    cqe.save()
    return JsonResponse({"success":0}) 
  except:
    return JsonResponse({"success":-1}) 

@csrf_exempt
def unlinkqn(request, testid):
  if int(testid) < 0:
    return HttpResponseRedirect(reverse("tests:show")) 
  thistest = None
  try:
    thistest = CodeTests.objects.get(pk=int(testid))
  except:
    return JsonResponse({"success":-1}) 
  qnid=0
  qn = None
  try:
    qnid = int(request.POST.get("qn"))
    qn = Qns.objects.get(pk=qnid)
  except:
    return JsonResponse({"success":-1}) 
  try:
    CodeQnsList.objects.filter(testid=thistest).filter(qn=qn).delete()
    return JsonResponse({"success":0}) 
  except:
    return JsonResponse({"success":-1}) 

def delFile(p):
  try:
    os.remove(p)
  except:
    # do nothing if we cant delete it
    pass

def editqn(request, qnid):
  if int(qnid) < 0:
    return HttpResponseRedirect(reverse("tests:show")) 
  thisqn = None
  try:
    thisqn = Qns.objects.get(pk=int(qnid))
  except:
    return HttpResponseRedirect(reverse("tests:show")) 
  codeQnForm=None
  if request.method == "GET":
    codeQnForm = copy_qn(thisqn) 
  if request.method == "POST":
    codeQnForm=CodeQnForm(request.POST, request.FILES)
    if codeQnForm.is_valid():
      update_qn(thisqn,codeQnForm)
      # only update files if user uploaded new ones
      if "smallscript" in request.FILES:
        delFile(thisqn.smallscript.path)
        thisqn.smallscript = request.FILES["smallscript"]
        print thisqn.smallscript.path
      if "largescript" in request.FILES:
        delFile(thisqn.largescript.path)
        thisqn.largescript = request.FILES["largescript"]
        print thisqn.largescript.path
      try:
        thisqn.save()
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
      except Exception,e:
        codeQnForm.add_error(None,"Failed to update qn")
        print("Failed to update question:"+str(e))
  return render(request, "codetests/codetests_editqn.html",{ "theqn": thisqn,
                                                          "form": codeQnForm})

def viewfile(request, qnid, size):
  if size != "small" and size != "large":
    return HttpResponseNotFound("<h1>Not Found</h1>")
  if int(qnid) < 0:
    return HttpResponseNotFound("<h1>Not Found</h1>")
  thisqn = None
  try:
    thisqn = Qns.objects.get(pk=int(qnid))
  except:
    return HttpResponseNotFound("<h1>Not Found</h1>")
  if size == "small": 
    fp = thisqn.smallscript;
  else:
    fp = thisqn.largescript;
  try:
    fp.open();
    data = fp.read();
  except Exception,e:
    print("Failed to read %s script file:%s"%(size, str(e)))
    return HttpResponseNotFound("<h1>Not Found</h1>")
    
  title=size+" problem set file for question '"+thisqn.title+"'"
  return render(request,"codetests/simplefile.html",{"data": data,
                                                     "title":title})
   
