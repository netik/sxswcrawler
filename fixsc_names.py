#!/usr/bin/python

import os.path

BASEDIR="music/sc"

# this is the output of the 
f = open("data/sc_download_log.txt", "r")

urlindex={}

# map URLs to filenames 
for line in f:
  if line.startswith("http"):
    lasturl = line.rstrip()

  if line.startswith("Downloading:"):
    parts = line.split(": ")
    urlindex[lasturl] = parts[1].rstrip()
    print "%s = %s" % (lasturl, parts[1].rstrip())

f.close()

# map files to artist/title
f = open("data/sc_data.txt","r")

for line in f: 
  parts = line.split("|")
  try:
    oldfn= urlindex[parts[3]]
  except:
    print "can't find %s" % parts[3]

  artist = parts[5].replace("-"," ").replace(" ","_").rstrip()
  title = parts[6].replace("-"," ").replace(" ","_").rstrip()
  
  outfn = "%s-%s.mp3" % (artist,title)
  print "%s -> %s"  % (urlindex[parts[3]], outfn)

  try: 
    os.rename("%s/%s" % (BASEDIR,oldfn),
            "%s/%s" % (BASEDIR, outfn))
  except: 
    print "passing on %oldfn"


