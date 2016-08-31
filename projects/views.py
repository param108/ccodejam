from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from models import Batch,Project,Member,Milestone,LineItem
from forms import BatchForm
from codejam import settings
from django.http import HttpResponseRedirect,JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
import json
import datetime
# Create your views here.
@login_required(login_url=(settings.BASE_URL+'/login/'))
def mybatches(request):
  bs = Batch.objects.filter(project__member__user=request.user)
  return render(request, "projects/showBatches.html",{ "superuser": request.user.is_superuser, 
                                                       "batchlist": bs,
                                                       "base_url": settings.BASE_URL })


@login_required(login_url=(settings.BASE_URL+'/login/'))
@user_passes_test(lambda u: u.is_superuser)
def batches(request):
  bs = Batch.objects.all()
  return render(request, "projects/showBatches.html",{ "superuser": request.user.is_superuser, 
                                                       "batchlist": bs,
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

@login_required(login_url=(settings.BASE_URL+'/login/'))
@user_passes_test(lambda u: u.is_superuser)
def addBatch(request):
  return _addBatch(request, None, None, settings.BASE_URL+"/projects/batch/new/")


@login_required(login_url=(settings.BASE_URL+'/login/'))
@user_passes_test(lambda u: u.is_superuser)
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

@csrf_exempt
@login_required(login_url=(settings.BASE_URL+'/login/'))
@user_passes_test(lambda u: u.is_superuser)
def delBatch(request, batchid):
  batch = None
  try:
    batch = Batch.objects.get(pk=int(batchid))
  except:
    return HttpResponseRedirect(settings.BASE_URL+"/projects/batch/show/")
  batch.delete() 
  return HttpResponseRedirect(settings.BASE_URL+"/projects/batch/show/")

@login_required(login_url=(settings.BASE_URL+'/login/'))
@user_passes_test(lambda u: u.is_superuser)
def addProjects(request, batchid):
  batch = None
  try:
    batch = Batch.objects.get(pk=int(batchid))
  except:
    return HttpResponseRedirect(settings.BASE_URL+"/projects/batch/show/")
  if request.method == "GET":
    return render(request, "projects/addProjects.html",
               { "superuser": request.user.is_superuser, 
                 "base_url": settings.BASE_URL,
                 "batch": batch,
                 "projects": Project.objects.filter(batch=batch) })
  else:
    pass

@login_required(login_url=(settings.BASE_URL+'/login/'))
def myProjects(request, batchid):
  batch = None
  try:
    batch = Batch.objects.get(pk=int(batchid))
  except:
    return HttpResponseRedirect(settings.BASE_URL+"/projects/batch/show/")
  projects = Project.objects.filter(batch=batch).filter(member__user=request.user)
  if request.method == "GET":
    return render(request, "projects/addProjects.html",
               { "superuser": request.user.is_superuser,
                 "base_url": settings.BASE_URL,
                 "batch": batch,
                 "projects": projects })
  else:
    pass



@csrf_exempt
@login_required(login_url=(settings.BASE_URL+'/login/'))
@user_passes_test(lambda u: u.is_superuser)
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

@login_required(login_url=(settings.BASE_URL+'/login/'))
@user_passes_test(lambda u: u.is_superuser)
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

@login_required(login_url=(settings.BASE_URL+'/login/'))
@user_passes_test(lambda u: u.is_superuser)
def addMentors(request, batchid, projectid):
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

  mentors = Member.objects.filter(project=project)
  return render(request, "projects/addMentors.html", {"base_url": settings.BASE_URL,
                                                      "batch": batch,
                                                      "project": project,
                                                      "mentors": mentors })
  #return HttpResponseRedirect(settings.BASE_URL+"/projects/mentors/add/"+batchid+"/"+projectid+"/")

def checkLoggedIn(memb):
  try:
    u = User.objects.get(username=memb.username)  
    memb.user = u
    memb.loggedin = True
  except:
    memb.loggedin = False
 
@csrf_exempt
@login_required(login_url=(settings.BASE_URL+'/login/'))
@user_passes_test(lambda u: u.is_superuser)
def updateMentors(request, batchid, projectid):
  batch = None
  try:
    batch = Batch.objects.get(pk=int(batchid))
  except:
    # try to screw with me I silently return ok without doing shit.
    return JsonResponse({"status": 0});

  project = None
  try:
    project = Project.objects.get(pk = int(projectid))
  except:   
    return JsonResponse({"status": 0});

  if project.batch != batch:
    return JsonResponse({"status": 0});
    
  if request.method == "POST":
    mentors = json.loads(request.body)
    for pr in mentors['mentors']:
      if pr["id"] != "-1":
        id = int(pr["id"])
        try:
          memb = Member.objects.get(pk=id) 
          if memb.project.id == project.id:
            memb.username = pr["username"]
            memb.role = pr["role"]
            checkLoggedIn(memb)
            memb.save()
        except Exception,e:
          print ("Failed to save new project"+str(e))
      else:
        memb = Member()
        memb.project = project
        memb.username = pr["username"]
        memb.role = pr["role"]
        checkLoggedIn(memb)
        memb.save()
        try:
          memb.save()
        except Exception,e:
          print ("Failed to update project"+str(e))
  return JsonResponse({"status": 0});

@csrf_exempt
@login_required(login_url=(settings.BASE_URL+'/login/'))
@user_passes_test(lambda u: u.is_superuser)
def delMentors(request, batchid, projectid, memberid):
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

  member = None
  try:
    member = Member.objects.get(pk = int(memberid))
  except:
    return HttpResponseRedirect(settings.BASE_URL+"/projects/mentors/add/"+batchid+"/"+projectid+"/")

  if member.project.id != project.id or project.batch.id != batch.id:
    return HttpResponseRedirect(settings.BASE_URL+"/projects/mentors/add/"+batchid+"/"+projectid+"/")

  member.delete()
  return HttpResponseRedirect(settings.BASE_URL+"/projects/mentors/add/"+batchid+"/"+projectid+"/")


def firstlogin(project):
  milestones = Milestone.objects.filter(project=project).order_by('seq')
  if len(milestones) == 0:
    start = project.batch.start
    delta = datetime.timedelta(weeks=project.batch.interval)
    for i in range(project.batch.numreadouts):
      milestone = Milestone()
      milestone.project = project
      milestone.seq = i+1
      milestone.date = start
      start = start + delta
      milestone.save()
  milestones = Milestone.objects.filter(project=project).order_by('seq')
  return milestones

def ExecProjMember(project, user):
  members = Member.objects.filter(project=project).filter(user=user)
  for memb in members:
    if memb.role == "Director" or memb.role == "Mentor":
      return True
  print "Not exec member:"+user.username
  return False


@login_required(login_url=(settings.BASE_URL+'/login/'))
def addMilestones(request, batchid, projectid):
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
    return HttpResponseRedirect(settings.BASE_URL+"/projects/batch/show/")

  if not ExecProjMember(project, request.user):
    return HttpResponseRedirect(settings.BASE_URL+"/dashboard/show/")

  itemlist=[]
  milestones = firstlogin(project)
  for milestone in milestones:
    lineitems = LineItem.objects.filter(milestone = milestone).order_by('seq')
    itemlist.append((milestone,lineitems))

  # figure out the role of the member
  memb = Member.objects.filter(project=project).filter(user=request.user)[0]
  role = memb.role

  return render(request, "projects/addMilestones.html",{'base_url': settings.BASE_URL, 'ls':itemlist,'role': role, 'open': batch.inputopen, 'project': project,
  'batch': batch})

@csrf_exempt
@login_required(login_url=(settings.BASE_URL+'/login/'))
def updateMilestones(request, batchid, projectid):
  batch = None
  try:
    batch = Batch.objects.get(pk=int(batchid))
  except:
    # try to screw with me I silently return ok without doing shit.
    return JsonResponse({"status": 0});

  project = None
  try:
    project = Project.objects.get(pk = int(projectid))
  except:   
    return JsonResponse({"status": 0});

  if not ExecProjMember(project, request.user):
    return HttpResponseRedirect(settings.BASE_URL+"/dashboard/show/")

  if project.batch != batch:
    return JsonResponse({"status": 0});
    
  if request.method == "POST":
    milestones = json.loads(request.body)
    for pr in milestones['lineitems']:
      if pr["id"] != "-1":
        lid = int(pr["id"])
        try:
          line = LineItem.objects.get(pk=lid) 
          if line.milestone.project.id == project.id:
            line.details = pr["details"]
            line.seq = pr["seq"]
            line.save()
        except Exception,e:
          print ("Failed to save new project"+str(e))
      else:
        line = LineItem()
        line.details = pr["details"]
        line.seq = pr["seq"]
        try:
          line.milestone = Milestone.objects.get(pk=int(pr["mid"]))
          line.save()
        except Exception,e:
          print ("Failed to update project"+str(e))
  return JsonResponse({"status": 0});

@csrf_exempt
@login_required(login_url=(settings.BASE_URL+'/login/'))
def delMilestones(request, batchid, projectid, lid):
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

  if not ExecProjMember(project, request.user):
    return HttpResponseRedirect(settings.BASE_URL+"/dashboard/show/")

  lineitem = None
  try:
    lineitem = LineItem.objects.get(pk = int(lid))
  except:
    return HttpResponseRedirect(settings.BASE_URL+"/projects/milestones/add/"+batchid+"/"+projectid+"/")

  if lineitem.milestone.project.id != project.id or project.batch.id != batch.id:
    return HttpResponseRedirect(settings.BASE_URL+"/projects/milestones/add/"+batchid+"/"+projectid+"/")

  lineitem.delete()
  return HttpResponseRedirect(settings.BASE_URL+"/projects/milestones/add/"+batchid+"/"+projectid+"/")


