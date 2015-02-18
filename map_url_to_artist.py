#!/usr/bin/python

import re
import os.path

CACHE_DIR ="../html_cache"
bandre = re.compile('<div class=\'data\'><h1>(.+)</h1>')
idre   = re.compile('<img alt="(\d+)"')
#le=http://audio.sxsw.com/2014/mp3_by_artist_id/5694.mp3
mp3re  = re.compile(r'http://audio.sxsw.com/2014/mp3_by_artist_id/\d+.mp3')
scre   = re.compile(r'http://audio.sxsw.com/2014/mp3_by_artist_id/\d+.mp3')
ytre   =

for day in range(6,16):
  files = os.listdir("%s/%d" % (CACHE_DIR, day))

  for f in files:
    if f.find(".html") > -1 and f[0] == "_":
      artist=""
      audiourl=""

      fh = open("%s/%d/%s" % (CACHE_DIR, day, f))

      for line in fh:
        m = bandre.search(line)

        if m != None:
          artist = m.group(1)

        q = mp3re.search(line)
        if q != None:
          audiourl = q.group(0)

      fh.close()

      print "%s|%s" % (artist,audiourl)

