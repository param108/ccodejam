from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from models import Batch,Project,Member,Milestone,LineItem,ScoreCard
from models import ScoreQn,SocreAns,ScoreCardLink
from forms import BatchForm
from codejam import settings
from django.http import HttpResponseRedirect,JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from coding.view import Lock
import django.utils.timezone as dtz
import json
import datetime
import pytz
import os

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
    projects = Project.objects.filter(batch=batch)
    projectlist=[]
    for project in projects:
      role="noedit"
      if canEditStatus(request.user, batch, project):
        role = "edit"
      projectlist.append((project,role))
 
    return render(request, "projects/addProjects.html",
               { "superuser": request.user.is_superuser, 
                 "base_url": settings.BASE_URL,
                 "batch": batch,
                 "projects": projectlist })
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

  projectlist=[]
  for project in projects:
    role="noedit"
    if canEditStatus(request.user, batch, project):
      role = "edit"
    projectlist.append((project,role))
  

  if request.method == "GET":
    return render(request, "projects/addProjects.html",
               { "superuser": request.user.is_superuser,
                 "base_url": settings.BASE_URL,
                 "batch": batch,
                 "projects": projectlist })
  else:
    pass

def ExecProjMember(project, user):
  members = Member.objects.filter(project=project).filter(user=user)
  for memb in members:
    if memb.role == "Director" or memb.role == "Mentor":
      return True
  print "Not exec member:"+user.username
  return False

def canEditStatus(user, batch, project):
  if batch.showdashboard:
    if user.is_superuser:
      return True
    if ExecProjMember(project, user):
      return True
  else:
    if user.is_superuser:
      return True 
  return False


def canEdit(user, batch, project):
  if batch.inputopen:
    if user.is_superuser:
      return True
    if ExecProjMember(project, user):
      return True
  else:
    if user.is_superuser:
      return True 
  return False

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

@login_required(login_url=(settings.BASE_URL+'/login/'))
def ShowMilestoneStates(request, batchid, projectid):
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

  #if not ExecProjMember(project, request.user):
  #  return HttpResponseRedirect(settings.BASE_URL+"/dashboard/show/")
  role = "noedit"
  if canEditStatus(request.user, batch, project):
    role = "status"

  itemlist=[]
  milestones = firstlogin(project)
  for milestone in milestones:
    lineitems = LineItem.objects.filter(milestone = milestone).order_by('seq')
    itemlist.append((milestone,lineitems))

  return render(request, "projects/addMilestones.html",{'base_url': settings.BASE_URL, 'ls':itemlist,'role': role, 'project': project,
  'batch': batch})

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

  #if not ExecProjMember(project, request.user):
  #  return HttpResponseRedirect(settings.BASE_URL+"/dashboard/show/")
  role = "noedit"
  if canEdit(request.user, batch, project):
    role = "edit"

  itemlist=[]
  milestones = firstlogin(project)
  for milestone in milestones:
    lineitems = LineItem.objects.filter(milestone = milestone).order_by('seq')
    itemlist.append((milestone,lineitems))

  return render(request, "projects/addMilestones.html",{'base_url': settings.BASE_URL, 'ls':itemlist,'role': role, 'project': project,
  'batch': batch})
@csrf_exempt
@login_required(login_url=(settings.BASE_URL+'/login/'))
def statusMilestones(request, batchid, projectid):
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

  if not canEditStatus(request.user, batch, project):
    return JsonResponse({"status": -1});

  if project.batch != batch:
    return JsonResponse({"status": -1});
    
  if request.method == "POST":
    milestones = json.loads(request.body)
    for pr in milestones['lineitems']:
      if pr["id"] != "-1":
        lid = int(pr["id"])
        try:
          line = LineItem.objects.get(pk=lid) 
          if line.milestone.project.id == project.id:
            line.state = pr["state"]
            line.save()
        except Exception,e:
          print ("Failed to save new project"+str(e))
      else:
        # this view is not the correct place for new lineItems
        return JsonResponse({"status": -1});
  return JsonResponse({"status": 0});


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

  if not canEdit(request.user, batch, project):
    return JsonResponse({"status": -1});

  if project.batch != batch:
    return JsonResponse({"status": -1});
    
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

  if not canEdit(request.user, batch, project):
    return JsonResponse({"status": -1});

  lineitem = None
  try:
    lineitem = LineItem.objects.get(pk = int(lid))
  except:
    return HttpResponseRedirect(settings.BASE_URL+"/projects/milestones/add/"+batchid+"/"+projectid+"/")

  if lineitem.milestone.project.id != project.id or project.batch.id != batch.id:
    return HttpResponseRedirect(settings.BASE_URL+"/projects/milestones/add/"+batchid+"/"+projectid+"/")

  lineitem.delete()
  return HttpResponseRedirect(settings.BASE_URL+"/projects/milestones/add/"+batchid+"/"+projectid+"/")

class MilestoneData:
  milestone=None
  lineitems=None
  def __init__(self, milestone, lineitems):
    self.milestone = milestone
    self.lineitems = lineitems

class ProjectData:
  project=None
  members=None
  mcount=0 #number of milestones
  reason=""
  status=""
  directors=[]
  nch=[]
  mentors=[] 
  def calcStatus(self):
    numlines = 0
    for mstone in self.milestones:
      numlines += len(mstone.lineitems)
    if self.mcount > numlines:
      self.reason = "Too few milestones"
      return "red"
    check = datetime.datetime.now(pytz.timezone(os.environ['TZ']))
    totalvalid=0
    completed=0
    for milestone in self.milestones:
      dcomp = dtz.make_aware(datetime.datetime.combine(milestone.milestone.date, datetime.datetime.min.time()), pytz.timezone(os.environ['TZ']))
      if dcomp < check:
        for lineitem in milestone.lineitems:
          totalvalid+=1
          if lineitem.state == "DONE":
            completed+=1
    if totalvalid > 0:
      # '=' is a hack to make 0 done a red
      if completed <= (totalvalid/2):
          self.reason = "Less than half completed"
          return "red"
      else:
        if completed < totalvalid:
          self.reason = "running behind schedule"
          return "orange"
    return "green"

  def getRoles(self):
    self.directors=[]
    self.nch=[]
    self.mentors=[] 
    for member in self.members:
      if member.role=="Director":
        self.directors.append(member)
      if member.role=="NCH":
        self.nch.append(member)
      if member.role=="Mentor":
        self.mentors.append(member) 

  def __init__(self, project):
    self.project=project
    self.members=Member.objects.filter(project=project)
    self.getRoles()
    self.milestones=[] 
    nummilestones = 0
    for milestone in Milestone.objects.filter(project=project):
      mobj = MilestoneData(milestone, LineItem.objects.filter(milestone = milestone).order_by("seq"))
      self.milestones.append(mobj)
      nummilestones+=1
    self.mcount = nummilestones
    self.status = self.calcStatus()

# no login required to view
def dashboard(request, batchid):
  batch = None
  try:
    batch = Batch.objects.get(pk=int(batchid))
  except:
    # try to screw with me I silently return ok without doing shit.
    return HttpResponseRedirect(settings.BASE_URL+"/projects/batch/show/")
  
  if not batch.showdashboard:
    return HttpResponseRedirect(settings.BASE_URL+"/projects/batch/show/")

  projects = Project.objects.filter(batch_id=int(batchid)).order_by("title")
  projectdatas=[]
  for project in projects:
    pd = ProjectData(project) 
    projectdatas.append(pd)
  return render(request, "projects/dashboard.html", { 'projects': projectdatas,
 'base_url': settings.BASE_URL, 'batch': batch })

def createScore(request,batchid):
  pass

def editScore(request,scardid):
  pass

def deleteScore(request,scardid):
  pass

def addScoreQn(request):
  pass

def delScoreQn(request, scqnid):
  pass

def editScoreQn(request, scqnid):
  pass

def createScoreCard(scorecardid, user):
  try:
    scorecard = ScoreCard.objects.get(pk=scorecardid)
  except:
    return False
  with(user, "createscorecard") as lock: 
    ScoreAns.objects.filter(user = user).filter(link_scorecard = scorecard)
    if len(ScoreAns):
      return True

    for link in  ScoreCardLink.object.filter(scorecard = scorecard).order_by("seq"):
      # if a link exists break
      ans = ScoreAns(user = user, link=link)
      ans.save()
    return True
  return False
    
def generateyesno(ans):
  i = '<div id="ans_%d" class="scorecard-input"><label>%s <input type="checkbox"/></label></div>'%(ans.id, ans.link.qn.qn)
  print i
  return i

def generaterange(ans):
  i = '<div id="ans_%d"><label>%s</label><br>'%(ans.id, ans.link.qn.qn)
  radios= [ '<input type="radio" name="ans_%d" value="%d">%d'%(ans.id,x) for x in range(1,6)]
  i+=" ".join(radios)
  print i
  return i+'</div>'

def generaterangecomment(ans):
  i = '<div id="ans_%d"><label>%s</label><br>'%(ans.id, ans.link.qn.qn)
  radios= [ '<input type="radio" name="ans_%d" value="%d">%d'%(ans.id,x) for x in range(1,6)]
  i+=" ".join(radios)
  i+='<textarea class="scorecard-textarea"></textarea>'
  print i
  return i+'</div>'

def generate_form(batchid):
  sc = ScoreCard.get(batch_id = batchid)
  



