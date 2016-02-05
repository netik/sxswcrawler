#!/usr/bin/python

import mutagen.mp3 
from mutagen.mp3 import * 
import re
import sys 
import os.path
import sys, codecs, locale

BASEDIR="music/sx"
CACHE_DIR ="cache"
bandre = re.compile(r"\content=\'(.*)\' name=\'twitter\:title\'")
idre   = re.compile(r"/mp3_by_artist_id/(\d+).mp3")
titlere = re.compile(r"<h4>Listen to <i>(.+)</i></h4>")
artistmap = {}
titlemap = {}

def ap(s):
  try:
    out = s.encode('ascii', 'ignore')
  except:
    out = s.decode('utf8')
  return out

# set this to be true to be non-destructive
DRYRUN=False

print "phase I... get ID to artist map"

files = os.listdir("%s/%s" % (CACHE_DIR, "events"))

for f in files:
  if f.find(".html") > -1 and f[0] == "_":
    
    id = ""
    artist = ""
    title = ""

    fh = open("%s/%s/%s" % (CACHE_DIR, "events", f), "r")
    for line in fh:
      m = bandre.search(line)
      if m != None:
        artist = m.group(1)

      m = idre.search(line)
      if m != None:
        id = m.group(1)

      m = titlere.search(line)
      if m != None:
        title = m.group(1)

    fh.close()

    if id == "":
      print "FAIL: %s/%s" % ("events", f)
    else: 
      sys.stdout.write("%s - %s - %s\n" % (id, artist,title))
      artistmap[id] = artist
      titlemap[id] = title

print "phase II... Rename files"

failcnt = 0

for fn in os.listdir(BASEDIR):
  print "--- start %s ---" %fn
  try: 
    audio = mutagen.File("%s/%s" % (BASEDIR, fn), easy=True)
  except mutagen.mp3.HeaderNotFoundError:
    print "Cannot process: %s" % fn

  artist = ""
  title  = ""

  try:
    if audio == None:
      continue
  except  mutagen.easyid3.EasyID3KeyError:
    print "ignoring key error"


  id = fn.replace(".mp3","")
  print "my id is %s " % id

  if audio.get("artist",None) != None:
    artist = audio.get("artist")
  else:
    if audio.get("performer",None) != None:
      artist = audio.get("performer")
    else:
      if artistmap.get(id, None) != None:
        artist = artistmap.get(id)
      else: 
        artist = artistmap.get(id)
        print "%s debug:" % fn
        print audio
        failcnt = failcnt + 1

  title = audio.get("title", 'unknown')
  if (title == 'unknown'):
    id = fn.replace(".mp3","")
    try:
      title = titlemap[id]
    except KeyError:
      title = "Unknown"
  
  if type(artist) is list: 
    artist = artist[0]

  if isinstance(artist, unicode):
    artist = artist.encode('ascii','ignore')

  if isinstance(title, unicode):
    title = title.encode('ascii','ignore')

  if type(title) is list: 
    title  = title[0]

  if artist == None:
    artist = "Unknown %s" % id

  artist = artist.replace("/","")
  title = title.replace("/","")

  # write this information back into the MP3
  try: 
    audio["title"] = title
    audio["artist"] = artist
    print audio.pprint()
    print
    if DRYRUN == False:
      audio.save()
  except:
    print "couldn't read/update ID3"

  # rename the file

  print u"%s %s/%s --> %s/%s - %s\n" % (unicode(id, "utf-8"), 
                                        unicode(BASEDIR, "utf-8"),
                                        unicode(fn, "utf-8"), 
                                        unicode(BASEDIR, "utf-8"), 
                                        ap(artist), ap(title))
  
  if DRYRUN == False:
    os.rename("%s/%s" % (BASEDIR,fn),
              "%s/%s - %s.mp3" % (BASEDIR, ap(artist), ap(title)))

  print "--- end %s ---" %fn

# we're done
  
print "%d mp3s with no artist" % failcnt
  













