#!/usr/bin/python

import io
import requests
import os.path
import re
import sys
import string

BASE_URL='http://schedule.sxsw.com'
CACHE_DIR="cache"

# debug all fetches
DEBUG=False

def fetch(url,fn,daynumber,nocache = True):
  # fetch a URL, but if we have the file on disk, return the file instead.
  # This prevents us from beating on the remote site while developing.
  if not os.path.isdir("%s/%s" % (CACHE_DIR, daynumber)):
    os.makedirs("%s/%s" % (CACHE_DIR, daynumber))

  cachefn = "%s/%s/%s" % (CACHE_DIR, daynumber, fn)
  print "fetch: %s" % cachefn

  if os.path.isfile(cachefn) and nocache == False:
    if DEBUG: 
      print "return cached content for url (%s)" % fn

    text = open(cachefn,'r').read()
    return text

  # lie. Alot. 
  headers = {'Accept'          : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
             'Accept-Charset'  : 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
             'Accept-Language' : 'en-US,en;q=0.8',
             'Cache-Control'   : 'max-age=0',
             'Host'            : 'schedule.sxsw.com',
             'Referer'         : 'http://schedule.sxsw.com/',
             'User-Agent'      : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.0.1364.68 Safari/537.22' } 

  print "fetch: %s --> %s " % (url, cachefn)

  r = requests.get(url, headers=headers)
  f = io.open(cachefn, 'w', encoding='utf8')
  f.write(r.text)
  f.close()
  print "  ... %d " % r.status_code
  return r.text 

def get_events(data):
  events=[]
  for line in data.split('\n'):
    m = re.search("href=\'(/2015/events/\w+)\'",line) 

    if m:
      events.append(m.group(1))
  return events


# http parameters

alphalist = list(string.ascii_lowercase)
alphalist.append('1')

for alpha in alphalist:
  #  http://schedule.sxsw.com/?conference=music&lsort=name&day=ALL&event_type=showcase
  eventpage = fetch("%s/?conference=music&lsort=name&day=ALL&a=%s" % ( BASE_URL, alpha ) ,"events_%s.html" % alpha, alpha, nocache = False)
  events = get_events(eventpage)

  # regexps for detecting content -- should really be in another stage. 

  ytRE = re.compile('(//www.youtube.com/embed/[a-zA-Z0-9_-]+)\'')
  scRE = re.compile('src=\'(https://w.soundcloud.com.+) ')
  mpRE = re.compile('file=(http://audio.sxsw.com/2014/mp3_by_artist_id/(\d+).mp3)')
  
  for event in events:
    if event.find("event_MS") == -1:
      continue

    detailurl = "%s%s" % (BASE_URL , event)
    detailpage = fetch(detailurl, "%s.html" % event.replace("/","_"), event, nocache = False)

    scM = scRE.search(detailpage)
    ytM = ytRE.search(detailpage)
    mpM = mpRE.search(detailpage)

    cachefn="cache/%s/%s.html" %  (alpha, event.replace("/","_") )

    if scM != None: 
      scurl = scM.group(1)
      print "%s soundcloud %s" % (cachefn, scurl.replace('\'',''))

    if ytM != None:
      yturl = ytM.group(1)
      print "%s youtube http:%s" % (cachefn, yturl)

    if mpM != None:
      mpurl = mpM.group(1)
      print "%s mp3 %s" % (cachefn, mpurl)

    if scM == None and ytM == None and mpM == None:
      print "%s none" % cachefn


