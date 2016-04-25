#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Beining --<ACICFG>
# Purpose: Yet another danmaku and video file downloader of Bilibili.
# Created: 11/06/2013
# 
# Biligrab is licensed under MIT license (https://github.com/cnbeining/Biligrab/blob/master/LICENSE)
# 
# Copyright (c) 2013-2015

'''
Biligrab
Beining@ACICFG
cnbeining[at]gmail.com
http://www.cnbeining.com
https://github.com/cnbeining/Biligrab
MIT license
'''

from ast import literal_eval
import sys
import os
from StringIO import StringIO
import gzip
import urllib
import urllib2
import math
import json
import commands
import subprocess
import hashlib
import getopt
import logging
import traceback
import threading
import Queue

from xml.dom.minidom import parseString

try:
    from danmaku2ass2 import *
except Exception:
    pass

global vid, cid, partname, title, videourl, part_now, is_first_run, APPKEY, SECRETKEY, LOG_LEVEL, VER, LOCATION_DIR, VIDEO_FORMAT, convert_ass, is_export, IS_SLIENT, pages, IS_M3U, FFPROBE_USABLE, QUALITY, IS_FAKE_IP, FAKE_IP

cookies, VIDEO_FORMAT = '', ''
LOG_LEVEL, pages, FFPROBE_USABLE = 0, 0, 0
APPKEY = 'c1b107428d337928'
SECRETKEY = 'ea85624dfcf12d7cc7b2b3a94fac1f2c'
VER = '0.98.91'
FAKE_UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.52 Safari/537.36'
FAKE_HEADER = {
    'User-Agent': FAKE_UA,
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache', 
    'pianhao': '%7B%22qing%22%3A%22super%22%2C%22qtudou%22%3A%22real%22%2C%22qyouku%22%3A%22super%22%2C%22q56%22%3A%22super%22%2C%22qcntv%22%3A%22super%22%2C%22qletv%22%3A%22super2%22%2C%22qqiyi%22%3A%22real%22%2C%22qsohu%22%3A%22real%22%2C%22qqq%22%3A%22real%22%2C%22qhunantv%22%3A%22super%22%2C%22qku6%22%3A%22super%22%2C%22qyinyuetai%22%3A%22super%22%2C%22qtangdou%22%3A%22super%22%2C%22qxunlei%22%3A%22super%22%2C%22qsina%22%3A%22high%22%2C%22qpptv%22%3A%22super%22%2C%22qpps%22%3A%22high%22%2C%22qm1905%22%3A%22high%22%2C%22qbokecc%22%3A%22super%22%2C%22q17173%22%3A%22super%22%2C%22qcuctv%22%3A%22super%22%2C%22q163%22%3A%22super%22%2C%22q51cto%22%3A%22high%22%2C%22xia%22%3A%22auto%22%2C%22pop%22%3A%22no%22%2C%22open%22%3A%22no%22%7D'}
LOCATION_DIR = os.path.dirname(os.path.realpath(__file__))

#----------------------------------------------------------------------
def list_del_repeat(list):
    """delete repeated items in a list, and keep the order.
    http://www.cnblogs.com/infim/archive/2011/03/10/1979615.html"""
    l2 = []
    [l2.append(i) for i in list if not i in l2]
    return(l2)

#----------------------------------------------------------------------
def logging_level_reader(LOG_LEVEL):
    """str->int
    Logging level."""
    return {
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG,
        'WARNING': logging.WARNING,
        'FATAL': logging.FATAL
    }.get(LOG_LEVEL)

#----------------------------------------------------------------------
def calc_sign(string):
    """str/any->str
    return MD5."""
    return str(hashlib.md5(str(string).encode('utf-8')).hexdigest())

#----------------------------------------------------------------------
def read_cookie(cookiepath):
    """str->list
    Original target: set the cookie
    Target now: Set the global header"""
    global BILIGRAB_HEADER
    try:
        cookies_file = open(cookiepath, 'r')
        cookies = cookies_file.readlines()
        cookies_file.close()
        # print(cookies)
        return cookies
    except Exception:
        logging.warning('Cannot read cookie, may affect some videos...')
        return ['']

#----------------------------------------------------------------------
def clean_name(name):
    """str->str
    delete all the dramas in the filename."""
    return (str(name).strip().replace('\\',' ').replace('/', ' ').replace('&', ' ')).replace('-', ' ')

#----------------------------------------------------------------------
def send_request(url, header, is_fake_ip):
    """str,dict,int->str
    Send request, and return answer."""
    global IS_FAKE_IP
    data = ''
    if IS_FAKE_IP == 1:
        header['X-Forwarded-For'] = FAKE_IP
        header['Client-IP'] = FAKE_IP
        header['X-Real-IP'] = FAKE_IP
    try:
        #logging.debug(header)
        request = urllib2.Request(url, headers=header)
        response = urllib2.urlopen(request)
        data = response.read()
    except urllib2.HTTPError:
        logging.info('ERROR!')
        return ''
    if response.info().get('Content-Encoding') == 'gzip':
        buf = StringIO(response.read())
        f = gzip.GzipFile(fileobj=buf)
        data = f.read()
    #except Exception:
        #raise URLOpenException('Cannot open URL! Raw output:\n\n{output}'.format(output = command_result[1]))
    #print(request.headers)
    logging.debug(data)
    return data

#----------------------------------------------------------------------
def mylist_to_aid_list(mylist):
    """str/int->list"""
    data = send_request('http://www.bilibili.com/mylist/mylist-{mylist}.js'.format(mylist = mylist), FAKE_HEADER, IS_FAKE_IP)
    #request = urllib2.Request('http://www.bilibili.com/mylist/mylist-{mylist}.js'.format(mylist = mylist), headers = FAKE_HEADER)
    #response = urllib2.urlopen(request)
    aid_list = []
    #data = response.read()
    for i in data.split('\n')[-3].split(','):
        if 'aid' in i:
            aid_list.append(i.split(':')[1])
    return aid_list


    
#----------------------------------------------------------------------
def find_cid_api(vid, p, cookies):
    """find cid and print video detail
    str,int?,str->str,str,str,str
    TODO: Use json."""
    global cid, partname, title, videourl, pages
    cid = 0
    title , partname , pages, = '', '', ''
    if str(p) is '0' or str(p) is '1':
        #str2Hash = 'appkey={APPKEY}&id={vid}&type=xml{SECRETKEY}'.format(APPKEY = APPKEY, vid = vid, SECRETKEY = SECRETKEY)
        #biliurl = 'https://api.bilibili.com/view?appkey={APPKEY}&id={vid}&type=xml&sign={sign}'.format(APPKEY = APPKEY, vid = vid, SECRETKEY = SECRETKEY, sign = calc_sign(str2Hash))
        biliurl = 'https://api.bilibili.com/view?appkey={APPKEY}&id={vid}&type=xml'.format(APPKEY = APPKEY, vid = vid, SECRETKEY = SECRETKEY)

    else:
        #str2Hash = 'appkey={APPKEY}&id={vid}&page={p}&type=xml{SECRETKEY}'.format(APPKEY = APPKEY, vid = vid, p = p, SECRETKEY = SECRETKEY)
        #biliurl = 'https://api.bilibili.com/view?appkey={APPKEY}&id={vid}&page={p}&type=xml&sign={sign}'.format(APPKEY = APPKEY, vid = vid, SECRETKEY = SECRETKEY, p = p, sign = calc_sign(str2Hash))
        biliurl = 'https://api.bilibili.com/view?appkey={APPKEY}&id={vid}&page={p}&type=xml'.format(APPKEY = APPKEY, vid = vid, SECRETKEY = SECRETKEY, p = p)
    logging.debug('BiliURL: ' + biliurl)
    videourl = 'http://www.bilibili.com/video/av{vid}/index_{p}.html'.format(vid = vid, p = p)
    logging.info('Fetching api to read video info...')
    data = ''
    try:
        #request = urllib2.Request(biliurl, headers=BILIGRAB_HEADER)
        #response = urllib2.urlopen(request)
        #data = response.read()
        data = send_request(biliurl, BILIGRAB_HEADER, IS_FAKE_IP)
        logging.debug('Bilibili API: ' + data)
        dom = parseString(data)
        for node in dom.getElementsByTagName('cid'):
            if node.parentNode.tagName == "info":
                cid = node.toxml()[5:-6]
                logging.info('cid is ' + cid)
                break
        for node in dom.getElementsByTagName('partname'):
            if node.parentNode.tagName == "info":
                partname = clean_name(str(node.toxml()[10:-11]))
                logging.info('partname is ' + partname)# no more /\ drama
                break
        for node in dom.getElementsByTagName('title'):
            if node.parentNode.tagName == "info":
                title = clean_name(str(node.toxml()[7:-8])).decode("utf-8")
                logging.info((u'Title is ' + title).encode(sys.stdout.encoding))
        for node in dom.getElementsByTagName('pages'):
            if node.parentNode.tagName == "info":
                pages = clean_name(str(node.toxml()[7:-8]))
                logging.info('Total pages is ' + str(pages))
        return [cid, partname, title, pages]
    except Exception:  # If API failed
        logging.warning('Cannot connect to API server! \nIf you think this is wrong, please open an issue at \nhttps://github.com/cnbeining/Biligrab/issues with *ALL* the screen output, \nas well as your IP address and basic system info.\nYou can get these data via "-l".')
        logging.debug('API Data: ' + data)
        return ['', '', '', '']

#----------------------------------------------------------------------
def find_cid_flvcd(videourl):
    """str->None
    set cid."""
    global vid, cid, partname, title
    logging.info('Fetching webpage with raw page...')
    #request = urllib2.Request(videourl, headers=FAKE_HEADER)
    data = send_request(videourl, FAKE_HEADER, IS_FAKE_IP)
    #request.add_header('Accept-encoding', 'gzip')
    #try:
        #response = urllib2.urlopen(request)
    #except urllib2.HTTPError:
        #logging.info('ERROR!')
        #return ''
    #if response.info().get('Content-Encoding') == 'gzip':
        #buf = StringIO(response.read())
        #f = gzip.GzipFile(fileobj=buf)
        #data = f.read()
    data_list = data.split('\n')
    logging.debug(data)
    # Todo: read title
    for lines in data_list:
        if 'cid=' in lines:
            cid = lines.split('&')
            cid = cid[0].split('=')
            cid = cid[-1]
            logging.info('cid is ' + str(cid))
            break

#----------------------------------------------------------------------
def check_dependencies(download_software, concat_software, probe_software):
    """None->str,str,str
    Will give softwares for concat, download and probe.
    The detection of Python3 is located at the end of Main function."""
    concat_software_list = ['ffmpeg', 'avconv']
    download_software_list = ['aria2c', 'axel', 'wget', 'curl']
    probe_software_list = ['ffprobe', 'mediainfo']
    name_list = [[concat_software,
                  concat_software_list],
                 [download_software,
                  download_software_list],
                 [probe_software,
                  probe_software_list]]
    for name in name_list:
        if name[0].strip().lower() not in name[1]:  # Unsupported software
            # Set a Unsupported software,  not blank
            if len(name[0].strip()) != 0:
                logging.warning('Requested Software not supported!\n         Biligrab only support these following software(s):\n         ' + str(name[1]) + '\n         Trying to find available one...')
            for software in name[1]:
                output = commands.getstatusoutput(software + ' --help')
                if str(output[0]) != '32512':  # If exist
                    name[0] = software
                    break
        if name[0] == '':
            logging.fatal('Cannot find software in ' + str(name[1]) + ' !')
            exit()
    return name_list[0][0], name_list[1][0], name_list[2][0]

#----------------------------------------------------------------------
def download_video_link(part_number, download_software, video_link, thread_single_download):
    """set->str"""
    logging.info('Downloading #{part_number}...'.format(part_number = part_number))
    if download_software == 'aria2c':
        cmd = 'aria2c -c -U "{FAKE_UA}" -s{thread_single_download} -x{thread_single_download} -k1M --out {part_number}.flv "{video_link}"'
    elif download_software == 'wget':
        cmd = 'wget -c -A "{FAKE_UA}" -O {part_number}.flv "{video_link}"'
    elif download_software == 'curl':
        cmd = 'curl -L -C - -A "{FAKE_UA}" -o {part_number}.flv "{video_link}"'
    elif download_software == 'axel':
        cmd = 'axel -U "{FAKE_UA}" -n {thread_single_download} -o {part_number}.flv "{video_link}"'
    cmd = cmd.format(part_number = part_number, video_link = video_link, thread_single_download = thread_single_download, FAKE_UA = FAKE_UA)
    logging.debug(cmd)
    return cmd

#----------------------------------------------------------------------
def execute_cmd(cmd):
    """"""
    return_code = subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if return_code != 0:
        logging.warning('ERROR')
    return return_code

def execute_sysencode_cmd(command):
    """execute cmd with sysencoding"""
    os.system(command.decode("utf-8").encode(sys.stdout.encoding))

#----------------------------------------------------------------------
def concat_videos(concat_software, vid_num, filename):
    """str,str->None"""
    global VIDEO_FORMAT,title
    if concat_software == 'ffmpeg':
        f = open('ff.txt', 'w')
        ff = ''
        cwd = os.getcwd()
        for i in range(vid_num):
            ff += 'file \'{cwd}/{i}.flv\'\n'.format(cwd = cwd, i = i)
        # ff = ff.encode("utf8")
        f.write(ff)
        f.close()
        logging.debug(ff)
        logging.info('Concating videos...')

        execute_sysencode_cmd('ffmpeg -f concat -i ff.txt -c copy "' + filename + '".mp4')
        VIDEO_FORMAT = 'mp4'
        if os.path.isfile((str(i) + '.mp4').decode("utf-8")):
            try:
                # os.remove('ff.txt')
                print((str(i) + '.flv').decode("utf-8"))
                os.remove((str(i) + '.flv').decode("utf-8"))
                for i in range(vid_num):
                    os.remove((str(i) + '.flv').decode("utf-8"))
                    #execute_sysencode_cmd('rm -r ' + str(i) + '.flv')
                logging.info('Done, enjoy yourself!')
            except Exception:
                logging.warning('Cannot delete temporary files!')
                return ['']
        else:
            print('ERROR: Cannot concatenate files, trying to make flv...')
            execute_sysencode_cmd('ffmpeg -f concat -i ff.txt -c copy "' + filename + '".flv')
            VIDEO_FORMAT = 'flv'
            if os.path.isfile((str(i) + '.flv').decode("utf-8")):
                logging.warning('FLV file made. Not possible to mux to MP4, highly likely due to audio format.')
                #execute_sysencode_cmd('rm -r ff.txt')
                # os.remove('ff.txt')
                print(('ff.txt').decode("utf-8"))
                os.remove(('ff.txt').decode("utf-8"))
                for i in range(vid_num):
                    #execute_sysencode_cmd('rm -r ' + str(i) + '.flv')
                    os.remove((str(i) + '.flv').decode("utf-8"))
            else:
                logging.error('Cannot concatenate files!')
    elif concat_software == 'avconv':
        pass

#----------------------------------------------------------------------
def process_m3u8(url):
    """str->list
    Only Youku."""
    url_list = []
    data = send_request(url, FAKE_HEADER, IS_FAKE_IP)
    if data == '':
        logging.error('Cannot download required m3u8!')
        return []
    #request = urllib2.Request(url, headers=BILIGRAB_HEADER)
    #try:
        #response = urllib2.urlopen(request)
    #except Exception:
        #logging.error('Cannot download required m3u8!')
        #return []
    #data = response.read()
    #logging.debug(data)
    data = data.split()
    if 'youku' in url:
        return [data[4].split('?')[0]]

#----------------------------------------------------------------------
def make_m3u8(video_list):
    """list->str
    list:
    [(VIDEO_URL, TIME_IN_SEC), ...]"""
    TARGETDURATION = int(max([i[1] for i in video_list])) + 1
    line = '#EXTM3U\n#EXT-X-TARGETDURATION:{TARGETDURATION}\n#EXT-X-VERSION:2\n'.format(TARGETDURATION = TARGETDURATION)
    for i in video_list:
        line += '#EXTINF:{time}\n{url}\n'.format(time = str(i[1]), url = i[0])
    line += '#EXT-X-ENDLIST'
    logging.debug('m3u8: ' + line)
    return line

#----------------------------------------------------------------------
def find_video_address_html5(vid, p, header):
    """str,str,dict->list
    Method #3."""
    api_url = 'http://www.bilibili.com/m/html5?aid={vid}&page={p}'.format(vid = vid, p = p)
    data = send_request(api_url, header, IS_FAKE_IP)
    if data == '':
        logging.error('Cannot connect to HTML5 API!')
        return []
    #request = urllib2.Request(api_url, headers=header)
    #url_list = []
    #try:
        #response = urllib2.urlopen(request)
    #except Exception:
        #logging.error('Cannot connect to HTML5 API!')
        #return []
    #data = response.read()
    #Fix #13
    #if response.info().get('Content-Encoding') == 'gzip':
        #data = gzip.GzipFile(fileobj=StringIO(data), mode="r").read()
    #logging.debug(data)
    info = json.loads(data.decode('utf-8'))
    raw_url = info['src']
    if 'error.mp4' in raw_url:
        logging.error('HTML5 API returned ERROR or not available!')
        return []  #As in #11
    if 'm3u8' in raw_url:
        logging.info('Found m3u8, processing...')
        return process_m3u8(raw_url)
    return [raw_url]

#----------------------------------------------------------------------
def find_video_address_force_original(cid, header):
    """str,str->str
    Give the original URL, if possible.
    Method #2."""
        # Force get oriurl
    #sign_this = calc_sign('appkey={APPKEY}&cid={cid}{SECRETKEY}'.format(APPKEY = APPKEY, cid = cid, SECRETKEY = SECRETKEY))
    api_url = 'http://interface.bilibili.com/player?'
    #data = send_request(api_url + 'appkey={APPKEY}&cid={cid}&sign={sign_this}'.format(APPKEY = APPKEY, cid = cid, SECRETKEY = SECRETKEY, sign_this = sign_this), header, IS_FAKE_IP)
    data = send_request(api_url + 'appkey={APPKEY}&cid={cid}}'.format(APPKEY = APPKEY, cid = cid, SECRETKEY = SECRETKEY), header, IS_FAKE_IP)
    #request = urllib2.Request(api_url + 'appkey={APPKEY}&cid={cid}&sign={sign_this}'.format(APPKEY = APPKEY, cid = cid, SECRETKEY = SECRETKEY, sign_this = sign_this), headers=header)
    #response = urllib2.urlopen(request)
    #data = response.read()
    #logging.debug('interface responce: ' + data)
    data = data.split('\n')
    for l in data:
        if 'oriurl' in l:
            originalurl = str(l[8:-9])
            logging.info('Original URL is ' + originalurl)
            return originalurl
    logging.warning('Cannot get original URL! Chances are it does not exist.')
    return ''

#----------------------------------------------------------------------
def find_link_flvcd(videourl):
    """str->list
    Used in method 2 and 5."""
    logging.info('Finding link via Flvcd...')
    data = send_request('http://www.flvcd.com/parse.php?' + urllib.urlencode([('kw', videourl)]) + '&format=super', FAKE_HEADER, IS_FAKE_IP)

    #request = urllib2.Request('http://www.flvcd.com/parse.php?' +
                              #urllib.urlencode([('kw', videourl)]) + '&format=super', headers=FAKE_HEADER)
    #request.add_header('Accept-encoding', 'gzip')
    #response = urllib2.urlopen(request)
    #data = response.read()
    #if response.info().get('Content-Encoding') == 'gzip':
        #buf = StringIO(data)
        #f = gzip.GzipFile(fileobj=buf)
        #data = f.read()
    data_list = data.split('\n')
    #logging.debug(data)
    for items in data_list:
        if 'name' in items and 'inf' in items and 'input' in items:
            c = items
            rawurlflvcd = c[59:-5]
            rawurlflvcd = rawurlflvcd.split('|')
            return rawurlflvcd

#----------------------------------------------------------------------
def find_video_address_pr(cid, quality, header):
    """str,str->list
    The API provided by BilibiliPr."""
    logging.info('Finding link via BilibiliPr...')
    api_url = 'http://pr.lolly.cc/P{quality}?cid={cid}'.format(quality = quality, cid = cid)
    data = send_request(api_url, header, IS_FAKE_IP)
    
    #request = urllib2.Request(api_url, headers=header)
    #try:
        #response = urllib2.urlopen(request, timeout=3)
        #data = response.read()
    #except Exception:
        #logging.warning('No response!')
        #return ['ERROR']
    #logging.debug('BilibiliPr API: ' + data)
    if '!' in data[0:2]:
        logging.warning('API returned 404!')
        return ['ERROR']
    else:
        rawurl = []
        originalurl = ''
        dom = parseString(data)
        for node in dom.getElementsByTagName('durl'):
            url = node.getElementsByTagName('url')[0]
            rawurl.append(url.childNodes[0].data)
        return rawurl

#----------------------------------------------------------------------
def find_video_address_normal_api(cid, header, method, convert_m3u = False):
    """str,str,str->list
    Change in 0.98: Return the file list directly.
    Method:
    0: Original API
    1: CDN API
    2: Original URL API - Divided in another function
    3: Mobile API - Divided in another function
    4: Flvcd - Divided in another function
    5: BilibiliPr
     [(VIDEO_URL, TIME_IN_SEC), ...]
    """
    if method == '1':
        api_url = 'http://interface.bilibili.com/v_cdn_play?'
    else:  #Method 0 or other
        api_url = 'http://interface.bilibili.com/playurl?'
    if QUALITY == -1:
        #sign_this = calc_sign('appkey={APPKEY}&cid={cid}{SECRETKEY}'.format(APPKEY = APPKEY, cid = cid, SECRETKEY = SECRETKEY))
        #interface_url = api_url + 'appkey={APPKEY}&cid={cid}&sign={sign_this}'.format(APPKEY = APPKEY, cid = cid, SECRETKEY = SECRETKEY, sign_this = sign_this)
        interface_url = api_url + 'appkey={APPKEY}&cid={cid}'.format(APPKEY = APPKEY, cid = cid, SECRETKEY = SECRETKEY)
    else:
        #sign_this = calc_sign('appkey={APPKEY}&cid={cid}&quality={QUALITY}{SECRETKEY}'.format(APPKEY = APPKEY, cid = cid, SECRETKEY = SECRETKEY, QUALITY = QUALITY))
        #interface_url = api_url + 'appkey={APPKEY}&cid={cid}&quality={QUALITY}&sign={sign_this}'.format(APPKEY = APPKEY, cid = cid, SECRETKEY = SECRETKEY, sign_this = sign_this, QUALITY = QUALITY)
        interface_url = api_url + 'appkey={APPKEY}&cid={cid}&quality={QUALITY}}'.format(APPKEY = APPKEY, cid = cid, SECRETKEY = SECRETKEY, QUALITY = QUALITY)
    logging.info(interface_url)
    data = send_request(interface_url, header, IS_FAKE_IP)
    #request = urllib2.Request(interface_url, headers=header)
    #logging.debug('Interface: ' + interface_url)
    #response = urllib2.urlopen(request)
    #data = response.read()
    #logging.debug('interface API: ' + data)
    for l in data.split('\n'):  # In case shit happens
        if 'error.mp4' in l or 'copyright.mp4' in l:
            logging.warning('API header may be blocked!')
            return ['API_BLOCKED']
    rawurl = []
    originalurl = ''
    dom = parseString(data)
    if convert_m3u:
        for node in dom.getElementsByTagName('durl'):
            length = node.getElementsByTagName('length')[0]
            url = node.getElementsByTagName('url')[0]
            rawurl.append((url.childNodes[0].data, int(int(length.childNodes[0].data) / 1000) + 1))
    else:
        for node in dom.getElementsByTagName('durl'):
            url = node.getElementsByTagName('url')[0]
            rawurl.append(url.childNodes[0].data)
    return rawurl

#----------------------------------------------------------------------
def find_link_you_get(videourl):
    """str->list
    Extract urls with you-get."""
    command_result = commands.getstatusoutput('you-get -u {videourl}'.format(videourl = videourl))
    logging.debug(command_result)
    if command_result[0] != 0:
        raise YougetURLException('You-get failed somehow! Raw output:\n\n{output}'.format(output = command_result[1]))
    else:
        url_list = command_result[1].split('\n')
        for k, v in enumerate(url_list):
            if v.startswith('http'):
                url_list = url_list[k:]
                break
        #url_list = literal_eval(url_list_str)
        logging.debug('URL_LIST:{url_list}'.format(url_list = url_list))
        return list(url_list)

#----------------------------------------------------------------------
def get_video(oversea, convert_m3u = False):
    """str->list
    A full parser for getting video.
    convert_m3u: [(URL, time_in_sec)]
    else: [url,url]"""
    rawurl = []
    if oversea == '2':
        raw_link = find_video_address_force_original(cid, BILIGRAB_HEADER)
        rawurl = find_link_flvcd(raw_link)
    elif oversea == '3':
        rawurl = find_video_address_html5(vid, p, BILIGRAB_HEADER)
        if rawurl == []:  #As in #11
            rawurl = find_video_address_html5(vid, p, FAKE_HEADER)
    elif oversea == '4':
        rawurl = find_link_flvcd(videourl)
    elif oversea == '5':
        rawurl = find_video_address_pr(cid, 1080, BILIGRAB_HEADER)
        if '404' in rawurl[0]:
            logging.info('Using lower quality...')
            rawurl = find_video_address_pr(cid, 720, BILIGRAB_HEADER)
            if '404' in rawurl[0]:
                logging.error('Failed!')
                rawurl = []
            else:
                pass
        elif 'ERROR' in rawurl[0]:
            logging.info('Wait a little bit...')
            time.sleep(5)
            rawurl = find_video_address_pr(cid, 1080, BILIGRAB_HEADER)
    elif oversea == '6':
        raw_link = find_video_address_force_original(cid, BILIGRAB_HEADER)
        rawurl = find_link_you_get(raw_link)
    else:
        rawurl = find_video_address_normal_api(cid, BILIGRAB_HEADER, oversea, convert_m3u)
        if 'API_BLOCKED' in rawurl[0]:
            logging.warning('API header may be blocked! Using fake one instead...')
            rawurl = find_video_address_normal_api(cid, FAKE_HEADER, oversea, convert_m3u)
    return rawurl

#----------------------------------------------------------------------
def get_resolution(filename, probe_software):
    """str,str->list"""
    resolution = []
    filename = filename + '.' + VIDEO_FORMAT
    try:
        if probe_software == 'mediainfo':
            resolution = get_resolution_mediainfo(filename)
        if probe_software == 'ffprobe':
            resolution = get_resolution_ffprobe(filename)
        logging.debug('Software: {probe_software}, resolution {resolution}'.format(probe_software = probe_software, resolution = resolution))
        return resolution
    except Exception:  # magic number
        return[1280, 720]

#----------------------------------------------------------------------
def get_resolution_mediainfo(filename):
    """str->list
    [640,360]
    path to dimention"""
    resolution = str(os.popen('mediainfo \'--Inform=Video;%Width%x%Height%\' "' +filename +'"').read()).strip().split('x')
    return [int(resolution[0]), int(resolution[1])]

#----------------------------------------------------------------------
def get_resolution_ffprobe(filename):
    '''str->list
    [640,360]'''
    width = ''
    height = ''
    cmnd = ['ffprobe', '-show_format', '-show_streams', '-pretty', '-loglevel', 'quiet', filename]
    p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # print filename
    out, err = p.communicate()
    if err:
        print err
        return None
    try:
        for line in out.split():
            if 'width=' in line:
                width = line.split('=')[1]
            if 'height=' in line:
                height = line.split('=')[1]
    except Exception:
        return None
    # return width + 'x' + height
    return [int(width), int(height)]

#----------------------------------------------------------------------
def get_url_size(url):
    """str->int
    Get remote URL size by reading Content-Length.
    In bytes."""
    site = urllib.urlopen(url)
    meta = site.info()
    return int(meta.getheaders("Content-Length")[0])

#----------------------------------------------------------------------
def getvideosize(url, verbose=False):
    try:
        if url.startswith('http:') or url.startswith('https:'):
            ffprobe_command = ['ffprobe', '-icy', '0', '-loglevel', 'repeat+warning' if verbose else 'repeat+error', '-print_format', 'json', '-select_streams', 'v', '-show_format', '-show_streams', '-timeout', '60000000', '-user-agent', BILIGRAB_UA, url]
        else:
            ffprobe_command = ['ffprobe', '-loglevel', 'repeat+warning' if verbose else 'repeat+error', '-print_format', 'json', '-select_streams', 'v', '-show_streams', url]
        logcommand(ffprobe_command)
        ffprobe_process = subprocess.Popen(ffprobe_command, stdout=subprocess.PIPE)
        try:
            ffprobe_output = json.loads(ffprobe_process.communicate()[0].decode('utf-8', 'replace'))
        except KeyboardInterrupt:
            logging.warning('Cancelling getting video size, press Ctrl-C again to terminate.')
            ffprobe_process.terminate()
            return 0, 0
        width, height, widthxheight, duration, total_bitrate = 0, 0, 0, 0, 0
        try:
            if dict.get(ffprobe_output, 'format')['duration'] > duration:
                duration = dict.get(ffprobe_output, 'format')['duration']
        except Exception:
            pass
        for stream in dict.get(ffprobe_output, 'streams', []):
            try:
                if duration == 0 and (dict.get(stream, 'duration') > duration):
                        duration = dict.get(stream, 'duration')
                if dict.get(stream, 'width')*dict.get(stream, 'height') > widthxheight:
                    width, height = dict.get(stream, 'width'), dict.get(stream, 'height')
                if dict.get(stream, 'bit_rate') > total_bitrate:
                    total_bitrate += int(dict.get(stream, 'bit_rate'))
            except Exception:
                pass
        if duration == 0:
            duration = int(get_url_size(url) * 8 / total_bitrate)
        return [[int(width), int(height)], int(float(duration))+1]
    except Exception as e:
        logorraise(e)
        return [[0, 0], 0]

#----------------------------------------------------------------------
def convert_ass_py3(filename, probe_software, resolution = [0, 0]):
    """str,str->None
    With danmaku2ass, branch master.
    https://github.com/m13253/danmaku2ass/
    Author: @m13253
    GPLv3
    A simple way to do that.
    resolution_str:1920x1080"""
    xml_name = os.path.abspath(filename + '.xml')
    ass_name = filename + '.ass'
    logging.info('Converting danmaku to ASS file with danmaku2ass(main)...')
    logging.info('Resolution is %dx%d' % (resolution[0], resolution[1]))
    if resolution == [0, 0]:
        logging.info('Trying to get resolution...')
        resolution = get_resolution(filename, probe_software)
    logging.info('Resolution is %dx%d' % (resolution[0], resolution[1]))
    if execute_sysencode_cmd('python3 %s/danmaku2ass3.py -o %s -s %dx%d -fs %d -a 0.8 -dm 8 %s' % (LOCATION_DIR, ass_name, resolution[0], resolution[1], int(math.ceil(resolution[1] / 21.6)), xml_name)) == 0:
        logging.info('The ASS file should be ready!')
    else:
        logging.error('''Danmaku2ASS failed.
        Head to https://github.com/m13253/danmaku2ass/issues to complain about this.''')

#----------------------------------------------------------------------
def convert_ass_py2(filename, probe_software, resolution = [0, 0]):
    """str,str->None
    With danmaku2ass, branch py2.
    https://github.com/m13253/danmaku2ass/tree/py2
    Author: @m13253
    GPLv3"""
    logging.info('Converting danmaku to ASS file with danmaku2ass(py2)...')
    xml_name = filename + '.xml'
    if resolution == [0, 0]:
        logging.info('Trying to get resolution...')
        resolution = get_resolution(filename, probe_software)
    logging.info('Resolution is {width}x{height}'.format(width = resolution[0], height = resolution[1]))
    #convert_ass(xml_name, filename + '.ass', resolution)
    try:
        Danmaku2ASS(xml_name, filename + '.ass', resolution[0], resolution[1],
                    font_size = int(math.ceil(resolution[1] / 21.6)), text_opacity=0.8, duration_marquee=8.0)
        logging.info('INFO: The ASS file should be ready!')
    except Exception as e:
        logging.error('''Danmaku2ASS failed: %s
        Head to https://github.com/m13253/danmaku2ass/issues to complain about this.'''% e)
        logging.debug(traceback.print_exc())
        pass  #Or it may stop leaving lots of lines unprocessed

#----------------------------------------------------------------------
def download_danmaku(cid, filename):
    """str,str,int->None
    Download XML file, and convert to ASS(if required)
    Used to be in main(), but replaced due to the merge of -m (BiligrabLite).
    If danmaku only, will see whether need to export ASS."""
    logging.info('Fetching XML...')
    execute_sysencode_cmd('curl -o "{filename}.xml" --compressed  http://comment.bilibili.com/{cid}.xml'.format(filename = filename, cid = cid))
    #execute_sysencode_cmd('gzip -d '+cid+'.xml.gz')
    logging.info('The XML file, {filename}.xml should be ready...enjoy!'.format(filename = filename.decode("utf-8").encode(sys.stdout.encoding)))
    
#----------------------------------------------------------------------
def logcommand(command_line):
    logging.debug('Executing: '+' '.join('\''+i+'\'' if ' ' in i or '&' in i or '"' in i else i for i in command_line))

#----------------------------------------------------------------------
def logorraise(message, debug=False):
    if debug:
        raise message
    else:
        logging.error(str(message))

########################################################################
class DanmakuOnlyException(Exception):

    '''Deal with DanmakuOnly to stop the main() function.'''
    #----------------------------------------------------------------------

    def __init__(self, value):
        self.value = value
    #----------------------------------------------------------------------

    def __str__(self):
        return repr(self.value)

########################################################################
class Danmaku2Ass2Exception(Exception):

    '''Deal with Danmaku2ASS2 to stop the main() function.'''
    #----------------------------------------------------------------------

    def __init__(self, value):
        self.value = value
    #----------------------------------------------------------------------

    def __str__(self):
        return repr(self.value)

########################################################################
class NoCidException(Exception):

    '''Deal with no cid to stop the main() function.'''
    #----------------------------------------------------------------------

    def __init__(self, value):
        self.value = value
    #----------------------------------------------------------------------

    def __str__(self):
        return repr(self.value)

########################################################################
class NoVideoURLException(Exception):

    '''Deal with no video URL to stop the main() function.'''
    #----------------------------------------------------------------------

    def __init__(self, value):
        self.value = value
    #----------------------------------------------------------------------

    def __str__(self):
        return repr(self.value)

########################################################################
class ExportM3UException(Exception):

    '''Deal with export to m3u to stop the main() function.'''
    #----------------------------------------------------------------------

    def __init__(self, value):
        self.value = value
    #----------------------------------------------------------------------

    def __str__(self):
        return repr(self.value)

########################################################################
class YougetURLException(Exception):

    '''you-get cannot get URL somehow'''
    #----------------------------------------------------------------------

    def __init__(self, value):
        self.value = value
    #----------------------------------------------------------------------

    def __str__(self):
        return repr(self.value)

########################################################################
class URLOpenException(Exception):

    '''cannot get URL somehow'''
    #----------------------------------------------------------------------

    def __init__(self, value):
        self.value = value
    #----------------------------------------------------------------------

    def __str__(self):
        return repr(self.value)


########################################################################
class DownloadVideo(threading.Thread):
    """Threaded Download Video"""
    #----------------------------------------------------------------------
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
    #----------------------------------------------------------------------
    def run(self):
        while True:
            #grabs start time from queue
            down_set = self.queue.get()
            #return_value = download_video(down_set)
            cmd = download_video_link(*down_set)
            return_value = execute_cmd(cmd)
            self.queue.task_done()

#----------------------------------------------------------------------
def main_threading(download_thread = 3, video_list = [], thread_single_download = 16):
    """"""
    command_pool = [(video_list.index(url_this), download_software, url_this, thread_single_download) for url_this in video_list]
    #spawn a pool of threads, and pass them queue instance
    for i in range(int(download_thread)):
        t = DownloadVideo(queue)
        t.setDaemon(True)
        t.start()
    #populate queue with data
    for command_single in command_pool:
        queue.put(command_single)
    #wait on the queue until everything has been processed
    queue.join()

#----------------------------------------------------------------------
def main(vid, p, oversea, cookies, download_software, concat_software, is_export, probe_software, danmaku_only, time_fetch=5, download_thread= 16, thread_single_download= 16):
    global cid, partname, title, videourl, is_first_run
    videourl = 'http://www.bilibili.com/video/av{vid}/index_{p}.html'.format(vid = vid, p = p)
    # Check both software
    logging.debug(concat_software + ', ' + download_software)
    # Start to find cid, api
    cid, partname, title, pages = find_cid_api(vid, p, cookies)
    #if cid is 0:
        #logging.warning('Cannot find cid, trying to do it brutely...')
        #find_cid_flvcd(videourl)
    if cid is 0:
        if IS_SLIENT == 0:
            logging.warning('Strange, still cannot find cid... ')
            is_black3 = str(raw_input('Type y for trying the unpredictable way, or input the cid by yourself; Press ENTER to quit.'))
        else:
            is_black3 = 'y'
        if 'y' in str(is_black3):
            vid = str(int(vid) - 1)
            p = 1
            find_cid_api(int(vid) - 1, p)
            cid = cid + 1
        elif str(is_black3) is '':
            raise NoCidException('FATAL: Cannot get cid anyway!')
        else:
            cid = str(is_black3)
    # start to make folders...
    if title is not '':
        folder = title
    else:
        folder = cid
    if len(partname) is not 0:
        filename = partname
    elif title is not '':
        filename = title
    else:
        filename = cid
    #In case cannot find which s which
    filename = str(p) + ' - ' + filename
    # In case make too much folders
    folder_to_make = os.getcwd() + '/' + folder
    if is_first_run == 0:
        if not os.path.exists(folder_to_make):
            os.makedirs(folder_to_make)
        is_first_run = 1
        os.chdir(folder_to_make)
    # Download Danmaku
    download_danmaku(cid, filename)
    if is_export >= 1 and IS_M3U != 1 and danmaku_only == 1:
        rawurl = get_video(oversea, convert_m3u = True)
        check_dependencies_remote_resolution('ffprobe')
        resolution = getvideosize(rawurl[0])[0]
        convert_ass(filename, probe_software, resolution = resolution)
    if IS_M3U == 1:
        rawurl = []
        #M3U export, then stop
        if oversea in {'0', '1'}:
            rawurl = get_video(oversea, convert_m3u = True)
        else:
            duration_list = []
            rawurl = get_video(oversea, convert_m3u = False)
            for url in rawurl:
                duration_list.append(getvideosize(url)[1])
            rawurl = map(lambda x,y: (x, y), rawurl, duration_list)
        #print(rawurl)
        resolution = getvideosize(rawurl[0][0])[0]
        m3u_file = make_m3u8(rawurl)
        f = open(filename + '.m3u', 'w')
        cwd = os.getcwd()
        m3u_file = m3u_file.encode("utf8")
        f.write(m3u_file)
        f.close()
        convert_ass(filename, probe_software, resolution = resolution)
        logging.debug(m3u_file)
        raise ExportM3UException('INFO: Export to M3U')
    if danmaku_only == 1:
        raise DanmakuOnlyException('INFO: Danmaku only')
    # Find video location
    logging.info('Finding video location...')
    # try api
        # flvcd
    url_flag = 1
    rawurl = []
    logging.info('Trying to get download URL...')
    rawurl = get_video(oversea, convert_m3u = False)
    if len(rawurl) == 0 and oversea != '4':  # hope this never happen
        logging.warning('API failed, using falloff plan...')
        rawurl = find_link_flvcd(videourl)
    vid_num = len(rawurl)
    if IS_SLIENT == 0 and vid_num == 0:
        logging.warning('Cannot get download URL!')
        rawurl = list(str(raw_input('If you know the url, please enter it now: URL1|URL2...'))).split('|')
    vid_num = len(rawurl)
    if vid_num is 0:  # shit really hit the fan
        raise NoVIdeoURLException('FATAL: Cannot get video URL anyway!')
    logging.info('{vid_num} videos in part {part_now} to download, fetch yourself a cup of coffee...'.format(vid_num = vid_num, part_now = part_now))
    #Multi thread
    if len(rawurl) == 1:
        cmd = download_video_link(0,download_software,rawurl[0], thread_single_download)
        execute_sysencode_cmd(cmd)
    else:
        global queue
        queue = Queue.Queue()
        main_threading(download_thread, rawurl, thread_single_download)
        queue.join()
    concat_videos(concat_software, vid_num, filename)
    if is_export >= 1:
        try:
            convert_ass(filename, probe_software)
        except Exception:
            logging.warning('Problem with ASS conversion!')
            pass
    logging.info('Part Done!')

#----------------------------------------------------------------------
def get_full_p(p_raw):
    """str->list"""
    p_list = []
    p_raw = p_raw.split(',')
    for item in p_raw:
        if '~' in item:
            # print(item)
            lower = 0
            higher = 0
            item = item.split('~')
            part_now = '0'
            try:
                lower = int(item[0])
            except Exception:
                logging.warning('Cannot read lower!')
            try:
                higher = int(item[1])
            except Exception:
                logging.warning('Cannot read higher!')
            if lower == 0 or higher == 0:
                if lower == 0 and higher != 0:
                    lower = higher
                elif lower != 0 and higher == 0:
                    higher = lower
                else:
                    logging.warning('Cannot find any higher or lower, ignoring...')
                    # break
            mid = 0
            if higher < lower:
                mid = higher
                higher = lower
                lower = mid
            p_list.append(lower)
            while lower < higher:
                lower = lower + 1
                p_list.append(lower)
            # break
        else:
            try:
                p_list.append(int(item))
            except Exception:
                logging.warning('Cannot read "{item}", abandon it.'.format(item = item))
                # break
    p_list = list_del_repeat(p_list)
    return p_list

#----------------------------------------------------------------------
def check_dependencies_remote_resolution(software):
    """"""
    if 'ffprobe' in software:
        output = commands.getstatusoutput('ffprobe --help')
        if str(output[0]) == '32512':
            FFPROBE_USABLE = 0
        else:
            FFPROBE_USABLE = 1

#----------------------------------------------------------------------
def check_dependencies_exportm3u(IS_M3U):
    """int,str->int,str"""
    if IS_M3U == 1:
        output = commands.getstatusoutput('ffprobe --help')
        if str(output[0]) == '32512':
            logging.error('ffprobe DNE, python3 does not exist or not callable!')
            err_input = str(raw_input('Do you want to exit, ignore or stop the conversion?(e/i/s)'))
            if err_input == 'e':
                exit()
            elif err_input == '2':
                FFPROBE_USABLE = 0
            elif err_input == 's':
                IS_M3U = 0
            else:
                logging.warning('Cannot read input, stop the conversion!')
                IS_M3U = 0
        else:
            FFPROBE_USABLE = 1
    return IS_M3U

#----------------------------------------------------------------------
def check_dependencies_danmaku2ass(is_export):
    """int,str->int,str"""
    if is_export == 3:
        convert_ass = convert_ass_py3
        output = commands.getstatusoutput('python3 --help')
        if str(output[0]) == '32512' or not os.path.exists(os.path.join(LOCATION_DIR, 'danmaku2ass3.py')):
            logging.warning('danmaku2ass3.py DNE, python3 does not exist or not callable!')
            err_input = str(raw_input('Do you want to exit, use Python 2.x or stop the conversion?(e/2/s)'))
            if err_input == 'e':
                exit()
            elif err_input == '2':
                convert_ass = convert_ass_py2
                is_export = 2
            elif err_input == 's':
                is_export = 0
            else:
                logging.warning('Cannot read input, stop the conversion!')
                is_export = 0
    elif is_export == 2 or is_export == 1:
        convert_ass = convert_ass_py2
        if not os.path.exists(os.path.join(LOCATION_DIR, 'danmaku2ass2.py')):
            logging.warning('danmaku2ass2.py DNE!')
            err_input = str(raw_input('Do you want to exit, use Python 3.x or stop the conversion?(e/3/s)'))
            if err_input == 'e':
                exit()
            elif err_input == '3':
                convert_ass = convert_ass_py3
                is_export = 3
            elif err_input == 's':
                is_export = 0
            else:
                logging.warning('Cannot read input, stop the conversion!')
                is_export = 0
    else:
        convert_ass = convert_ass_py2
    return is_export, convert_ass

#----------------------------------------------------------------------
def usage():
    """"""
    print('''
    Biligrab
    
    https://github.com/cnbeining/Biligrab
    http://www.cnbeining.com/
    
    Beining@ACICFG
    
    
    
    Usage:
    
    python biligrab.py (-h) (-a) (-p) (-s) (-c) (-d) (-v) (-l) (-e) (-b) (-m) (-n) (-u) (-t) (-q) (-r) (-g)
    
    -h: Default: None
        Print this usage file.
        
    -a: Default: None
        The av number.
        If not set, Biligrab will use the fallback interactive mode.
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
        If set to 0, Biligrab will download all the available parts in the video.
        
    -s: Default: 0
    Source to download.
    0: The original API source, can be Letv backup,
       and can fail if the original video is not available(e.g., deleted)
    1: The CDN API source, "oversea accelerate".
       Can be MINICDN backup in Mainland China or oversea.
       Good to bypass some bangumi's restrictions.
    2: Force to use the original source.
       Use Flvcd to parse the video, but would fail if
       1) The original source DNE, e.g., some old videos
       2) The original source is Letvcloud itself.
       3) Other unknown reason(s) that stops Flvcd from parsing the video.
    For any video that failed to parse, Biligrab will try to use Flvcd.
    (Mainly for oversea users regarding to copyright-restricted bangumies.)
    If the API is blocked, Biligrab would fake the UA.
    3: (Not stable) Use the HTML5 API.
       This works for downloading some cached Letvcloud videos, but is slow, and would fail for no reason sometimes.
       Will retry if unavailable.
    4: Use Flvcd.
       Good to fight with oversea and copyright restriction, but not working with iQiyi.
       May retrieve better quality video, especially for Youku.
    5: Use BilibiliPr.
       Good to fight with some copyright restriction that BilibiliPr can fix.
       Not always working though.
    6: Use You-get (https://github.com/soimort/you-get).
       You need a you-get callable directly like "you-get -u blahblah".
       
    -c: Default: ./bilicookies
    The path of cookies.
    Use cookies to visit member-only videos.
    
    -d: Default: None
    Set the desired download software.
    Biligrab supports aria2c(16 threads), axel(20 threads), wget and curl by far.
    If not set, Biligrab will detect an available one;
    If none of those is available, Biligrab will quit.
    For more software support, please open an issue at https://github.com/cnbeining/Biligrab/issues/
    
    -v: Default:None
    Set the desired concatenate software.
    Biligrab supports ffmpeg by far.
    If not set, Biligrab will detect an available one;
    If none of those is available, Biligrab will quit.
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
    If not set, Biligrab will detect an available one;
    If none of those is available, Biligrab will quit.
    For more software support, please open an issue at https://github.com/cnbeining/Biligrab/issues/
    Make sure you include a *working* command line example of this software!
    
    -m: Default: 0
    Only download the danmaku.
    
    -n: Default: 0
    Silent Mode.
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
    
    -r: Default: -1
    Select video quality.
    Only works with Source 0 or 1.
    Range: 0~4, higher for better quality.
    
    -g: Default: 6
    Threads for downloading every part.
    Works with aria2 and axel.
    
    -i: Default: None
    Fake IP address.
    ''')

#----------------------------------------------------------------------
if __name__ == '__main__':
    is_first_run, is_export, danmaku_only, IS_SLIENT, IS_M3U, mylist, time_fetch, download_thread, QUALITY, thread_single_download = 0, 1, 0, 0, 0, 0, 5, 16, -1, 16
    argv_list,av_list = [], []
    argv_list = sys.argv[1:]
    p_raw, vid, oversea, cookiepath, download_software, concat_software, probe_software, vid_raw, LOG_LEVEL, FAKE_IP, IS_FAKE_IP = '', '', '', '', '', '', '', '', 'INFO', '', 0
    convert_ass = convert_ass_py2
    try:
        opts, args = getopt.getopt(argv_list, "ha:p:s:c:d:v:l:e:b:m:n:u:t:q:r:g:i:",
                                   ['help', "av=", 'part=', 'source=', 'cookie=', 'download=', 'concat=', 'log=', 'export=', 'probe=', 'danmaku=', 'slient=', 'm3u=', 'mylist=', 'thread=', 'quality=', 'thread_single=', 'fake-ip='])
    except getopt.GetoptError:
        usage()
        exit()
    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
            exit()
        if o in ('-a', '--av'):
            vid_raw = a
        if o in ('-p', '--part'):
            p_raw = a
        if o in ('-s', '--source'):
            oversea = a
        if o in ('-c', '--cookie'):
            cookiepath = a
            if cookiepath == '':
                logging.warning('No cookie path set, use default: ./bilicookies')
                cookiepath = './bilicookies'
        if o in ('-d', '--download'):
            download_software = a
        if o in ('-v', '--concat'):
            concat_software = a
        if o in ('-l', '--log'):
            try:
                LOG_LEVEL = str(a)
            except Exception:
                LOG_LEVEL = 'INFO'
        if o in ('-e', '--export'):
            is_export = int(a)
        if o in ('-b', '--probe'):
            probe_software = a
        if o in ('-m', '--danmaku'):
            danmaku_only = int(a)
        if o in ('-n', '--slient'):
            IS_SLIENT = int(a)
        if o in ('-u', '--m3u'):
            IS_M3U = int(a)
        if o in ('-t', '--mylist'):
            mylist = a
        if o in ('-q', '--thread'):
            download_thread = int(a)
        if o in ('-r', '--quality'):
            QUALITY = int(a)
        if o in ('-g', '--thread_single'):
            thread_single_download = int(a)
        if o in ('-i', '--fake-ip'):
            FAKE_IP = a
            IS_FAKE_IP = 1
    if len(vid_raw) == 0:
        vid_raw = str(raw_input('av'))
        p_raw = str(raw_input('P'))
        oversea = str(raw_input('Source?'))
        cookiepath = './bilicookies'
    logging.basicConfig(level = logging_level_reader(LOG_LEVEL))
    logging.debug('FAKE IP: ' + str(IS_FAKE_IP) + ' ' + FAKE_IP)
    av_list = get_full_p(vid_raw)
    if mylist != 0:
        av_list += mylist_to_aid_list(mylist)
    logging.debug('av_list')
    if len(cookiepath) == 0:
        cookiepath = './bilicookies'
    if len(p_raw) == 0:
        logging.info('No part number set, download all the parts.')
        p_raw = '0'
    if len(oversea) == 0:
        oversea = '0'
        logging.info('Oversea not set, use original API(methon 0).')
    IS_M3U = check_dependencies_exportm3u(IS_M3U)
    if IS_M3U == 1 and oversea not in {'0', '1'}:
        # See issue #8
        logging.info('M3U exporting with source other than 0 or 1 can be broken, and lead to wrong duration!')
        if IS_SLIENT == 0:
            input_raw = str(raw_input('Enter "q" to quit, or enter the source you want.'))
            if input_raw == 'q':
                exit()
            else:
                oversea = input_raw
    concat_software, download_software, probe_software = check_dependencies(download_software, concat_software, probe_software)
    p_list = get_full_p(p_raw)
    if len(av_list) > 1 and len(p_list) > 1:
        logging.warning('You are downloading multi parts from multiple videos! This may result in unpredictable outputs!')
        if IS_SLIENT == 0:
            input_raw = str(raw_input('Enter "y" to continue, "n" to only download the first part, "q" to quit, or enter the part number you want.'))
            if input_raw == 'y':
                pass
            elif input_raw == 'n':
                p_list = ['1']
            elif input_raw == 'q':
                exit()
            else:
                p_list = get_full_p(input_raw)
    cookies = read_cookie(cookiepath)
    global BILIGRAB_HEADER, BILIGRAB_UA
    # deal with danmaku2ass's drama / Twice in case someone failed to check dependencies
    is_export, convert_ass = check_dependencies_danmaku2ass(is_export)
    is_export, convert_ass = check_dependencies_danmaku2ass(is_export)
    python_ver_str = '.'.join([str(i) for i in sys.version_info[:2]])
    BILIGRAB_UA = 'Biligrab/{VER} (cnbeining@gmail.com) (Python-urllib/{python_ver_str}, like libcurl/1.0 NSS-Mozilla/2.0)'.format(VER = VER, python_ver_str = python_ver_str)
    
    #BILIGRAB_UA = 'Biligrab / ' + str(VER) + ' (cnbeining@gmail.com) (like )'
    BILIGRAB_HEADER = {'User-Agent': BILIGRAB_UA, 'Cache-Control': 'no-cache', 'Pragma': 'no-cache', 'Cookie': cookies[0]}
    if LOG_LEVEL == 'DEBUG':
        logging.debug('!!!!!!!!!!!!!!!!!!!!!!!\nWARNING: This log contains some sensitive data. You may want to delete some part of the data before you post it publicly!\n!!!!!!!!!!!!!!!!!!!!!!!')
        logging.debug('BILIGRAB_HEADER')
        try:
            request = urllib2.Request('http://ipinfo.io/json', headers=FAKE_HEADER)
            response = urllib2.urlopen(request)
            data = response.read()
            print('!!!!!!!!!!!!!!!!!!!!!!!\nWARNING: This log contains some sensitive data. You may want to delete some part of the data before you post it publicly!\n!!!!!!!!!!!!!!!!!!!!!!!')
            print('=======================DUMP DATA==================')
            print(data)
            print('========================DATA END==================')
            print('DEBUG: ' + str(av_list))
        except Exception:
            print('WARNING: Cannot connect to IP-geo database server!')
            pass
    for av in av_list:
        vid = str(av)
        if str(p_raw) == '0':
            logging.info('You are downloading all the parts in this video...')
            try:
                p_raw = str('1~' + find_cid_api(vid, p_raw, cookies)[3])
                p_list = get_full_p(p_raw)
            except Exception:
                logging.info('Error when reading all the parts!')
                if IS_SLIENT == 0:
                    input_raw = str(raw_input('Enter the part number you want, or "q" to quit.'))
                    if input_raw == '0':
                        print('ERROR: Cannot use all the parts!')
                        exit()
                    elif input_raw == 'q':
                        exit()
                    else:
                        p_list = get_full_p(input_raw)
                else:
                    logging.info('Download the first part of the video...')
                    p_raw = '1'
                    p_list = [1]
            logging.info('Your target download is av{vid}, part {p_raw}, from source {oversea}'.format(vid = vid, p_raw = p_raw, oversea = oversea))
        for p in p_list:
            reload(sys)
            sys.setdefaultencoding('utf-8')
            part_now = str(p)
            try:
                logging.info('Downloading part {p} ...'.format(p = p))
                main(vid, p, oversea, cookies, download_software, concat_software, is_export, probe_software, danmaku_only, time_fetch, download_thread, thread_single_download)
            except DanmakuOnlyException:
                pass
            except ExportM3UException:
                pass
            except Exception as e:
                print('ERROR: Biligrab failed: %s' % e)
                print('       If you think this should not happen, please dump your log using "-l", and open a issue at https://github.com/cnbeining/Biligrab/issues .')
                print('       Make sure you delete all the sensitive data before you post it publicly.')
                traceback.print_exc()
    exit()
