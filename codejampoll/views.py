from django.shortcuts import render
from forms import VoteForm
from codejam import settings
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse,HttpResponseNotFound
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from models import Votes
from django.utils.cache import add_never_cache_headers
# Create your views here.

choicelist = [("3D", "3D - Datapath Decoders and Debuggers"),
("ARP SUP","ARP SUP"),
("DRAIN", "DRAIN - Dynamic Reachability and Authorization in IOT Network "),
("DSNS", "DSNS-Design Simulation for Network Timing and Synchronization"),
("FEX consistency checker","FEX consistency checker"),
("Fretta","Fretta"),
("ICE-AGE RING ","ICE-AGE RING "),
("iConnect","iConnect"),
("ISP Helper","ISP Helper"),
("Jericho","Jericho"),
("Next Gen IOSXR Install","Next Gen IOSXR Install"),
("PackMan","PackMan"),
("PrESET","PrESET"),
("RoCon","RoCon"),
("SAN Zoners","SAN Zoners"),
("SMU iV&V for N5K/N6K","SMU iV&V for N5K/N6K"),
("Scapa QoS","Scapa QoS"),
("Segment Routing","Segment Routing"),
("SparTAN","SparTAN"),
("TBOT on XR","TBOT on XR"),
("unWind", "unWind!!-Quality Assured"),
("Winternetfell","Winternetfell"),
("Yin and yang","Yin and yang")]

@staff_member_required
def view(request):
  votes = Votes.objects.filter(tag="NCH2016")
  total = len(votes)
  score = {}
  for v in votes:
    if v.shortname not in score:
      score[v.shortname] = 1 
    else:
      score[v.shortname] += 1 
  final_list= []
  for i in score:
    final_list.append((i,score[i],total)) 
  final_list.sort(key=lambda x:x[1], reverse=True)
  ret = render(request, "codejampoll/scoreboard.html",{"flist":final_list, "base_url":settings.BASE_URL})
  add_never_cache_headers(ret)
  return ret

def getchoice_data(ch):
  for i in choicelist:
    if i[0] == ch:
      return i

@login_required(login_url=(settings.BASE_URL+'/login/'))
def vote(request):
  if request.method == "GET":
    v = VoteForm()
    v.setup_choices(choicelist)
    ret = render(request, "codejampoll/vote.html",{"form":v, "base_url":settings.BASE_URL})
    add_never_cache_headers(ret)
    return ret
  elif request.method == "POST":
    v = VoteForm(request.POST)
    v.setup_choices(choicelist)
    if v.is_valid():
      ch =  v.cleaned_data["Choice"] 
      v = Votes.objects.filter(user=request.user).filter(tag="NCH2016")
      totalch = getchoice_data(ch)
      if len(v):
        v[0].shortname = totalch[0]
        v[0].longname = totalch[1]
        v[0].save()
      else:
        newv = Votes()
        newv.tag = "NCH2016"
        newv.user = request.user
        newv.shortname = totalch[0]
        newv.longname = totalch[1]
        newv.save()
      logout(request)
      ret = render(request, "codejampoll/loggedout.html",{"message":"previous vote successfully registered.", "base_url":settings.BASE_URL})
      add_never_cache_headers(ret)
      return ret;
    else:
      ret = render(request, "codejampoll/vote.html",{"form":v, "base_url":settings.BASE_URL})
      add_never_cache_headers(ret)
      return ret
    return HttpResponse("Done")

@login_required(login_url=(settings.BASE_URL+'/login/'))
def cancelvote(request):
  logout(request)
  ret = render(request, "codejampoll/loggedout.html",{"message":"previous vote cancelled.", "base_url":settings.BASE_URL})
  add_never_cache_headers(ret)
  return ret
  
