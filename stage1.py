#!/usr/bin/python
#
# stage1.py
#
# SXSW Music Events Crawler
# J. Adams <jna@retina.net> 
# Last update 2/7/2016
#
# Crawl the SXSW site, downloading every artist and event page into a
# cache directory for later parsing by stage2.py
#

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
    print "makedir %s/%s" % (CACHE_DIR, daynumber)
    os.makedirs("%s/%s" % (CACHE_DIR, daynumber))

  cachefn = "%s/%s/%s" % (CACHE_DIR, daynumber, fn)
  print "fetch: %s" % cachefn

  if os.path.isfile(cachefn) and nocache == False:
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
    m = re.search("href=\'(/2016/events/\w+)\'",line) 

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
  for event in events:
    if event.find("event_MS") == -1:
      continue
    
    detailurl = "%s%s" % (BASE_URL , event)
    detailpage = fetch(detailurl, "%s.html" % event.replace("/","_"), event, nocache = False)

    # for now we will just fetch and print the name out. 
    cachefn="cache/%s/%s.html" %  (alpha, event.replace("/","_") )
    print "%s unkonw" % cachefn
