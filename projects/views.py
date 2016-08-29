from django.shortcuts import render
from models import Batch,Project
from forms import BatchForm
from codejam import settings
from django.http import HttpResponseRedirect,JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
# Create your views here.

def batches(request):
  bs = Batch.objects.all()
  return render(request, "projects/showBatches.html",{ "batchlist": bs,
                                                       "base_url": settings.BASE_URL })

# util function
def _addBatch(request, initform, initbatch, url):
  if request.method=="GET":
    if initform:
      form = initform
    else:
      form = BatchForm()
    return render(request, "projects/addBatch.html", { "url": url,
                                                       "form": form,
                                                       "base_url": settings.BASE_URL })
  else:
    form = BatchForm(request.POST)
    if form.is_valid():
      if initbatch:
        batch = initbatch
      else:
        batch = Batch()
      batch.batchname = form.cleaned_data["batchname"]
      batch.numreadouts= form.cleaned_data["numreadouts"]
      batch.start= form.cleaned_data["start"]
      batch.interval= form.cleaned_data["interval"]
      if "inputopen" in form.cleaned_data:
        batch.inputopen= form.cleaned_data["inputopen"]
      else:
        batch.inputopen=False
      if "showdashboard" in form.cleaned_data:
        batch.showdashboard= form.cleaned_data["showdashboard"]
      else:
        batch.showdashboard=False
      try:
        batch.save()
        return HttpResponseRedirect(settings.BASE_URL+"/projects/batch/show/")
      except:
        form.add_error("batchname","Please choose a unique batchname")
    return render(request, "projects/addBatch.html", { "url": url,
                                                       "form": form,
                                                       "base_url": settings.BASE_URL })

def addBatch(request):
  return _addBatch(request, None, None, settings.BASE_URL+"/projects/batch/new/")


def editBatch(request, batchid):
  batch = None
  try:
    batch = Batch.objects.get(pk=int(batchid))
  except:
    return HttpResponseRedirect(settings.BASE_URL+"/projects/batch/show/")
  form = None
  if request.method == "GET":
    form = BatchForm(initial={"batchname":batch.batchname,
                              "numreadouts":batch.numreadouts,
                              "start":batch.start,
                              "interval" : batch.interval,
                              "inputopen" : batch.inputopen,
                              "showdashboard": batch.showdashboard})
  return _addBatch(request, form, batch, settings.BASE_URL+"/projects/batch/edit/"+str(batchid)+"/")

def delBatch(request, batchid):
  batch = None
  try:
    batch = Batch.objects.get(pk=int(batchid))
  except:
    return HttpResponseRedirect(settings.BASE_URL+"/projects/batch/show/")
  batch.delete() 
  return HttpResponseRedirect(settings.BASE_URL+"/projects/batch/show/")

def addProjects(request, batchid):
  batch = None
  try:
    batch = Batch.objects.get(pk=int(batchid))
  except:
    return HttpResponseRedirect(settings.BASE_URL+"/projects/batch/show/")
  if request.method == "GET":
    return render(request, "projects/addProjects.html",
               { "base_url": settings.BASE_URL,
                 "batch": batch,
                 "projects": Project.objects.filter(batch=batch) })
  else:
    pass


@csrf_exempt
def updateProjects(request, batchid):
  batch = None
  try:
    batch = Batch.objects.get(pk=int(batchid))
  except:
    # try to screw with me I silently return ok without doing shit.
    return JsonResponse({"status": 0});
  if request.method == "POST":
    projects = json.loads(request.body)
    for pr in projects['projects']:
      if pr["id"] != "-1":
        id = int(pr["id"])
        try:
          proj = Project.objects.get(pk=id) 
          if proj.batch.id == batch.id:
            proj.title = pr["val"]
            proj.save()
        except Exception,e:
          print ("Failed to save new project"+str(e))
      else:
        proj = Project()
        proj.batch = batch
        proj.title = pr["val"]
        try:
          proj.save()
        except Exception,e:
          print ("Failed to update project"+str(e))
  return JsonResponse({"status": 0});

def delProjects(request, batchid, projectid):
  batch = None
  try:
    batch = Batch.objects.get(pk=int(batchid))
  except:
    # try to screw with me I silently return ok without doing shit.
    return HttpResponseRedirect(settings.BASE_URL+"/projects/batch/show/")

  project = None
  try:
    project = Project.objects.get(pk = int(projectid))
  except:   
    return HttpResponseRedirect(settings.BASE_URL+"/projects/add/"+batchid+"/")
  project.delete()
  return HttpResponseRedirect(settings.BASE_URL+"/projects/add/"+batchid+"/")

