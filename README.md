SXSW Crawler 
=======================

This is a set of hacked-together scripts for crawling SXSW and getting
music for all the bands. The site format changes every year, different
sites change their APIs and shit breaks. There is no guarantee this
will work. It is, however, a good starting place. You may have to make
changes, but, there's enough here to hang yourself.

I recommend runnning this mid-Feburary. Artists are usually nailed
down by then.

The process (For me, anyway) works like this:

  1. Download all songs.
  2. Feed into iTunes
  3. Rate with iTunes rater (github.com/netik/iTunesRater)
  4. Take that library and convert it into a schedule  (./sxsw_to_ical.py)
  5. Take that schedule (as an ICS file) and put it into your 
     phone to have during the event. 

Caveats: I am not responsible for what you do with these scripts. Most
of the music is copyrighted and you shouldn't steal it. Please don't
abuse the bandwidth of any of these sites. 

There's a couple of changes for 2015, First off, we're breaking up the
job into easy to manage parts so that you don't end up having to run
the crawl multiple times.


1. Run the crawl to get data. You should only have to do this once. 

  cd scripts
  ./1_run_crawl.sh

  This will create data/crawl_log.txt which everything else will key
  off of.

  ./stage2.py

  This will parse the downloaded files and log to determine where the
  audio files are

  ./download_sx.py

  ./download_yt.py

  ./get_sc_data.py (see below for setup!)
  ./download_sc.py

  run these individually 
   

How does this work?
======================

Essentially we're reading their events pages, parsing them, and trying
to get MP3s. There are usually a few different sources of music:

SXSW MP3s
==========

(2013,2014) It used to be that they hosted MP3s for all of the bands
on the SXSW sites for review. These days there's maybe 40-60 songs on
the SXSW site, and the rest are on youtube or otherwise. But, we'll
download those directly.

2016 Update: SXSW seems to be hosting most of their music on their own
again. Yay!

Youtube 
========

We'll use jwz's youtubedown to get these files as mp4s. We'll then
convert them to mp3s later. 

Soundcloud
==========

Far more complicated but still possible. Soundcloud artists do not
have songs, they have artist data listed, but we want to hear them to
know if we should bother going to the show.

We need to find their most popular song and download it. Assumption:
"Most Popular" is the hit song that might sell you on the band. (Who
knows!)

Python Dependencies:
  easy_install requests
  easy_install soundcloud
  easy_install lxml
  easy_install ID3 -- or id3-py-1.2/ included in this directory

  Valid soundcloud API keys. Get them from Soundcloud and put them in
  a file called soundcloud_api_keys.py. make sure the file looks like
  this:

     client_id='xxxxx'
     client_secret='xxxxx'
Run: 
  ./get_sc_data.py

  That will build the sc metadata catalog. 

There are a whole series of scripts in these folders for cleaning up the
music/ directory. (rename_* and fix_*.) Using them is beyond the scope of 
this README. 

After you've imported and listened to all of the songs:

  ./sxsw_to_ical.py -h 

I usually rate 2 stars and 3 stars if I really want to go. Rarely, if
ever do I rate 4 or 5 stars unless the band is amazing. Note that the
sxsw_to_ical script processes ALL bands in iCal. It does not pick off
just the SXSW ratings. If you rate multiple songs for a single band,
it will use the HIGHEST rating you've given to that band. 

There is a bunch of other junk in here that frankly, I forget what
they do.

dedupe.sh* - apparently this was used to dedupe the crawl. dead?
fixnames.py* - I think I used this to rename the downloaded music. 
map_artists.py* - Maybe I used this to find more artists in the crawl
map_url_to_artist.py* - ??
rename_mp3_files.py* - tries to fixup MP3 
rename_no_spaces.py* - remove spaces from youtube files
rename_sc_tracks.py* - clean up soundcloud filenames

soundcloud-downloader.py* - I didn't write this, download files from
                            soundcloud, possibly broken

stage1.py* - first part of the fetcher

