from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from codejam import settings

# Create your views here.
@login_required(login_url=(settings.BASE_URL+'/login/'))
def show(request):
  btns = []
  rolestring = "User"
  if request.user.is_staff:
    rolestring = "Admin"
    btns.append({ 'name': "Add Admin", "url":settings.BASE_URL+"/addadmin/"})
    btns.append({ 'name': "Create a test", "url":settings.BASE_URL+"/tests/show/"})
    btns.append({ 'name': "Add Question", "url":settings.BASE_URL+"/tests/questions/"})
  btns.append({ 'name': "Open Tests", "url":settings.BASE_URL+"/go/tests/"})
  #btns.append({ 'name': "Help", "url":settings.BASE_URL+"/docs/show/help1"})
  return render(request, 'dashboard/dashboard.html',
    { 'base_url': settings.BASE_URL,
      'username': request.user.username,
      'role': rolestring,
      'btns':btns,
      'media_url':settings.MEDIA_URL})
