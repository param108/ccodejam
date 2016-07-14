from django.shortcuts import render
from codetests.models import CodeTests
import os,time
from codejam import settings
import datetime
from django.utils.timezone import is_naive
import pytz
# Create your views here.
def testpage(request):
  os.environ['TZ']="Asia/Kolkata"
  time.tzset()
  check = datetime.datetime.now(pytz.timezone(os.environ['TZ']))
  # valid optimizes the number of records retrieved by
  # avoiding tests have ended already
  tests = CodeTests.objects.filter(end__gte=check).filter(start__lte=check);
  #tests = CodeTests.objects.all()
  for thistest in tests:
    print(thistest.testname)
    print(thistest.start)
    print(check)
    print(thistest.end)
  if request.method == "GET":
    return render(request, "coding/coding_tests.html",{"tests": tests, "base+url":settings.BASE_URL})
  return HttpResponseRedirect(settings.BASE_URL+"/go/tests/")
