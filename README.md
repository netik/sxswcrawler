SXSW Crawler 
=======================

This is a set of scripts for crawling SXSW and getting music for all
the bands. The site format changes every year, different sites change
their APIs and shit breaks. There is no guarantee this will work. 

However, it's an excellent starting place for music discovery. 

What's new?
=============

There's a couple of changes for 2015, First off, I'm breaking up the
job into easy to manage parts so that you don't end up having to run
the crawl multiple times. Second, I'm making the code much more
modular.

I recommend runnning this mid-Feburary. Artists are usually nailed
down by then.

THE PROCESS
============

I think we've developed an excellent way to discover music at a
festival that regularly hosts over 1500 bands. We're going to take a
bit of a big-data approach here, and process music faster than any A&R
person can.

Much credit for this process goes to jwz who wrote youtubedown and
worked on this with me throughout the last 5 years of SXSW.

The process works like this:

  1. Crawl SXSW. Get all of the HTML for music events during the festival.
  2. Break the work queue down by type (soundcloud, raw mp3, youtube)
  3. Download all of thesongs in each type using different mechanisms
  4. Feed into iTunes
  5. Rate with iTunesRater (github.com/netik/iTunesRater)
  6. Take that library and convert it into a schedule  (./sxsw_to_ical.py)
  7. Take that schedule (as an ICS file) and put it into your phone to have during the event. 
  8. Go see some damn music. 

Caveats: I am not responsible for what you do with these scripts. Most
of the music is copyrighted and you shouldn't steal it. Please don't
abuse the bandwidth of any of the sites or services involved here.

Installation
=============

Python 2.7 required

Dependencies: 

```
  easy_install requests
  easy_install soundcloud
  easy_install mutagen
  easy_install lxml
  easy_install ID3 -- or id3-py-1.2/ included in this directory
  easy_install fuzzy   # for sxsw to ical fuzzy matching
```


youtubedown (get from www.jwz.org/hacks/youtubedown) 
 - Make sure to get a current version of this. It should be in your $PATH

You will also need Valid soundcloud API keys. Get them from Soundcloud
and put them in a file called soundcloud_api_keys.py. make sure the
file looks like this:

```
   client_id='xxxxx'
   client_secret='xxxxx'
```

get_sc_data will use them as part of the soundcloud "best song" determination.

Running
===============

Run the crawl to get data. You should only have to do this once. 

```
  # Crawl the site!
  ./1_run_crawl.sh
```

  This will create data/queue.txt which everything else will key
  off of.

```
  # parse the data set for possible downloads
  ./stage2.py
```

This will parse the downloaded files and log to determine where the
audio files are.

Now, download them.

```
  # Get SXSW mp3 files
  ./download_sx.py 
```

Now, you should have a big, fat directory (music/) full of mp3 files.
Run "rename_mp 3_files.py" to rename them from "xxxx.mp3" to "artist -
title.mp3" with proper ID3 tags.

The rename script will try to derive the proper artist and title
name from the SXSW web pages. If it can't do that it'll fall back to
the MP3 ID3 information.

If that doesn't work at all, we'll leave the file alone and you'll be
stuck with the nnnn.mp3 filename, but hopefully not. At that point,
you might want to resort to either exiftool or iTunes to resolve these
issues for you.

Now, get the other file types. Historically, youtube and sound cloud
make up a a small fragment of artists available from sxsw.

Youtube files:

```
  ./download_yt.py
  ./fix_yt_namse.py
```

Soundcloud

```
  ./get_sc_data.py (see below for setup!)
  ./download_sc.py
```

More about the files 
======================

Essentially we're reading their events pages, parsing them, and trying
to get MP3s. There are usually a few different sources of music:


As of Feb, 2016, I'm seeing 884 official sxsw MP3s, 103 youtube files,
and 37 soundcloud entries.

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

  ./get_sc_data.py

ONLY AFTER stage1.py has finished. This will build the sc metadata catalog. 

There are a whole series of scripts in these folders for cleaning up the
music/ directory. (rename_* and fix_*.) Using them is beyond the scope of 
this README. 

What do I do afterwards?
===========================

After you've imported, rated, and listened to all of the songs, go
make your personal calendar.

  ./sxsw_to_ical.py -h 

I usually rate 2 stars and 3 stars if I really want to go. Rarely, if
ever do I rate 4 or 5 stars unless the band is amazing. Note that the
sxsw_to_ical script processes ALL bands in iCal. It does not pick off
just the SXSW ratings. If you rate multiple songs for a single band,
it will use the HIGHEST rating you've given to that band. 

Other Files
=============
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

