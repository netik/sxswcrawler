#!/usr/bin/python
#
# If a filename starts with "Unknown ", strip it off and rename
# This seems to be a side effect from sxsw renaming?
#

import sys 
import os

def ap(s):
  try:
    out = s.encode('ascii', 'ignore')
  except:
    out = s.decode('utf8')
  return out

BASEDIR="music/sx"
DRYRUN=False

files = os.listdir(BASEDIR)

for f in files:
    if f.startswith("Unknown "):
        newf = f.replace("Unknown ","",1)
        print "%s -> %s" % ( ap(f), ap(newf) )

        if DRYRUN == False:
            os.rename("%s/%s" % (BASEDIR,f),
                      "%s/%s" % (BASEDIR,newf))
        

