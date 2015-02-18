#!/usr/bin/python

import mutagen.mp3 
from mutagen.mp3 import * 
import re
import os.path

BASEDIR="music/external_drive"
CACHE_DIR ="cache"

bandre = re.compile('<div class=\'data\'><h1>(.+)</h1>')
idre   = re.compile('<img alt="(\d+)"')
artistmap = {}

print "phase I... get ID to artist map"

for day in range(6,16):
  files = os.listdir("%s/%d" % (CACHE_DIR, day))

  for f in files:
    if f.find(".html") > -1 and f[0] == "_":

      id=""
      artist=""

      fh = open("%s/%d/%s" % (CACHE_DIR, day, f))

      for line in fh:
        m = bandre.search(line)
        if m != None:
          artist = m.group(1)

        m = idre.search(line)
        if m != None:
          id = m.group(1)

      fh.close()

      if id == "":
        print "FAIL: %d/%s" % (day, f)
      else: 
#        print "%s - %s" % (id,artist)
        artistmap[id] = artist

print "phase II... process MP3s"

failcnt = 0
for fn in os.listdir(BASEDIR):
  try: 
    audio = mutagen.File("%s/%s" % (BASEDIR, fn), easy=True)
  except mutagen.mp3.HeaderNotFoundError:
    print "Cannot process: %s" % fn

  songfn = ""
  title  = ""

  if audio == None:
    continue


  if audio.get("artist",None) != None:
    songfn = audio.get("artist")
  else:
    if audio.get("performer",None) != None:
      songfn = audio.get("performer")
    else:
      id = fn.replace(".mp3","")
      if artistmap.get(id, None) != None:
        songfn = artistmap.get(id)
      else: 
        songfn = "Unknown_%s" % id
        print "%s debug:" % fn
        print audio

      failcnt = failcnt + 1

  title = audio.get("title", "Unknown")

  if type(songfn) is list: 
    songfn = songfn[0]

  if isinstance(songfn, unicode):
    songfn = songfn.encode('ascii','ignore')

  if isinstance(title, unicode):
    title = title.encode('ascii','ignore')

  if type(title) is list: 
    title  = title[0]

  songfn = songfn.replace("/","")
  title = title.replace("/","")

  print "%s -> %s - %s" % (fn, songfn, title)
  os.rename("%s/%s" % (BASEDIR,fn),
            "%s/%s - %s" % (BASEDIR, songfn, title))
  
print "%d mp3s with no artist" % failcnt
  
