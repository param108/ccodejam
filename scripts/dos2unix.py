import tempfile
import sys
import subprocess


fname=sys.argv[1]
fp = open(fname,"rb")
fd,path=tempfile.mkstemp()


op = open(path,"wb")
halfway = False
data = fp.read(1000)
while len(data) == 1000:
  if data[-1]=="\r":
    data[:(len(data) -1)]
  data = data.replace("\r\n","\n")
  op.write(data)
  data = fp.read(1000)
data = data.replace("\r\n","\n")
if data[-1] != "\n":
  data += "\n"
op.write(data)
subprocess.check_output(["mv",path,sys.argv[1]])
