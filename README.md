Biligrab
========

Yet another danmaku and video file downloader of Bilibili.

Integrated with most of the "black science".

4 independent ways to parse true source(s).

Auto concat and convert to MP4 file(s), direct integrate with Mukioplayer-Py-Mac(https://github.com/cnbeining/Mukioplayer-Py-Mac  , the Flash danmaku playing solution) and ABPlayer-HTML5-Mac(https://github.com/cnbeining/ABPlayerHTML5-Py--nix  , the HTML5 playing solution, preferred). 

Interact and non-interact mode for different situations.

An intergration with Danmaku2ass(https://github.com/m13253/danmaku2ass) is fulfilled by m13253 with biligrab-danmaku2ass(https://github.com/m13253/biligrab-danmaku2ass), which can convert danmaku to .ass file.

Usage
------
If you have a Bilibili account, set the cookie with https://github.com/dantmnf/biliupload/blob/master/getcookie.py  will help you to download some of the restricted videos.

Interactive mode:

python biligrab.py

Or non-interact mode:

```python biligrab.py (-h) (-a) (-p) (-s) (-c) (-d) (-v)```

    Usage:
    
    python biligrab.py (-h) (-a) (-p) (-s) (-c) (-d) (-v)
    
    -h: Default: None
        Print this usage file.
    
    -a: Default: None
        The av number.
        If not set, Biligrab will use the falloff interact mode.
        
    -p: Default: 1
        The part number.
        Support "~", "," and mix use.
        Examples:
            Input        Output
              1           [1]
             1,2         [1, 2]
             1~3        [1, 2, 3]
            1,2~3       [1, 2, 3]
                 
    -s: Default: 0
    Source to download.
    0: The original API source, can be Letv backup,
       and can failed if the original video is not avalable(e.g., deleted)
    1: The CDN API source, "oversea accelerate".
       Can be MINICDN backup in Mainland China or oversea.
       Good to bypass some bangumi's limit.
    2: Force to use the original source.
       Use Flvcd to parase the video, but would fail if
       1) The original source DNE, e.g., some old videos
       2) The original source is Letvcloud itself.
       3) Other unknown reason(s) that stops Flvcd from parase the video.
    For any video that failed to parse, Biligrab will try to use Flvcd.
    (Mainly for oversea users regarding to copyright-restricted bangumies.)
    
    -c: Default: ./bilicookies
    The path of cookies.
    Use cookies to visit member-only videos.
    
    -d: Default: None
    Set the desired download software.
    Biligrab supports aria2c(16 threads), axel(20 threads), wget and curl by far.
    If not set, Biligrab will detect an avalable one;
    If none of those is avalable, Biligrab will quit.
    For more software support, please open an issue at https://github.com/cnbeining/Biligrab/issues/
    
    -v Default:None
        Set the desired download software.
    Biligrab supports ffmpeg by far.
    If not set, Biligrab will detect an avalable one;
    If none of those is avalable, Biligrab will quit.
    For more software support, please open an issue at https://github.com/cnbeining/Biligrab/issues/
    Make sure you include a *working* command line example of this software!
    

Requirement
-------
- Python 2.7
- aria2c
- curl
- ffmpeg

Author
-----
Beining, http://www.cnbeining.com/

License
-----
MIT license.

History
----
0.90: Fix if cannot get download URL for some reason(geo location, or API server error), try to use Flvcd to download video. 

0.89: Fix #4, force declare the varible, and set the path if not assigned. 

0.88: Fix #3, 2 typos.

0.87: Able to edit cookie path. Fix cannot read cookie.

0.86: Add non-interact mode, change API domain, fix #2.

0.81: Fix Flvcd module; When failed to concat, try to concat to flv; If failed, leave the original file; Delete some lines to make it easier to intregrate; Fix domain name

0.8: Fix the most recent change with APIs, with player biliInterface-201407302359. Use own key instead of AcDown's.

For history before V0.74, visit http://www.cnbeining.com/ , or check the code at https://gist.github.com/cnbeining/9605757/revisions  .