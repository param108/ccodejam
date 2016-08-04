from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse,HttpResponseNotFound
from models import Qns
from forms import CodeTestForm,CodeQnForm,GenerateForm
from models import CodeTests,CodeQnsList
import datetime
import os,time
from django.core.urlresolvers import reverse
from codejam import settings
import subprocess, re
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required

# Create your views here.
@staff_member_required
def show(request):
  os.environ['TZ']="Asia/Kolkata"
  time.tzset()
  qns = CodeTests.objects.all();
  if request.method == "GET":
    qnform = CodeTestForm(initial={'datetimefield':datetime.datetime.now()})
    return render(request, "codetests/codetests_show.html",{"form": qnform, "tests": qns,
                                                            "base_url":settings.BASE_URL})
  qnform = CodeTestForm(request.POST) 
  if qnform.is_valid():
    try:
      print(qnform.cleaned_data["datetimefield"])
      hidden = False
      if "hidden" in qnform.cleaned_data:
        hidden = True
      newtest = CodeTests(testname = qnform.cleaned_data["testname"],
                        start = qnform.cleaned_data["datetimefield"],
                        duration = qnform.cleaned_data["duration"],
                        hidden = hidden)
      newtest.end = newtest.start + datetime.timedelta(hours=newtest.duration)
      newtest.save()
      return HttpResponseRedirect(reverse("tests:edit",args=[newtest.id])) 
    except Exception,e:
      qnform.add_error(None, "Failed to save the test"+str(e));
      pass
  return render(request, "codetests/codetests_show.html",{"form": qnform, "tests": qns,
                                                          "base_url":settings.BASE_URL})

# accesses the direct upload tgz archive and populates the qns and ans
def updateDirectUpload(qn):
  if qn.usesuploadedqns:
    print "updateDirectUpload:"+qn.directupload.path
    if os.path.exists(qn.directupload.path):
      try:
        subprocess.check_call([settings.PYTHON, settings.DIRECTUPLOAD, settings.TAR, qn.directupload.path, "%s/qns/%d/qnset/"%(settings.MEDIA_ROOT,qn.id)])
        delFile(qn.directupload.path) 
      except:
        pass
    qn.numqnsuploadedsmall=renumberDirectUploads(qn, "small")
    if qn.need2questions:
      qn.numqnsuploadedlarge=renumberDirectUploads(qn, "large")
    qn.save()

def renumberfiles(present):
  idx = 1
  sorted_present = sorted(present) 
  for i in sorted_present:
    if idx != i:
      subprocess.check_call(["mv","%dq.txt"%(i), "%dq.txt"%(idx)])
      subprocess.check_call(["mv","%da.txt"%(i), "%da.txt"%(idx)])
    idx+=1

def renumberDirectUploads(qn, qtype):
  os.chdir("%s/qns/%d/qnset/%s"%(settings.MEDIA_ROOT,qn.id,qtype))
  files = os.listdir(".")
  print files
  getqns = re.compile('([0-9]+)q[.]txt')
  numqns=0
  present = []
  for f in files:
    m = getqns.match(f)
    if m:
      if os.path.exists(f.replace("q","a")):
        numqns+=1 
        present.append(int(m.group(1)))
      else:
        # if the 'a' doesnt exist for a 'q' delete it
        delFile(f)
  print str(present)
  renumberfiles(present)    
  return len(present)

@staff_member_required
def questions(request):
  codeQnForm = CodeQnForm()
  if request.method == "POST":
    codeQnForm = CodeQnForm(request.POST, request.FILES)
    if codeQnForm.is_valid():
      try:
        qn = save_qn(codeQnForm)
        qn.save()
        if "smallscript" in request.FILES:
          try:
            delFile(qn.smallscript.path)
          except:
            pass
          qn.smallscript = request.FILES["smallscript"]
        if "largescript" in request.FILES:
          try:
            delFile(qn.largescript.path)
          except:
            pass
          qn.largescript = request.FILES["largescript"]
        if "translatorscript" in request.FILES:
          try:
            delFile(qn.translatorscript.path)
          except:
            pass
          qn.translatorscript= request.FILES["translatorscript"]
        directupload = False
        if "directupload" in request.FILES:
          try:
            delFile(qn.directupload.path)
          except:
            pass
          qn.directupload= request.FILES["directupload"]
          directupload = True
        qn.save()
        if directupload:
          updateDirectUpload(qn)
        return HttpResponseRedirect(reverse("tests:questions")) 
      except Exception,e:
        codeQnForm.add_error(None,"Failed to save the form:"+str(e))
        print("Failed to save question:"+str(e))
    else:
      print "QnForm failed"
      codeQnForm.add_error(None,"Form Has Errors")
  qnlist = Qns.objects.all()
  return render(request, "codetests/codetests_addqn.html",{"qnlist": qnlist,
                                                          "form": codeQnForm,
                                                          "base_url":settings.BASE_URL})


@staff_member_required
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
 
@staff_member_required
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
  if k in t.cleaned_data:
    return t.cleaned_data[k] 
  else:
    # for boolean fields, not present is False
    return False
def update_qn(qn, qnform):
  qn.title=_fg(qnform,"title")
  qn.description=_fg(qnform,"description")
  qn.need2questions=_fg(qnform,"need2questions")
  qn.needtranslator=_fg(qnform,"needtranslator")
  qn.needdos2unix=_fg(qnform,"needdos2unix")
  qn.usesuploadedqns=_fg(qnform,"usesuploadedqns")
  qn.smalllimits=_fg(qnform,"smalllimits")
  qn.largelimits=_fg(qnform,"largelimits")
  qn.inputexample=_fg(qnform,"inputexample")
  qn.outputexample=_fg(qnform,"outputexample")
  qn.utimesmall=_fg(qnform,"utimesmall")
  qn.language=_fg(qnform,"language")
  qn.utimelarge=_fg(qnform,"utimelarge")
  qn.largescore=_fg(qnform,"largescore")
  qn.smallscore=_fg(qnform,"smallscore")
         #smallscript=rfiles["smallscript"],
         #largescript=rfiles["largescript"],
  qn.difficulty=_fg(qnform,"difficulty")
  return qn;
 
def save_qn(qnform):
  qn=Qns(title=_fg(qnform,"title"),
         need2questions=_fg(qnform,"need2questions"),
         needtranslator=_fg(qnform,"needtranslator"),
         needdos2unix=_fg(qnform,"needdos2unix"),
         usesuploadedqns=_fg(qnform,"usesuploadedqns"),
         description=_fg(qnform,"description"),
         smalllimits=_fg(qnform,"smalllimits"),
         largelimits=_fg(qnform,"largelimits"),
         inputexample=_fg(qnform,"inputexample"),
         outputexample=_fg(qnform,"outputexample"),
         utimesmall=_fg(qnform,"utimesmall"),
         utimelarge=_fg(qnform,"utimelarge"),
         largescore=_fg(qnform,"largescore"),
         smallscore=_fg(qnform,"smallscore"),
         language=_fg(qnform,"language"),
         #smallscript=rfiles["smallscript"],
         #largescript=rfiles["largescript"],
         difficulty=_fg(qnform,"difficulty"))
  return qn;
           
def copy_qn(qn):
  qn=CodeQnForm(initial={"title":qn.title,
         "need2questions":qn.need2questions,
         "needtranslator":qn.needtranslator,
         "usesuploadedqns":qn.usesuploadedqns,
         "needdos2unix":qn.needdos2unix,
         "description":qn.description,
         "smalllimits":qn.smalllimits,
         "largelimits":qn.largelimits,
         "inputexample":qn.inputexample,
         "outputexample":qn.outputexample,
         "utimesmall":qn.utimesmall,
         "language":qn.language,
         "largescore":qn.largescore,
         "smallscore":qn.smallscore,
         #smallscript:rfiles["qn.smallscript"],
         #largescript:rfiles["qn.largescript"],
         "difficulty":qn.difficulty})
  return qn
 
@staff_member_required
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
        if "smallscript" in request.FILES:
          try:
            delFile(qn.smallscript.path)
          except:
            pass
          qn.smallscript = request.FILES["smallscript"]
        if "largescript" in request.FILES:
          try:
            delFile(qn.largescript.path)
          except:
            pass
          qn.largescript = request.FILES["largescript"]
        if "translatorscript" in request.FILES:
          try:
            delFile(qn.translatorscript.path)
          except:
            pass
          qn.translatorscript= request.FILES["translatorscript"]
        directupload = False
        if "directupload" in request.FILES:
          try:
            delFile(qn.directupload.path)
          except:
            pass
          qn.directupload= request.FILES["directupload"]
          directupload = True
        qn.save()
        if directupload:
          updateDirectUpload(qn)
        idx=CodeQnsList.objects.filter(testid=thistest).count()
        # add the new entry in the end
        qnentry = CodeQnsList(qn=qn,testid=thistest,seq=idx)
        qnentry.save()
        return HttpResponseRedirect(reverse("tests:addqns",args=[thistest.id])) 
      except Exception,e:
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
                                                          "form": codeQnForm, "tid":thistest.id,
                                                          "base_url":settings.BASE_URL})

@staff_member_required
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

@staff_member_required
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

@staff_member_required
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
        try:
          delFile(thisqn.smallscript.path)
        except:
          pass
        thisqn.smallscript = request.FILES["smallscript"]
      if "largescript" in request.FILES:
        try:
          delFile(thisqn.largescript.path)
        except:
          pass
        thisqn.largescript = request.FILES["largescript"]
      if "translatorscript" in request.FILES:
        try:
          delFile(thisqn.translatorscript.path)
        except:
          pass
        thisqn.translatorscript= request.FILES["translatorscript"]
      directupload = False
      if "directupload" in request.FILES:
        try:
          delFile(thisqn.directupload.path)
        except:
          pass
        thisqn.directupload= request.FILES["directupload"]
        directupload = True
      try:
        thisqn.save()
        if directupload:
          updateDirectUpload(thisqn)
        return HttpResponseRedirect(reverse("tests:questions"))
      except Exception,e:
        codeQnForm.add_error(None,"Failed to update qn")
        print("Failed to update question:"+str(e))
  return render(request, "codetests/codetests_editqn.html",{ "theqn": thisqn,
                                                          "form": codeQnForm,
                                                          "base_url":settings.BASE_URL}) 

@staff_member_required
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
                                                     "title":title,
                                                     "base_url":settings.BASE_URL}) 
   
@staff_member_required
def generate(request, testid):
  thistest = None
  try:
    thistest = CodeTests.objects.get(pk=int(testid))
  except:
    return HttpResponseRedirect(reverse("tests:show")) 
  if thistest.generationStatus != "NOTSTARTED" and thistest.generationStatus != "ERRORED" and thistest.generationStatus != "DONE": 
    return HttpResponseRedirect(reverse("tests:show")) 
  if request.method=="GET":
    gen = GenerateForm()
    return render(request,"codetests/generate.html", {"form": gen, "tid": testid, 
                                                      "thetest":thistest,
                                                      "base_url":settings.BASE_URL}) 
  if request.method=="POST":
    gen = GenerateForm(request.POST)
    if gen.is_valid():
      if gen.cleaned_data["numqns"] > 0:
        thistest.qnsgenerated=gen.cleaned_data["numqns"]
        thistest.generationStatus="AWAITING"
        thistest.save()
        return HttpResponseRedirect(reverse("tests:show")) 
      else:
        gen.add_error("numqns","Must be a positive number")
    return render(request,"codetests/generate.html", {"form": gen, "tid": testid, 
                                                      "thetest": thistest,
                                                      "base_url":settings.BASE_URL}) 

def clone(request, testid):
  pass
