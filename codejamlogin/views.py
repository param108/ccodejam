from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
import django
from codejam import settings
from models import admin_users
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
# Create your views here.
def login(request):
  base_url = settings.BASE_URL
  if request.method == 'POST':
    uname = request.POST.get('username',""); 
    passwd = request.POST.get('password',""); 
    nnext = request.POST.get('next',base_url + "/");
    logged_in = False
    if len(uname) == 0 or len(passwd) == 0:
      return render(request, 'registration/login.html',{'errors': 1, 'next':nnext, 'base_url': base_url});

    # first try to login the user
    user = authenticate(username=uname, password=passwd)
    if user is not None:
      if user.is_active:
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
        django.contrib.auth.login(request, user)

        if nnext == (base_url + "/"):
          nnext=base_url + "dashboard/show/"

        return redirect(nnext)
    # login failure case
    return render(request, 'registration/login.html',{'errors': 1, 'next':nnext, 'base_url': base_url});
  else:
    nnext = request.GET.get('next',base_url + "/");
    return render(request, 'registration/login.html',{'errors': 0, 'next':nnext, 'base_url':base_url});


@login_required(login_url=settings.BASE_URL+'/login/')
@staff_member_required
def show_admins(request):
    table = None
    a_form = None
    if request.method=='POST':
      a_form = admin_user_form(request.POST)
      if a_form.is_valid():
        a_user = admin_users(username=a_form.cleaned_data["username"], is_staff = True)
        a_user.save()
    else:
      a_form = admin_user_form()
    table = admin_users.objects.all()
    return render(request, 'registration/add_admin.html', { 'table': table, 'form': a_form,'base_url':settings.BASE_URL })

