from django.shortcuts import render
from coding.models import Qns
from forms import CodeTestForm
from models import CodeTests
# Create your views here.
def show(request):
  qns = CodeTests.objects.all();
  qnform = CodeTestForm() 
  return render(request, "codetests/codetests_show.html",{"form": qnform, "tests": qns})
