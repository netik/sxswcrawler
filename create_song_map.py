#!/usr/bin/python
#
# Given a set of scraped artist files, attempt to map the audio URL to
# their band name and song title
#

import re
import os.path

CACHE_DIR = "./cache/artists"
bandre = re.compile(r'<meta property="twitter:title" content="([^"]*)">')
mp3re  = re.compile(r'<audio src="(http://audio.sxsw.com/\d+/mp3_by_artist_id/[^"]*.mp3)"></audio>')
scre   = re.compile(r'(https://soundcloud.com/[^"]*)"')
ytre   = re.compile(r'(https://www.youtube.com/[^"]*)"')

detailre = re.compile(r'<div class="artist-detail-bar">([^\<]*)</div>')

files = os.listdir(CACHE_DIR)

for f in files:

  artist=None
  audiourl=None
  detail = ""
  
  fh = open("%s/%s" % (CACHE_DIR, f))
    
  for line in fh:
    m = bandre.search(line)
    
    if m != None:
      artist = m.group(1)

    d = detailre.search(line)
    if d != None:
      detail = d.group(1)
      
    q = mp3re.search(line)
    if q != None:
      audiourl = q.group(1)

    # only go to these if mp3 isn't set
    if audiourl == None:
      q = scre.search(line)
      if q != None:
        audiourl = q.group(1)

    # only go to these if mp3 and sc isn't set
    # we prefer to take mp3 or soundcloud before switching to YT
    if audiourl == None:
      q = ytre.search(line)
      if q != None and audiourl == None:
        audiourl = q.group(1)

  fh.close()
    
  print "%s|%s|%s|%s" % (f, artist, audiourl, detail)

