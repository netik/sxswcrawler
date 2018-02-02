#!/usr/bin/python
#
# this gets the first song of every artist
#

import soundcloud
import requests
import json
import re 
import sys

sys.path.append(".")
from Timer import Timer
from soundcloud_api_keys import * 

def ap(s):
  try:
    out = s.encode('ascii', 'ignore')
  except:
    out = s.decode('utf8')
  return out

client = soundcloud.Client(client_id=client_id)

headers = {'Accept'          : 'text/json',
           'Accept-Charset'  : 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Language' : 'en-US,en;q=0.8',
           'Cache-Control'   : 'max-age=0',
           'User-Agent'      : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.0.1364.68 Safari/537.22' } 

# as it turns out, we missed every single soundcloud song this year. Go get them anyway. 
f = open("data/download_queue.txt","r")
outf = open("data/sc_data.txt","w+")

for line in f: 
  parts = line.split(" ")

  ml = re.search("(http[s]*://soundcloud\.com/[a-zA-Z0-9_\- ]+)", line)

  if ml != None: 
    url = "http://api.soundcloud.com/resolve.json?url=%s&client_id=%s" % ( ml.group(0), client_id )
    try:
      with Timer() as t:
        print "open: %s" % url 
        r = requests.get(url, headers=headers)
        udata = json.loads(r.text)
    except ValueError:
      print "json decode failed - SC failure or api rate limit?"
      continue

    # /users/id/tracks
    try:
      print "get tracks"
      tracks = client.get("/users/%s/tracks" % udata['id'])
    except KeyError:
      print "skip (no uid): %s" % url
      continue
    except requests.exceptions.HTTPError:
      print "HTTP error: %s" % url
      continue
    
    # no tracks? 
    if len(tracks) == 0:
      print "skip (notracks): %s" % url
      continue

    besttrack = None
    cnt = 0 

    try: 

      for track in tracks:
        if besttrack == None:
          besttrack = track

        if track.playback_count > cnt:
          besttrack = track
          cnt = track.playback_count

    except AttributeError:
      besttrack = track

    try:
      user = client.get("/users/%d" % udata['id'])
    except requests.exceptions.HTTPError:
      print "HTTP error (/users get): %s" % url
      continue
      
    print ap(user.username)

    print >> outf, "%s|%d|%d|%s|%s|%s|%s" % ( ap(ml.group(0)), 
                                              udata['id'], 
                                              besttrack.id,
                                              ap(besttrack.permalink_url),
                                              ap(parts[0]), 
                                              user.username.encode('utf-8'), 
                                              besttrack.title.encode('utf-8')) 
  else:
    print "skip (no_url_in_line): %s" % line.rstrip()

  sys.stdout.flush()


