from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
import django
from rampup import settings
from create_user.models import RampUser, admin_users
from newtask.views import show as dashboardshow

# if RampUser doesnt exist for this user, create it
def checkCreateRampUser(user):
  ruser = None
  try:
    ruser = RampUser.objects.get(user=user)     
  except:
    ruser = RampUser(user=user)
    ruser.save()

# Create your views here.
def login(request):
  base_url = settings.BASE_URL
  if request.method == 'POST':
    uname = request.POST.get('username',""); 
    passwd = request.POST.get('password',""); 
    role = request.POST.get('role',""); 
    nnext = request.POST.get('next',base_url + "/");
    logged_in = False
    if len(uname) == 0 or len(passwd) == 0 or len(role) == 0:
      return render(request, 'registration/login.html',{'errors': 1, 'next':nnext, 'base_url': base_url});

    # first try to login the user
    user = authenticate(username=uname, password=passwd)
    if user is not None:
      if user.is_active:
        checkCreateRampUser(user)
        #now check if the role matches the user i.e if the chosen role was
        #admin and the user is staff
        if role == "admin": 
          if user.is_staff:
            #must login BEFORE using sessions.
            django.contrib.auth.login(request, user)
            request.session["role"]="admin" 
          else:
            # check the admins database for the username
            try:
              a_user = admin_users.objects.get(username__exact=user.username)
              if a_user.is_staff:
                print user.username+":"+str(a_user.is_staff)
                user.is_staff = True
                user.save()
                django.contrib.auth.login(request, user)
                request.session["role"]="admin" 
                logged_in = True
            except:
              # fallthrough
              pass

            # if he chose user or he doesnt have staff priveleges just log him
            # in as user
            if not logged_in:
              print user.username+": False"
              django.contrib.auth.login(request, user)
              request.session["role"]="user" 
        else:
          # if he chose user or he doesnt have staff priveleges just log him
          # in as user
          django.contrib.auth.login(request, user)
          request.session["role"]="user" 
        if nnext == (base_url + "/"):
          nnext=base_url + "/dashboard/show/"

        return redirect(nnext)
    # login failure case
    return render(request, 'registration/login.html',{'errors': 1, 'next':nnext, 'base_url': base_url});
  else:
    nnext = request.GET.get('next',base_url + "/");
    return render(request, 'registration/login.html',{'errors': 0, 'next':nnext, 'base_url':base_url});
