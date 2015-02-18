#!/usr/bin/python

import os
import re 
import mutagen.mp3 
from mutagen.mp3 import * 


BASEDIR="/Volumes/field_photos/SXSW_2014_MP3s/soundcloud"
files = os.listdir(BASEDIR)

for f in files:
  try: 
    audio = mutagen.File("%s/%s" % (BASEDIR, f), easy=True)
  except mutagen.mp3.HeaderNotFoundError:
    print "Cannot process: %s" % fn

  fn = f.replace(" -", "-")
  fn = fn.replace("- ", "-")
  fn = fn.replace(" ", "_")
  fn = re.sub("^0[\d]+_","",fn)

  # all of these tracks are reversed, so take the last - if we have one.

  parts = fn.rsplit("-",1)
  artist = parts[1].replace(".mp3","").rstrip("_").lstrip("_")
  song = parts[0]

  print artist
  print song

  if audio.get("artist",None) != None:
    artist_id3 = audio.get("artist")
    if artist_id3 != artist:
      print "Has id3, but %s != %s" % ( artist_id3, artist)

  song = re.sub("^0[\d]-_","",song).rstrip("_").lstrip("_")
  song = re.sub("^0[\d]_-_","",song).rstrip("_").lstrip("_")
  song = re.sub("^0[\d]-","",song).rstrip("_").lstrip("_")

  newfile = artist + "-" + song + ".mp3"

  print BASEDIR+"/"+f
  print " --- > " + BASEDIR+"/"+newfile
  print
  #os.rename(BASEDIR+"/"+f,BASEDIR+"/"+fn)

