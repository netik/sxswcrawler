#!/usr/bin/python

import os.path

BASEDIR="music/external_drive"

for fn in os.listdir(BASEDIR):
  oldfn = fn
  fn = fn.replace("[u'","")
  fn = fn.replace("']","")

  fn = fn.replace("[u\"","")
  fn = fn.replace("\"]","")

  if fn.find(".mp3") == -1:
    fn = "%s.mp3" % fn 

  print "%s -> %s "  % (oldfn, fn)
  os.rename("%s/%s" % (BASEDIR,oldfn),
            "%s/%s" % (BASEDIR, fn))


