#!/usr/bin/python

import re
import os.path

CACHE_DIR ="../html_cache"
bandre = re.compile('<div class=\'data\'><h1>(.+)</h1>')
idre   = re.compile('<img alt="(\d+)"')

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

      print "%s - %s" % (id,artist)

