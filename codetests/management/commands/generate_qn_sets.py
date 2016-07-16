from django.core.management.base import BaseCommand, CommandError
from codetests.models import CodeTests,CodeQnsList
from codejam import settings
import subprocess
import os
class Command(BaseCommand):
    help = 'Generates questions for all tests that need generated questions'

    def handle(self, *args, **options):
      testlist = CodeTests.objects.filter(generationStatus="AWAITING")
      for testid in testlist:
        testid.generationStatus="STARTED"
        testid.save()
      for testid in testlist:
        failed = False
        for qnx in CodeQnsList.objects.filter(testid=testid):
          qn = qnx.qn
          smallfilepath=settings.MEDIA_ROOT+"/solutions/"+str(testid.id)+"/"+str(qn.id)+"/small/"
          largefilepath=settings.MEDIA_ROOT+"/solutions/"+str(testid.id)+"/"+str(qn.id)+"/large/"

          if not os.path.exists(smallfilepath):
            os.makedirs(smallfilepath)
          if not os.path.exists(largefilepath):
            os.makedirs(largefilepath)

          idx = testid.qnsgenerated
          sno = 1
          while idx > 0: 
            rc = subprocess.check_call([settings.PYTHON, qn.smallscript.path, 
                                                        smallfilepath+str(sno)+"q.txt",
                                                        smallfilepath+str(sno)+"a.txt"])   
            if rc != 0:
              print "Failed to generate small script idx = %d, rc = %d"%(idx, rc)
              failed=True
              break
            rc = subprocess.check_call([settings.PYTHON, qn.largescript.path, 
                                                        largefilepath+str(sno)+"q.txt",
                                                        largefilepath+str(sno)+"a.txt"])   
            if rc != 0:
              print "Failed to generate small script idx = %d, rc = %d"%(idx, rc)
              failed=True
              break
            sno+=1 
            idx-=1

          if failed: 
            break
        if failed:
          print "failed testid '%s'"%(testid.title)
          testid.generationStatus="ERRORED"
          testid.save()
        else:
          testid.generationStatus="DONE"
          testid.save()
