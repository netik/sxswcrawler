#!/usr/bin/python

import os
import re 
import mutagen.mp3 
from mutagen.mp3 import * 


BASEDIR="./music/sx"
files = os.listdir(BASEDIR)

for f in files:
  try: 
    audio = mutagen.File("%s/%s" % (BASEDIR, f))
  except mutagen.mp3.HeaderNotFoundError:
    print "Cannot process: %s" % fn
    
  fn = f.replace(" -", "-")
  fn = fn.replace("- ", "-")
  fn = fn.replace(" ", "_")
  fn = re.sub("^0[\d]+_","",fn)
  
  artist=""
  print audio["title"]
  
  if audio.get("artist",None) != None:
    artist = audio.get("artist")

  song = ""
  if audio.get("title",None) != None:
    song = audio.get("title")
    
  song = re.sub("^0[\d]-_","",song).rstrip("_").lstrip("_")
  song = re.sub("^0[\d]_-_","",song).rstrip("_").lstrip("_")
  song = re.sub("^0[\d]-","",song).rstrip("_").lstrip("_")

  newfile = artist + "-" + song + ".mp3"

  print BASEDIR+"/"+f
  print " --- > " + BASEDIR+"/"+newfile
  print

  #os.rename(BASEDIR+"/"+f,BASEDIR+"/"+fn)

