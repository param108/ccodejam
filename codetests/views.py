from django.shortcuts import render
from coding.models import Qns
from forms import CodeTestForm
# Create your views here.
def show(request):
  qns = Qns.objects.all();
  qnform = CodeTestForm() 
  return render(request, "codetests/codetests_show.html",{"form": qnform, "tests": qns})
