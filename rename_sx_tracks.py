#!/usr/bin/python
#
# ./rename_sx_tracks.py 
#
# Given a set of mp3 files in music/sx, try to read their ID3 tags and
# rename the file's name to match
#

import os
import re 
import mutagen.mp3 
from mutagen.mp3 import * 

HTML_MAP={}

BASEDIR="./music/sx"

# load the map file in.
mp3re  = re.compile(r'http://audio.sxsw.com/\d+/mp3_by_artist_id/([^\.]*.mp3)')
mapf = open("data/map.txt");

for line in mapf:
  parts = line.rstrip().split("|")
  q = mp3re.search(parts[2])
  
  if q != None:
    audiofn = q.group(1)

    HTML_MAP[audiofn] = {
      "htmlfn": parts[0],
      "artist" : parts[1],
      "audiofn" : parts[2],
      "detail" : parts[3]
    }
    

# process the list
files = os.listdir(BASEDIR)
failed = 0

for f in files:
  try: 
    audio = mutagen.File("%s/%s" % (BASEDIR, f))
  except mutagen.mp3.HeaderNotFoundError:
    print "Can't process: %s" % fn
    failed = failed + 1
    
  fn = f.replace(" -", "-")
  fn = fn.replace("- ", "-")
  fn = fn.replace(" ", "_")
  fn = re.sub("^0[\d]+_","",fn)

  artist=None
  title=None
  record = HTML_MAP.get(f, None)

  # can we just use the damn detail record?
  if record["detail"] != "":
    sp = record["detail"].split(" - ") 
    artist, title = sp[0], " - ".join(sp[1:]) # dumb.
    
  # well now we have to tear through the ID3 tags. sigh.
  # ---------- figure out artist ----------
  if audio.get("artist",None) != None:
    artist = audio.get("artist")
  else:
    # maybe they have TPE1 instead?
    if audio.get("TPE1",None):
      artist = audio.get("TPE1")
    else:
      if audio.get("\xa9ART", None):   # itunes 12 bullshit?
        artist = str(audio.get("\xa9ART"))
        
  if artist == None:
    # try html?
    if record != None:
      artist = record["artist"]

  # ---------- figure out title ----------
  if audio.get("title",None) != None:
    title = audio.get("title")
  else:
    # maybe they have TALB?
    if audio.get("TALB",None):
      title = audio.get("TALB")
    else:
      # maybe they have TIT2?
      if audio.get("TIT2",None):
        title = audio.get("TIT2")
      else:
        if audio.get("\xa9nam", None):
          title = audio.get("\xa9nam")
          
  if artist == None or title == None:
    print "%s: can't find artist or title! (a=%s, t=%s)" % (f, artist, title)
    print record
    failed = failed + 1
    continue

#  print "%s - %s.mp3" % (artist, title)
  title = re.sub(r' ',"",str(title)).rstrip("_").lstrip("_")
  newfile = "%s-%s.mp3" % (artist, title)
  #print "%s/%s --> %s/%s" % ( BASEDIR, f, BASEDIR, newfile )

  #os.rename(BASEDIR+"/"+f,BASEDIR+"/"+fn)

print "failed = %d " % failed
