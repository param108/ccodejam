from django.shortcuts import render
from models import Batch
from forms import BatchForm
from codejam import settings
from django.http import HttpResponseRedirect
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
                 "batch": batch })
  else:
    pass
