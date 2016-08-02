import os
import sys
import subprocess
import tempfile
import shutil
if len(sys.argv)!=4:
  print "usage: %s <path to tar> <archive with qnsets> <output directory>"
  sys.exit(1)

tarpath=sys.argv[1]
tarfile = sys.argv[2]
outputpath = sys.argv[3]

try:
  os.makedirs(outputpath)
except:
  # ignore the errors
  pass

temppath=tempfile.mkdtemp(prefix="codejam")
os.chdir(temppath)
subprocess.check_call([tarpath, "-zxvf", tarfile])
subprocess.check_call(['cp', '-r', 'large', outputpath])
subprocess.check_call(['cp', '-r', 'small', outputpath])
shutil.rmtree(temppath, ignore_errors=True)


