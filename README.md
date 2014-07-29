Biligrab
========

Yet another danmaku and video file downloader of Bilibili.

Integrated with most of the "black science".

4 independent ways to parse true source(s).

Auto concat and convert to MP4 file(s), direct integrate with Mukioplayer-Py-Mac(https://github.com/cnbeining/Mukioplayer-Py-Mac  , the Flash danmaku playing solution) and ABPlayer-HTML5-Mac(https://github.com/cnbeining/ABPlayerHTML5-Py--nix  , the HTML5 playing solution, preferred). 

An intergration with Danmaku2ass(https://github.com/m13253/danmaku2ass) is fulfilled by m13253 with biligrab-danmaku2ass(https://github.com/m13253/biligrab-danmaku2ass), which can convert danmaku to .ass file.

Usage
------
If you have a Bilibili account, set the cookie with https://github.com/dantmnf/biliupload/blob/master/getcookie.py  will help you to download some of the restricted videos.

python biligrab.py

>av

The aid, for http://www.bilibili.com/video/av1336405/, aid == 1336405 .

>P

Part number.

There are 3 ways you can input the number:

1: Part 1

1~3: Part 1,2,3

1,3,4,5: Part 1,3,4,5

You can mix those ways:
1~4, 6,7: Part 1,2,3,4,6,7.

>Source?

0: Use the original way that the player uses. Should gives you the original URL, but may fail if the original video is deleted, and may give you the Letv cloud or avgcideo.com backup.

1: Use the "CDN" API, the so-called "oversea acceleration". Should give you the acgvideo.com backup, but may return original address if video is not backup.

2: Force to retrieve the original URL, but would fail with videos that does not have "original source", like the "directly upload" with Letv cloud. Use Flvcd to parse the address. Use for for videos backuped with Letv cloud, but you prefer the original Sina address.

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

For history before V0.74, visit http://www.cnbeining.com/ , or check the code at https://gist.github.com/cnbeining/9605757/revisions  .