#!/usr/bin/python
#
# Build an ICS file of bands of interest at SXSW using the on-disk cache
# to avoid ratelimits from SXSW
#
# derived from jwz's sxsw_scape.pl, but now in Python.
#
#  - First, generate a list of bands of interest by getting a list
#    of all iartists with at least one song ranked 3 stars or higher
#    in iTunes.  Also, all music videos.
#
#  - Keep only events with bands of interest.
#
#  - Build ICS from the existing data
#
#  - Pull full event descriptions from sxsw.com (instead of only short
#    excerpts).
#
#  - Set location of each event to include the street address of the venue.
#
#  - Update each event to note other dates on which this band is playing
#    (so that you can look at an event on Wednesday and know that you
#    will also have an opportunity to see this band on Thursday).

# Before importing the generated .ics file into iCal, I strongly suggest:
#
#  - Check "Preferences / Advanced / Turn on time zone support" or
#    else  things will import with the wrong times.
#  - Set "Preferences / Alerts / Events" to "None" or else every event
#    you import will have a default alert added to it.
#
# Import it into its own calendar to make it easy to nuke it and start over.

from HTMLParser import HTMLParser
import argparse
import arrow
from dateutil import tz
import fuzzy
import io
import os
import pickle
import re
import requests
import sys
import time
import cProfile
import hashlib
import json

# config
DEFAULT_YEAR="2015"
zone = 'US/Central'
# -- end config -- 

iartists = {}
venues = {}
events = {}
icsentries = []
badtime = 0 
ics_seq = 0 
perfdates = {}

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ' '.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def simplify(s):
  s = s.upper()
  orig = s
  s = re.sub(r'\b(a|an|and|in|of|on|for|the|with|dj|los|le|les|la)\b', '',s,flags=re.IGNORECASE)
  s = re.sub(r'[^A-Z\d]','',s)     # lose non-alphanumeric
  s = re.sub(r'(.)1+','\1',s)   # collapse consecutive letters ("xx" -> "x")
  if (s  ==  ''):
    s = orig 
  return s

def sxsw_datefix(a):
  # Oh, come on.  When the sxsw.com web site says "Thu Mar 15, 1:00 AM"
  # it actually means Mar 16!!  They consider the day to end at 2 AM
  # or something.  So adjust the day if the hour is "early"
  if a == None:
   return None

  if a.hour < 6:
    a = a.replace(day=a.day + 1)

  return a

def score_artist(artist):
  global iartists

  if artist == None: 
    return -1

  if not iartists.has_key(simplify(artist)):
    return -1

  # we are storing a tokenized form of the artist with the score. This lookup is then O(2)
  # calc score
  s_min=10
  s_max=-1
  s_tot=0

  for s in iartists[simplify(artist)]:
    s_tot = s_tot + s
    if s < s_min: 
      s_min = s
    if s > s_max: 
      s_max = s

  s_avg = s_tot / len(iartists[simplify(artist)])

  if args.scoremode == 'max':
    score = s_max
  elif args.scoremode == 'min':
    score = s_min
  else:
    score = s_avg

  return score

def valid_artist(artist):
  ''' determine if an artist exists and if the artist scores high enough '''
  global iartists

  score = score_artist(artist)
  if score == -1:
    return False

  if score >= args.stars:
    return True

  return False


def fetch(url, fn, nocache=False):
  # fetch a URL, but if we have the file on disk, return the file instead.
  # This prevents us from beating on the remote site while developing.
  cachefn="%s/venues/%s" % (args.cachedir, fn)
  if not os.path.isdir("%s/venues" % args.cachedir):
     os.mkdir("%s/venues" % args.cachedir)

  if os.path.isfile(cachefn) and nocache == False:
    if args.verbose: 
      print "return cached content for venue url (%s)" % fn

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

def get_venue(venue, venue_url):
  global venues
  
  text = fetch(venue_url, venue.replace(" ", "_"))
  m = re.search(r'<div class=\'venue-details\'>.<h1 class=\'venue-title\'>(.+)</h1>.<h3>(.+?)</h3>', text, re.DOTALL)

  if m: 
    addr = strip_tags(m.group(2).lstrip().rstrip())
    venues[venue.replace(" ", "_")] = addr
    return addr 
  else:
    venues[venue.replace(" ", "_")] = ""
    return None

def parse_event(filename):
  global args
  global events
  global perfdates
  global badtime
  global venues

  hometown = genre = description = artist = artisturl = timeend = time_s = time_e = a_start = a_end = venue = venueurl = None

  fh = open(filename,"r")
  text = fh.read()

  m = re.search(r'<div class=\'title\'>.<h1>(.+)</h1>', text, re.DOTALL)
  if m:
    artist = m.group(1).lstrip().rstrip()

  m = re.search(r'<div id=\'detail_time\'>(.+?)</div>', text, re.DOTALL)
  if m:
    time_htm = m.group(1).lstrip().rstrip().replace('\n','')
    time_s = strip_tags(time_htm)
    time_s = re.sub(' +', ' ', time_s)

    if time_s.find("-") > 0:
      time_sp = time_s.split("-")
      time_s = time_sp[0]
      time_p = time_sp[0].split(" ")

      time_e = " ".join(time_p[0:3]) + time_sp[1]

    try:
      a_start = arrow.get(time_s.rstrip() + ", " + DEFAULT_YEAR,'ddddd, MMMM D h:mmA, YYYY')
      a_start.replace(tzinfo=tz.gettz('US/Central'))
    except arrow.parser.ParserError:
      a_start = None    
      if args.verbose:
        print >> sys.stderr, "failed to parse start time: %s " % time_s 
      badtime = badtime + 1

    if time_e != None: 
      try:
        a_end = arrow.get(time_e.rstrip() + ", " + DEFAULT_YEAR,'ddddd, MMMM D h:mmA, YYYY')
        a_end.replace(tzinfo=tz.gettz('US/Central'))
      except arrow.parser.ParserError:
        a_end = None    
        if args.verbose:
          print >> sys.stderr, "failed to parse end time: %s " % time_e
    else:
       a_end = a_start

  m = re.search(r'<a class=\'detail_venue\' href=\'(.+?)\'>(.+?)</a>', text, re.DOTALL)
  if m:
    venue = m.group(2).lstrip().rstrip().replace('\n','')
    venueurl = m.group(1).lstrip().rstrip().replace('\n','')

    if not venues.has_key(venue):
       get_venue(venue, venueurl)

  m = re.search(r'<div class=\'block description\'>(.+?)</div>', text, re.DOTALL)
  if m:
    description = strip_tags(m.group(1)).lstrip().rstrip()
    description = re.sub("Show the rest$", "", description, re.IGNORECASE)

  if description == None:
    m = re.search(r'<div class=\'short\'>(.+?)</div>', text, re.DOTALL)
    if m:
      description = strip_tags(m.group(1)).lstrip().rstrip()

  m = re.search(r'<div class=\'info\'>.<a href=\"(.+?)\"', text, re.DOTALL)
  if m:
    artisturl = strip_tags(m.group(1))

  m = re.search(r'<div class=\'block\'>.<span class=\'label\'>Genre</span>.<div class=\'info\'>.<a href="(.+?)">(.+?)</a>', text, re.DOTALL)
  if m:
    genre = m.group(2).replace("\n","")

  m = re.search(r'<span class=\'label\'>From</span>.<div class=\'info\'>(.+?)</div>', text, re.DOTALL)
  if m:
    hometown = m.group(1).replace("\n","")

  # hack the URL together
  url = os.path.basename(filename).replace("_2015_events_event_","")
  url = "http://schedule.sxsw.com/2015/events/event_%s" % url
  url = url.replace(".html", "")
  print url 

  events[filename] = { "artist": artist, 
                       "artisturl": artisturl,
                       "time_s": time_s, 
                       "time_start" : sxsw_datefix(a_start),
                       "time_end" : sxsw_datefix(a_end),
                       "genre": genre,
                       "venue": venue,
                       "description": description,
                       "url": url,
                       "venueurl": venueurl,
                       "hometown": hometown } 

  if a_start != None: 
    if not perfdates.has_key(simplify(artist)):
      perfdates[simplify(artist)] = []
    perfdates[simplify(artist)].append({ "start": sxsw_datefix(a_start), "end": sxsw_datefix(a_end), "venue": venue})

def get_rated_iartists(stars=3):
  global args
  artistre = re.compile('<key>Artist</key><string>(.+)</string>')
  ratere  = re.compile('<key>Rating</key><integer>(\d+)</integer>')
  itunes_xml = args.itunesxml
  iartists = {}
  
  ARTIST_CACHEFILE = "%s/rated_artists-%s.pickle" % (args.cachedir, hashlib.sha256(args.itunesxml).hexdigest())

  if os.path.exists(ARTIST_CACHEFILE) and args.cache == True: 
    st = os.stat(ARTIST_CACHEFILE)
    print >> sys.stderr, "Using existing iTunes artist rating cachefile, created at %s" % time.ctime(st.st_ctime)
    cf = open(ARTIST_CACHEFILE, "r")
    iartists = pickle.load(cf)
    cf.close()
    return iartists

  print >> sys.stderr, "Generating new iTunes artist rating cachefile..."
  f = open(itunes_xml,"r")

  artist = ""
  for line in f:
    # this dict resets our key to ensure we don't bleed into next artist
    if line.find('<key>Track ID</key>') > -1:
      artist = ''

    # we won't remember the artist if the song is disabled. 
    if line.find('<key>Disabled</key><true/>') > -1 and args.ignoredisabled == True:
      artist = ''

    m = artistre.search(line)
    if m:
      artist = m.group(1)

    m = ratere.search(line)
    if m and artist != '':
      if iartists.has_key(simplify(artist.lstrip().rstrip())):
        iartists[simplify(artist.lstrip().rstrip())].append(int(m.group(1)) / 20)
      else:
        iartists[simplify(artist.lstrip().rstrip())] = [ (int(m.group(1)) / 20) ] 

  if args.verbose:
    print >> sys.stderr, "Producing new cachefile %s" % ARTIST_CACHEFILE

  cf = open(ARTIST_CACHEFILE, "w")
  pickle.dump(iartists, cf)
  cf.close()

  return iartists

def ical_quote(s,nowrap=False):
  if s == None: 
    return ""

  s = re.sub(r'\s+$','',s, re.DOTALL | re.M)
  s = re.sub(r'([\"\\,;])',r'\\\1',s, re.DOTALL | re.M)
  s = re.sub(r'\r\n',r'\n',s, re.DOTALL | re.M)
  s = re.sub(r'\r',r'\n',s, re.DOTALL | re.M)
  s = re.sub(r'\n',r'\\n\n', s, re.DOTALL | re.M)
  s = re.sub(r'\\n',r'  \\n', s, re.DOTALL | re.M)
  # combine multiple blank lines into one.
  s = re.sub(r'(\n *\n)( *\n)+', r'\1', s, re.DOTALL | re.M)

  if nowrap: 
    s = re.sub(r'\\n', r'\\n\n ',s, re.DOTALL)
    out = s
  else: 
    p = maxwidth=80
    out = ""
    for c in s: 
      if c != '\n':
        out = out + c
      p = p - 1
      if p <= 0 and (c != '\\') and (out[len(out)-1] != "\\"):
        p=maxwidth
        out=out + "\n " 
    
  return out

def make_vcal(out):
  global zone
  global icsentries

  if args.verbose: 
    print >> sys.stderr, "writing %s" % out 

  f = open (out,"w")
  c = "\n".join(['BEGIN:VCALENDAR',
                  'VERSION:2.0',
                  'PRODID:-//Apple Inc.//iCal 5.0.1//EN',
                  'METHOD:PUBLISH',
                  'X-WR-CALNAME:SXSW 2015',
                  'X-WR-TIMEZONE:' + zone,
                  'CALSCALE:GREGORIAN',
                  'BEGIN:VTIMEZONE',
                  'TZID:US/Central',
                  'BEGIN:DAYLIGHT',
                  'TZOFFSETFROM:-0600',
                  'RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU',
                  'DTSTART:20070311T020000',
                  'TZNAME:CDT',
                  'TZOFFSETTO:-0500',
                  'END:DAYLIGHT',
                  'BEGIN:STANDARD',
                  'TZOFFSETFROM:-0500',
                  'RRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU',
                  'DTSTART:20071104T020000',
                  'TZNAME:CST',
                  'TZOFFSETTO:-0600',
                  'END:STANDARD',
                  'END:VTIMEZONE','\n'])

  c = c + "\n".join(icsentries)

  c = c + 'END:VCALENDAR'

  c = re.sub(r'(\n )(\n )+',r'\1',c)
  c = re.sub(r'  +',r' ',c)
  print >> f, c
  f.close();

def make_ics(event):
  global ics_seq
  global zone
  ics_seq = ics_seq + 1

  uid=hashlib.sha256(event['artist']+'|'+event['time_s']).hexdigest()

  t = event['time_start']
  dtstart = "TZID=%s:%04d%02d%02dT%02d%02d%02d" % (zone,
                                                    t.year, 
                                                    t.month, 
                                                    t.day, 
                                                    t.hour, 
                                                    t.minute,
                                                    t.second)

  t = event['time_end']
  if t: 
    dtend    = "TZID=%s:%04d%02d%02dT%02d%02d%02d" % (zone,
                                                       t.year, 
                                                       t.month, 
                                                       t.day, 
                                                       t.hour, 
                                                       t.minute,
                                                       t.second)
  else:
    # ah fuck.
    print  >> sys.stderr, "WARNING: event %s has no end time" % event['artist']
    dtend = dtstart
    

  t = arrow.utcnow()
  dtstamp = "%04d%02d%02dT%02d%02d%02dZ" % (t.year, 
                                            t.month, 
                                            t.day, 
                                            t.hour, 
                                            t.minute,
                                            t.second)

  loc = event['venue'] + "\n" + venues[event['venue'].replace(" ","_")] + "\nAustin, TX 78701\n"

# this doesn't seem to want to work, even if we replay the old data at ical. 
#  struct_loc = 'VALUE=URI;X-ADDRESS=515 E 6th St\\nAustin TX 78701;X-APPLE-RADIUS=25.63865019644897;X-TITLE=Flamingo Cantina:geo:30.266390,-97.737772'
#  struct_loc = 'VALUE=URI;X-ADDRESS=' + venues[event['venue'].replace(" ","_")] + "\\nAustin, TX 78701" + ';X-APPLE-RADIUS=25;X-TITLE=' + event['venue']

  if event['description']:
    desc = event['description']
  else:
    print >> sys.stderr, "WARNING: No description for %s" % event['artist']
    desc = "No description."

  if event['artisturl'] != None:
    desc = desc.rstrip() + ".\\n" + event['artisturl']

  # find multiple dates, if any
  md = ""
  if len( perfdates[simplify(event['artist'])] ) > 1:
    md = u"Multiple Shows:\n"
    for e in perfdates[simplify(event['artist'])]:

      if e['start'].format('X') != event['time_start'].format('X'):
        md = "".join([ md,e['start'].format(u'MM/DD h:mm a '), e['venue'],"\n" ])

    md = md + "\n"
  md = md.encode('utf-8')
  stars = '\xe2\x98\x85' * score_artist(event['artist'])
  desc = "".join([ event['genre'] + " " + stars, "\n", event['hometown'], "\n\n" , md, desc])

  entry = "\n".join([ 
          'BEGIN:VEVENT',
          'UID:'		+ ical_quote(uid),
          'DTSTAMP:'		+ ical_quote (dtstamp),
          'SEQUENCE:%d'		% ics_seq,
          'LOCATION:'		+ ical_quote (loc),
#          'X-APPLE-STRUCTURED-LOCATION;' + struct_loc,
          'SUMMARY:'		+ ical_quote (event['artist']),
          'DTSTART;'		+ dtstart,
          'DTEND;'		+ dtend,
          'URL:'		+ ical_quote (event['url']),
          'DESCRIPTION:'	+ ical_quote(desc), 
          'CLASS:PUBLIC',
          'CATEGORIES:BAND',
          'STATUS:CONFIRMED',
          'END:VEVENT' ]);

  return entry

if __name__ == "__main__":
  def main(): 
    global args
    global events
    global iartists 
    global icsentries

    if args.verbose:
      print >> sys.stderr, "Fetching iTunes..."
    iartists = get_rated_iartists(args.stars)
    if args.verbose:
      print >> sys.stderr, "Found %d qualifying artists in iTunes." % len(iartists)

    # pass #1: open every file
    # get band, artist, venue, description, venue address to a dict
    # all playing locations for the band
    for file in os.listdir(args.cachedir + "/events"):
      parse_event(os.path.join(args.cachedir + "/events", file))

    valid=0

    # pass #2 find bands 
    for k, v in events.iteritems():
      if valid_artist(v.get('artist')):
        if (v.get('time_start',None) != None) or args.notime == True:
            
          icsentries.append(make_ics(events[k]))
          valid = valid + 1 

    print >>sys.stderr,  "%d calendarable / %d artists in ical / %d artists in sxsw / %d bad sxsw events (notime)" % (valid, len(iartists), len(events), badtime)

    # save stats as json
    f = open (args.outputics + ".json", "w")
    print >>f, (json.dumps({"valid" :  valid, "iartists": len(iartists), "events": len(events), "badtime": badtime }, sort_keys=True))
    f.close();

    make_vcal(args.outputics)

parser = argparse.ArgumentParser(description="Process the SXSW 2015 Music cache and generate a calendar based on your favorite iTunes songs. Requires that you've already crawled the site with stage1.py.")
parser.add_argument('--itunesxml', '-i',  dest='itunesxml',help='The name of your XML file. Default: ~/Music/iTunes/iTunes Library.xml', default="~/Music/iTunes/iTunes Library.xml")

parser.add_argument('--outputics', '-o',  dest='outputics',help='Ignore disabled tracks in iTunes. Default: sxsw2015.ics', default="sxsw2015.ics")

parser.add_argument('--stars', '-s', metavar='stars', type=int, nargs="?", default=3, help='minimum number of stars (iTunes rating) for consideration. Default: 3')

parser.add_argument('--nocache', '-nc',dest='cache', help='Disables the artist cache for this read, rebuilding the cache for later use. Default: True', action='store_false', default=True)

parser.add_argument('--cachedir', '-c', metavar='directorys', nargs="?", default=os.getcwd() + "/cache", help="Location of cache directory. Default: " + os.getcwd() + "/cache")

parser.add_argument('--notime',  '-nt', dest='notime',help='Include events with no times (bad idea for calendars, good for debug.) Default: False', action='store_true', default=False)
parser.add_argument('--novenue', '-nv', dest='novenue',help='Include events with no venue. Default: False', action='store_true', default=False)
parser.add_argument('--scoremode', '-m',  dest='scoremode',help='Score mode: When multiple ratings are present for an artist\'s songs, which one do we use? Default: avg', choices=['avg','min','max','last'], default='avg')
parser.add_argument('--nodisabled', '-nd',  dest='ignoredisabled',help='Ignore disabled tracks in iTunes. Default: False', action='store_true', default=False)




parser.add_argument('--verbose', '-v',  dest='verbose',help='Verbose mode. better for debugging.', action='store_true', default=False)

args = parser.parse_args()

main()

 



