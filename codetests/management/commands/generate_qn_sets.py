from django.core.management.base import BaseCommand, CommandError
from codetests.models import CodeTests,CodeQnsList
from codejam import settings
import subprocess
import os
import shutil
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

          if qn.usesuploadedqns:
            failed = self.copyQns(testid, qn, smallfilepath, largefilepath)
          else:
            failed = self.generateQns(testid, qn, smallfilepath, largefilepath)
            if failed:
              break
        if failed:
          print "failed testid '%s'"%(testid.testname)
          testid.generationStatus="ERRORED"
          testid.save()
        else:
          testid.generationStatus="DONE"
          testid.save()

    def copyQns(self, testid, qn, smallfilepath, largefilepath):
      ret = False
      try:
        qnlimit = qn.numqnsuploadedsmall
        self.copyAQnSet(testid, qn, smallfilepath, "small", qnlimit)
        if qn.need2questions: 
          qnlimit = qn.numqnsuploadedlarge
          self.copyAQnSet(testid, qn, largefilepath, "large", qnlimit)
      except Exception,e:
        print ("Failed to copy questions:"+ str(e))
        ret = True
      return ret

    def copyAQnSet(self, testid, qn, outputpath, qtype, qnlimit):
      numqnstomake=testid.qnsgenerated
      idx = 1
      inputpath = "%s/qns/%d/qnset/%s/"%(settings.MEDIA_ROOT,qn.id,qtype)
      for i in range(testid.qnsgenerated):
        # repeat the questions until we have enough
        if idx == qnlimit:
          idx = 1 
        shutil.copyfile(inputpath+str(idx)+"q.txt", outputpath+str(i+1)+"q.txt")
        shutil.copyfile(inputpath+str(idx)+"a.txt", outputpath+str(i+1)+"a.txt")
        idx+=1
        
    def generateQns(self, testid, qn, smallfilepath, largefilepath):
      idx = testid.qnsgenerated
      sno = 1
      failed = False
      while idx > 0: 
        rc = subprocess.check_call([settings.PYTHON, qn.smallscript.path, 
                                                smallfilepath+str(sno)+"q.txt",
                                                smallfilepath+str(sno)+"a.txt"])   
        if rc != 0:
          print "Failed to generate small script idx = %d, rc = %d"%(idx, rc)
          failed=True
          break
        if qn.need2questions:
          rc = subprocess.check_call([settings.PYTHON, qn.largescript.path, 
                                                largefilepath+str(sno)+"q.txt",
                                                largefilepath+str(sno)+"a.txt"])   
          if rc != 0:
            print "Failed to generate small script idx = %d, rc = %d"%(idx, rc)
            failed=True
            break
        sno+=1 
        idx-=1
      return failed

