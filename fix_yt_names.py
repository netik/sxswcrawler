#!/usr/bin/python

import mutagen.mp3
from ID3 import * 
import os

BASEDIR="music/yt"

for fn in os.listdir(BASEDIR):  
  print fn
  parts=fn.split(" - ",2)
  try: 
    artist=parts[0].lstrip().rstrip()
    title=parts[1].lstrip().rstrip().replace(".mp3","")
  except:
    continue


  try: 
    audio = mutagen.File("%s/%s" % (BASEDIR, fn), easy=True)
  except mutagen.mp3.HeaderNotFoundError:
    print "Cannot process: %s" % fn

  try: 
    audio["title"] = title
    audio["artist"] = artist
    print audio.pprint()
    print
    audio.save()
  except:
    print "couldn't read/update ID3"
  
  

  

  

