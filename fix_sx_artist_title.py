#!/usr/bin/python

import mutagen.mp3 
from mutagen.mp3 import * 
import os
import re

CACHEDIR = "./cache/artists"
SXMUSICDIR = "./music/sx"

def addID3artist(filen, artist):
  try:
    id3info = ID3(filen)
    id3info['ARTIST'] = artist
    print "\nID3 tags added"
  except InvalidTagError, err:
    print "\nInvalid ID3 tag: {0}".format(err)

artist_dir = os.listdir(CACHEDIR)

for f in artist_dir:
  # get the filename 
  if f.startswith("_2018"):
    # this is the magic line... 
    #<div class="artist-detail-bar">Curtis Roush - Getaway</div><audio src="http://audio.sxsw.com/2018/mp3_by_artist_id/91d753acba5dc63536c7bafcac434860cb3b808e696171961ed3f0e33ad2c697.mp3"></audio>

    html = open(os.path.join(CACHEDIR,f))

    mp3_filename = None
    mp3_title = None

    for line in html:
      m_title = re.search("artist-detail-bar\"\>([^\<]+)</div>",line)
      if m_title:
        mp3_title = m_title.group(1)

      m_filename = re.search("audio src=\"([^\"]+)\"",line)
      if m_filename:
        mp3_filename = m_filename.group(1)

    # do we have enough data to go on?
    if mp3_filename != None and mp3_title != None:
      print "%s OK - %s %s" % (f, mp3_title, mp3_filename)

      # filename cleanup
      mp3_filename = mp3_filename.replace("http://audio.sxsw.com/2018/mp3_by_artist_id/", "")

      # title cleanup
      mp3_title = mp3_title.lstrip().rstrip().replace(" ", "_")
      mp3_title = mp3_title + ".mp3"
      try:
        os.rename(os.path.join(SXMUSICDIR, mp3_filename), "music/sx/%s" % mp3_title)
      except:
        pass
    else:
      if mp3_filename == None and mp3_title != None:
        print "%s have mp3 but don't have title"
      else:
        if mp3_filename != None and mp3_title == None:
          print "%s don't have mp3 but have title"
#        else:
#          print "%s no MP3" % f

      
        
