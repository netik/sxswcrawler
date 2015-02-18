#!/usr/bin/python

import os
import re 


BASEDIR="/Volumes/field_photos/SXSW_2014_MP3s/youtube"
files = os.listdir(BASEDIR)

for f in files:
  fn = f.replace(" -", "-")
  fn = fn.replace("- ", "-")
  fn = fn.replace(" ", "_")

#  fn = re.sub("\d+-_","-",fn)
#  fn = re.sub("-\d+_","-",fn)

  print BASEDIR+"/"+f
  print " --- > " + BASEDIR+"/"+fn
  print
  os.rename(BASEDIR+"/"+f,BASEDIR+"/"+fn)

