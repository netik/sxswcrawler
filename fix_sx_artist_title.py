#!/usr/bin/python

import mutagen.mp3 
from mutagen.mp3 import * 
import os
import re

def addID3artist(filen, artist):
  try:
    id3info = ID3(filen)
    id3info['ARTIST'] = artist
    print "\nID3 tags added"
  except InvalidTagError, err:
    print "\nInvalid ID3 tag: {0}".format(err)

f = open("data/mp3_missed.txt")

htmlfile=""
for line in f:
  # get the filename 
  m = re.search("file=(.*\.mp3)",line) 

  if m:
    url = m.group(1)
    parts = line.split(":")
    cachefile = parts[0]

    cache_f = open(cachefile,"r")

    for line in cache_f:
      m = re.search(r"\content=\'(.*)\' name=\'twitter\:title\'",line)
      ofile = os.path.basename(url)

      if m:
         artist=m.group(1).replace("&amp;","&")
         if artist == "": 
           print "WARNING: no artist %s"  % ofile
         else:
           print "%s --> %s" % ("music/sx/%s" % ofile,artist)
           addID3artist("music/sx/%s" % ofile, artist)

