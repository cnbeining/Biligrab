Biligrab
========

Yet another automatic/semi-automatic/manual danmaku and video file downloader of Bilibili.

Integrated with most of the "black science". Good to bypass some copyright and geolocation restrictions.

6 independent ways to parse source(s)! Now with BilibiliPr!

Auto concat and convert to MP4 (or FLV, even nothing, if not possible) file(s), direct integrate with Mukioplayer-Py-Mac(https://github.com/cnbeining/Mukioplayer-Py-Mac  , the Flash danmaku playing solution) and ABPlayer-HTML5-Mac(https://github.com/cnbeining/ABPlayerHTML5-Py--nix  , the HTML5 playing solution, preferred). 

Interact and command line mode for different situations. ALso support slient mode.

Able to process single or multiple videos with easy grammar, or reading mylist.

Intergrated with Danmaku2ass(https://github.com/m13253/danmaku2ass, GPL v2) by m13253, able to convert danmaku to ASS subtitle. Both py2 and master branch avalable for better handling danmaku.

Able to export danmaku only.

Or, if you prefer, Biligrab can export a M3U file, with which you can play danmaku without waiting with players like MPlayer, MPC or VLC, etc. 

Comes with a built-in multi-part download, useful to reduce slow overheads.

Usage
------
If you have a Bilibili account, set the cookie with https://github.com/dantmnf/biliupload/blob/master/getcookie.py  will help you to download some of the restricted videos. Also you can do that by hand.

The file should looks like:

    DedeUserID=123456;DedeUserID__ckMd5=****************;SESSDATA=*******************

Interactive mode (Note some of the functions are not avalable via this mode):

python biligrab.py

Or command line mode:

    python biligrab.py (-h) (-a) (-p) (-s) (-c) (-d) (-v) (-l) (-e) (-b) (-m) (-n) (-u) (-t) (-r) (-q)
    
    -h: Default: None
        Print this usage file.
        
    -a: Default: None
        The av number.
        If not set, Biligrab will use the falloff interact mode.
        Support "~", "," and mix use.
        Examples:
            Input        Output
              1           [1]
             1,2         [1, 2]
             1~3        [1, 2, 3]
            1,2~3       [1, 2, 3]
            
    -p: Default: 0
        The part number.
        Able to use the same syntax as "-a".
        If set to 0, Biligrab will download all the avalable parts in the video.
        
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
       3) Other unknown reason(s) that stops Flvcd from parasing the video.
    For any video that failed to parse, Biligrab will try to use Flvcd.
    (Mainly for oversea users regarding to copyright-restricted bangumies.)
    If the API is blocked, Biligrab would fake the UA.
    3: (Not stable) Use the HTML5 API.
       This works for downloading some cached Letvcloud videos, but is slow, and would fail for no reason sometimes.
       Will retry if unavalable.
    4: Use Flvcd.
       Good to fight with oversea and copyright restriction, but not working with iQiyi.
       May retrive better quality video, especially for Youku.
    5: Use BilibiliPr.
       Good to fight with some copyright restriction that BilibiliPr can fix.
       Not always working though.
       
    -c: Default: ./bilicookies
    The path of cookies.
    Use cookies to visit member-only videos.
    
    -d: Default: None
    Set the desired download software.
    Biligrab supports aria2c(16 threads), axel(20 threads), wget and curl by far.
    If not set, Biligrab will detect an avalable one;
    If none of those is avalable, Biligrab will quit.
    For more software support, please open an issue at https://github.com/cnbeining/Biligrab/issues/
    
    -v: Default:None
    Set the desired concatenate software.
    Biligrab supports ffmpeg by far.
    If not set, Biligrab will detect an avalable one;
    If none of those is avalable, Biligrab will quit.
    For more software support, please open an issue at https://github.com/cnbeining/Biligrab/issues/
    Make sure you include a *working* command line example of this software!
    
    -l: Default: INFO
    Dump the log of the output for better debugging.
    Can be set to debug.
    
    -e: Default: 1
    Export Danmaku to ASS file.
    Fulfilled with danmaku2ass(https://github.com/m13253/danmaku2ass/tree/py2),
    Author: @m13253, GPLv3 License.
    *For issue with this function, if you think the problem lies on the danmaku2ass side,
    please open the issue at both projects.*
    If set to 1 or 2, Biligrab will use Danmaku2ass's py2 branch.
    If set to 3, Biligrab will use Danmaku2ass's master branch, which would require
    a python3 callable via 'python3'.
    If python3 not callable or danmaku2ass2/3 DNE, Biligrab will ask for action.
    
    -b: Default: None
    Set the probe software.
    Biligrab supports Mediainfo and FFprobe.
    If not set, Biligrab will detect an avalable one;
    If none of those is avalable, Biligrab will quit.
    For more software support, please open an issue at https://github.com/cnbeining/Biligrab/issues/
    Make sure you include a *working* command line example of this software!
    
    -m: Default: 0
    Only download the danmaku.
    
    -n: Default: 0
    Slient Mode.
    Biligrab will not ask any question.
    
    -u: Default: 0
    Export video link to .m3u file, which can be used with MPlayer, mpc, VLC, etc.
    Biligrab will export a m3u8 instead of downloading any video(s).
    Can be broken with sources other than 0 or 1.
    
    -t: Default: None
    The number of Mylist.
    Biligrab will process all the videos in this list.
    
    -q: Default: 3
    The thread number for downloading.
    Good to fix overhead problem.

Requirement
-------
- Python 2.7
- curl + None/aria2c/wget/axel
- ffmpeg
- mediainfo/ffprobe(for danmaku2ass)
- Python 3.x(only for danmaku2ass's python3 mode)

Author
-----
Beining, http://www.cnbeining.com/

License
-----
MIT license.

The Danmaku2ass(master) and Danmaku2ass(py2) part belongs to @m13253, GPLv3 license. Used under the authorization of the original author.

This program is provided **as is**, with absolutely no warranty.

Contributing
------------
Any contribution is welcome. 

For issues, it would be better to include the log output, which can be enabled by ```-l```. 

MAKE SURE YOU DELETE ANY SENSIVE INFORMATION THAT YOU DO NOT WANT TO SHARE PUBLICLY(E.G., IP ADDRESS, USERNAME, ETC.) BEFORE YOU POST ANYTHING!

*You can still send me the info privately via my email. PGP public key avalable at http://www.cnbeining.com/about/*

Any donation is welcome as well. Please get in touch with me: cnbeining[at]gmail.com .

History
----
0.98.6: Add BilibiliPr's API.

0.98.5: Add testing multi-part download, Change UA, Change error handling, Fix #13, #14.

0.98.4: Change UA, change to use best source, rewrite HTML5 API as in #11.

0.98.39: Change to download high quality Youku video, rewrite the error report and logging, retry if failed to fetch video, rewrite arguments.

0.98.3: Change default probe software to ffprobe; Fix error at resolution with danmaku export only; Better debugging output; Fix error with danmaku2ass(py2)'s float problem; Beautify code.

0.98.29: Add ver. number: Fix: do not fail to fake UA when use normal api #9, thanks to @arition 's help.

0.98.28: Fix typo; Fix error with CLI mode.

0.98.27: Update as #7.

0.98.26: Add more support of broken sources.

0.98.25: Add **some** support of M3U export of Sina source and source that was broken.

0.98.2: Add **some** support of M3U export of non-Sina source.

0.98.1: Add mylist download.

0.98: Fix error with special characters in filename; Add export to M3U file to use players like MPlayer, VLC, etc.; Rewrite video URL API logic; Fix error with Danmaku2ASS(main); Error handling with ffprobe

0.97.9: Rewrite URL retrive logic; Divide URL retrive to functions; Change to ```.format()``` style; Add HTML5 API; Directly use Flvcd; Beautify ERROR logging.

0.97.5: Add (auto) download all the pages; Auto PEP-8.

0.97: Slient mode; Multiple video mode; Functions beautify; More error handling.

0.96.2: Merge pull request #6, #7: Optimize Danmaku2ASS parameters and exception handling, thanks to @m13253's help; Fix error when cookie does not exist, thanks to @m13253's report.

0.96.1: Add exception handling regarding to Danmaku2ass2; Fix vid guessing.

0.96: Add danmaku2ass(py2) to handle ass convertion without Python 3; Add the danmaku2ass dependencies check mode for safety; Add "danmaku only" mode to depreciate BiligrabLite; Change the default live time to 8 sec as the update from upstream; Update the license info.

0.95: Add danmaku2ass, able to convert danmaku to ass file; Fix axel error.

0.94: Add faking UA to bypass blocking; Add auto-generate UA; Rewrite API logic.

0.93: Fix error when handling filenames containing ```/\&```, thanks to @solimot 's report; Add log mode, which can be enabled by ```-l 1 ```; Clean multiple headers; Rearrange global varibles.

0.92: Fix wrongly exit when downloading multiple parts.

0.91: Add support to axel, wget, curl and easy way to add more support; Add easy way to add more concat support; Able to select desired software and auto detect; Change dependencies check; Code beauty.

0.90: Fix if cannot get download URL for some reason(geo location, or API server error), try to use Flvcd to download video. 

0.89: Fix #4, force declare the varible, and set the path if not assigned. 

0.88: Fix #3, 2 typos.

0.87: Able to edit cookie path. Fix cannot read cookie.

0.86: Add non-interact mode, change API domain, fix #2.

0.81: Fix Flvcd module; When failed to concat, try to concat to flv; If failed, leave the original file; Delete some lines to make it easier to intregrate; Fix domain name

0.8: Fix the most recent change with APIs, with player biliInterface-201407302359. Use own key instead of AcDown's.

For history before V0.74, visit http://www.cnbeining.com/ , or check the code at https://gist.github.com/cnbeining/9605757/revisions  .