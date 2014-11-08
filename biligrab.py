#!/usr/bin/env python
#coding:utf-8
# Author: Beining --<ACICFG>
# Purpose: Yet another danmaku and video file downloader of Bilibili. 
# Created: 11/06/2013
'''
Biligrab 0.96.2
Beining@ACICFG
cnbeining[at]gmail.com
http://www.cnbeining.com
https://github.com/cnbeining/Biligrab
MIT licence
'''

import sys
import os
from StringIO import StringIO
import gzip
import urllib
import urllib2
import sys
import math
import commands
import hashlib
import getopt
from danmaku2ass2 import * 

from xml.dom.minidom import parse, parseString
import xml.dom.minidom

reload(sys)
sys.setdefaultencoding('utf-8')

global vid, cid, partname, title, videourl, part_now, is_first_run, APPKEY, SECRETKEY, LOG_LEVEL, VER, LOCATION_DIR, VIDEO_FORMAT, convert_ass, is_export

cookies,VIDEO_FORMAT = '', ''
LOG_LEVEL = 0
APPKEY='85eb6835b0a1034e';
SECRETKEY = '2ad42749773c441109bdc0191257a664'
VER = '0.96.2'
FAKE_HEADER = {'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36', 'Cache-Control': 'no-cache', 'Pragma': 'no-cache' }
LOCATION_DIR = os.getcwd()

#----------------------------------------------------------------------
def list_del_repeat(list):
    """delete repeating items in a list, and keep the order.
    http://www.cnblogs.com/infim/archive/2011/03/10/1979615.html"""
    l2 = []
    [l2.append(i) for i in list if not i in l2]
    return(l2)

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
        #print(cookies)
        return cookies
    except:
        print('WARNING: Cannot read cookie, may affect some videos...')
        return ['']

#----------------------------------------------------------------------
def clean_name(name):
    """str->str
    delete all the dramas in the filename."""
    return str(name).strip().replace('\\', ' ').replace('/', ' ').replace('&', ' ')

#----------------------------------------------------------------------
def find_cid_api(vid, p, cookies):
    """find cid and print video detail
    TODO: Use json."""
    global cid, partname, title, videourl
    cid = 0
    title = ''
    partname = ''
    if str(p) is '0' or str(p) is '1':
        str2Hash = 'appkey=' + str(APPKEY) + '&id=' + str(vid) + '&type=xml' + str(SECRETKEY)
        biliurl = 'https://api.bilibili.com/view?appkey=' + str(APPKEY) + '&id=' + str(vid) + '&type=xml&sign=' + calc_sign(str2Hash)
        print('DEBUG: ' + biliurl)
    else:
        str2Hash = 'appkey=' + str(APPKEY) + '&id=' + str(vid) + '&page=' + str(p) + '&type=xml' + str(SECRETKEY)
        biliurl = 'https://api.bilibili.com/view?appkey=' + str(APPKEY) + '&id=' + str(vid) + '&page=' + str(p) + '&type=xml&sign=' + calc_sign(str2Hash)
        print('DEBUG: ' + biliurl)
    videourl = 'http://www.bilibili.com/video/av'+ str(vid)+'/index_'+ str(p)+'.html'
    print('INFO: Fetching webpage...')
    try:
        #print(BILIGRAB_HEADER)
        request = urllib2.Request(biliurl, headers = BILIGRAB_HEADER)
        response = urllib2.urlopen(request)
        data = response.read()
        dom = parseString(data)
        for node in dom.getElementsByTagName('cid'):
            if node.parentNode.tagName == "info":
                cid = node.toxml()[5:-6]
                print('INFO: cid is ' + cid)
                break
        for node in dom.getElementsByTagName('partname'):
            if node.parentNode.tagName == "info":
                partname = clean_name(str(node.toxml()[10:-11]))
                print('INFO: partname is ' + partname)  #no more /\ drama
                break
        for node in dom.getElementsByTagName('title'):
            if node.parentNode.tagName == "info":
                title = clean_name(str(node.toxml()[7:-8]))
                print('INFO: Title is ' + title)
    except:  #If API failed
        if LOG_LEVEL == 1:
            print('WARNING: Cannot connect to API server! \nIf you think this is wrong, please open an issue at \nhttps://github.com/cnbeining/Biligrab/issues with *ALL* the screen output, \nas well as your IP address and basic system info.')
            print('=======================DUMP DATA==================')
            print(data)
            print('========================DATA END==================')
        else:
            print('WARNING: Cannot connect to API server!')


#----------------------------------------------------------------------
def find_cid_flvcd(videourl):
    """str->None
    set cid."""
    global vid, cid, partname, title
    print('INFO: Fetching webpage via Flvcd...')
    request = urllib2.Request(videourl, headers= FAKE_HEADER)
    request.add_header('Accept-encoding', 'gzip')
    response = urllib2.urlopen(request)
    if response.info().get('Content-Encoding') == 'gzip':
        buf = StringIO(response.read())
        f = gzip.GzipFile(fileobj=buf)
        data = f.read()
    data_list = data.split('\n')
    if LOG_LEVEL == 1:
        print('Dumping info...')
        print('=======================DUMP DATA==================')
        print(data)
        print('========================DATA END==================')
    #Todo: read title
    for lines in data_list:
        if 'cid=' in lines:
            cid = lines.split('&')
            cid = cid[0].split('=')
            cid = cid[-1]
            print('INFO: cid is ' + str(cid))
            break

#----------------------------------------------------------------------
def find_link_flvcd(videourl):
    """"""
    print('INFO: Finding link via Flvcd...')
    request = urllib2.Request('http://www.flvcd.com/parse.php?'+urllib.urlencode([('kw', videourl)]), headers=FAKE_HEADER)
    request.add_header('Accept-encoding', 'gzip')
    response = urllib2.urlopen(request)
    data = response.read()
    data_list = data.split('\n')
    if LOG_LEVEL == 1:
        print('Dumping info...')
        print('=======================DUMP DATA==================')
        print(data)
        print('========================DATA END==================')
    for items in data_list:
        if 'name' in items and 'inf' in items and 'input' in items:
            c = items
            rawurlflvcd = c[59:-5]
            rawurlflvcd = rawurlflvcd.split('|')
            return rawurlflvcd

#----------------------------------------------------------------------
def check_dependencies(download_software, concat_software, probe_software):
    """None->str,str,str
    Will give softwares for concat, download and probe.
    The detection of Python3 is located at the end of Main function."""
    concat_software_list = ['ffmpeg', 'avconv']
    download_software_list = ['aria2c', 'axel', 'wget', 'curl']
    probe_software_list = ['mediainfo', 'ffprobe']
    name_list = [[concat_software, concat_software_list], [download_software, download_software_list], [probe_software, probe_software_list]]
    for name in name_list:
        if name[0].strip().lower() not in name[1] :  # Unsupported software
            if  len(name[0].strip()) != 0:  #Set a Unsupported software,  not blank
                print('WARNING: Requested Software not supported!\n         Biligrab only support these following software(s):\n         ' + str(name[1]) + '\n         Trying to find available one...')
            for software in name[1]:
                output = commands.getstatusoutput(software + ' --help')
                if str(output[0]) != '32512':  #If exist
                    name[0] = software
                    break
        if name[0] == '':
            print('FATAL: Cannot find software in ' + str(name[1]) + ' !')
            exit()
    return name_list[0][0], name_list[1][0], name_list[2][0]

#----------------------------------------------------------------------
def download_video(part_number, download_software, video_link):
    """"""
    if download_software == 'aria2c':
        os.system('aria2c -c -s16 -x16 -k1M --out '+part_number+'.flv "'+video_link+'"')
    elif download_software == 'wget':
        os.system('wget -c -O '+part_number+'.flv "'+video_link+'"')
    elif download_software == 'curl':
        os.system('curl -L -C -o '+part_number+'.flv "'+video_link+'"')
    elif download_software == 'axel':
        os.system('axel -n 20 -o '+part_number+'.flv "'+video_link+'"')


#----------------------------------------------------------------------
def concat_videos(concat_software, vid_num, filename):
    """str,str->None"""
    global VIDEO_FORMAT
    if concat_software == 'ffmpeg':
        f = open('ff.txt', 'w')
        ff = ''
        os.getcwd()
        for i in range(vid_num):
            ff = ff + 'file \'' + str(os.getcwd()) + '/'+ str(i) + '.flv\'\n'
        ff = ff.encode("utf8")
        f.write(ff)
        f.close()
        if LOG_LEVEL == 1:
            print('Dumping ff.txt...')
            print('=======================DUMP DATA==================')
            print(ff)
            print('========================DATA END==================')
        print('INFO: Concating videos...')
        os.system('ffmpeg -f concat -i ff.txt -c copy "'+filename+'".mp4')
        VIDEO_FORMAT = 'mp4'
        if os.path.isfile(str(filename+'.mp4')):
            os.system('rm -r ff.txt')
            for i in range(vid_num):
                os.system('rm -r '+str(i)+'.flv')
            print('INFO: Done, enjoy yourself!')
        else:
            print('ERROR: Cannot concatenative files, trying to make flv...')
            os.system('ffmpeg -f concat -i ff.txt -c copy "'+filename+'".flv')
            VIDEO_FORMAT = 'flv'
            if os.path.isfile(str(filename+'.flv')):
                print('WARNING: FLV file made. Not possible to mux to MP4, highly likely due to audio format.')
                os.system('rm -r ff.txt')
                for i in range(vid_num):
                    os.system('rm -r '+str(i)+'.flv')
            else:
                print('ERROR: Cannot concatenative files!')
    elif concat_software == 'avconv':
        pass

#----------------------------------------------------------------------
def find_video_address_api(cid, header, method):
    """"""
    sign_this = calc_sign('appkey=' + APPKEY + '&cid=' + cid + SECRETKEY)
    if method == '1':
        try:
            request = urllib2.Request('http://interface.bilibili.com/v_cdn_play?appkey=' + APPKEY + '&cid=' + cid + '&sign=' + sign_this, headers = header)
        except:
            print('ERROR: Cannot connect to CDN API server!')
    elif method is '2':
        #Force get oriurl
        try:
            request = urllib2.Request('http://interface.bilibili.com/player?appkey=' + APPKEY + '&cid=' + cid + '&sign=' + sign_this, headers = header)
        except:
            print('ERROR: Cannot connect to original source API server!')
    else:
        try:
            request = urllib2.Request('http://interface.bilibili.com/playurl?appkey=' + APPKEY + '&cid=' + cid + '&sign=' + sign_this, headers = header)
        except:
            print('ERROR: Cannot connect to normal API server!')
    response = urllib2.urlopen(request)
    data = response.read()
    return data

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
        if LOG_LEVEL == 1:
            print('DEBUG: Software: ' + probe_software + ', resolution ' + resolution)
        return resolution
    except:
        return[1280, 720]

#----------------------------------------------------------------------
def get_resolution_mediainfo(filename):
    """str->list
    [640,360]
    path to dimention"""
    resolution = str(os.popen('mediainfo \'--Inform=Video;%Width%x%Height%\' \'' + filename + '\'').read()).strip().split('x')
    return [int(resolution[0]), int(resolution[1])]

#----------------------------------------------------------------------
def get_resolution_ffprobe(filename):
    '''str->list
    [640,360]'''
    width = ''
    height = ''
    cmnd = ['ffprobe', '-show_format', '-show_streams' ,'-pretty', '-loglevel', 'quiet', filename]
    p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #print filename
    out, err =  p.communicate()
    if err:
        print err
        return None
    try:
        for line in out.split():
            if 'width=' in line:
                width = line.split('=')[1]
            if 'height=' in line:
                height = line.split('=')[1]
    except:
        return None
    #return width + 'x' + height
    return [int(width), int(height)]

#----------------------------------------------------------------------
def convert_ass_py3(filename, probe_software):
    """str,str->None
    With danmaku2ass, branch master.
    https://github.com/m13253/danmaku2ass/
    Author: @m13253
    GPLv3
    A simple way to do that.
    resolution_str:1920x1080"""
    print('INFO: Converting danmaku to ASS file with danmaku2ass(main)...')
    xml_name = os.path.abspath(xml_name + '.xml')
    ass_name = filename + '.ass'
    print('INFO: Trying to get resolution...')
    resolution = get_resolution(filename, probe_software)
    print('INFO: Resolution is %dx%d' % (resolution[0], resolution[1]))
    if os.system('python3 %s/danmaku2ass3.py -o %s -s %dx%d -fs %d -a 0.8 -l 8 %s' % (LOCATION_DIR, ass_name, resolution[0], resolution[1], int(math.ceil(resolution[1]/21.6)), xml_name)) == 0:
        print('INFO: The ASS file should be ready!')
    else:
        print('ERROR: Danmaku2ASS failed.')
        print('       Head to https://github.com/m13253/danmaku2ass/issues to complain about this.')

#----------------------------------------------------------------------
def convert_ass_py2(filename, probe_software):
    """str,str->None
    With danmaku2ass, branch py2.
    https://github.com/m13253/danmaku2ass/tree/py2
    Author: @m13253
    GPLv3"""
    print('INFO: Converting danmaku to ASS file with danmaku2ass(py2)...')
    xml_name = filename + '.xml'
    print('INFO: Trying to get resolution...')
    resolution = get_resolution(filename, probe_software)
    print('INFO: Resoution is ' + str(resolution))
    #convert_ass(xml_name, filename + '.ass', resolution)
    try:
        Danmaku2ASS(xml_name, filename + '.ass', resolution[0], resolution[1], 
                font_size= int(math.ceil(resolution[1]/21.6)), text_opacity= 0.8, comment_duration= 8.0)
        print('INFO: The ASS file should be ready!')
    except Exception as e:
        print('ERROR: Danmaku2ASS failed: %s' % e)
        print('       Head to https://github.com/m13253/danmaku2ass/issues to complain about this.')


#----------------------------------------------------------------------
def download_danmaku(cid, filename, is_export, probe_software):
    """str,str,int->None
    Download XML file, and convert to ASS(if required)
    Used to be in main(), but replaced due to the merge of -m (BiligrabLite).
    If danmaku only, will see whether need to export ASS."""
    print('INFO: Fetching XML...')
    os.system('curl -o "'+filename+'.xml" --compressed  http://comment.bilibili.com/'+cid+'.xml')
    #os.system('gzip -d '+cid+'.xml.gz')
    print('INFO: The XML file, ' + filename + '.xml should be ready...enjoy!')


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
#----------------------------------------------------------------------
def main(vid, p, oversea, cookies, download_software, concat_software, is_export, probe_software, danmaku_only):
    global cid, partname, title, videourl, is_first_run
    videourl = 'http://www.bilibili.com/video/av'+ str(vid)+'/index_'+ str(p)+'.html'
    # Check both software
    concat_software, download_software, probe_software = check_dependencies(download_software, concat_software, probe_software)
    print(concat_software, download_software)
    #Start to find cid, api-flvcd
    find_cid_api(vid, p, cookies)
    global cid
    if cid is 0:
        print('WARNING: Cannot find cid, trying to do it brutely...')
        find_cid_flvcd(videourl)
    if cid is 0:
        is_black3 = str(raw_input('WARNING: Strange, still cannot find cid... \nType y for trying the unpredictable way, or input the cid by yourself; Press ENTER to quit.'))
        if 'y' in str(is_black3):
            vid = str(int(vid) - 1)
            p = 1
            find_cid_api(int(vid)-1, p)
            cid = cid + 1
        elif str(is_black3) is '':
            print('FATAL: Cannot get cid anyway! Quit.')
            exit()
        else:
            cid = str(is_black3)
    #start to make folders...
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
    # In case make too much folders
    folder_to_make = os.getcwd() + '/' + folder
    if is_first_run == 0:
        if not os.path.exists(folder_to_make):
            os.makedirs(folder_to_make)
        is_first_run = 1
        os.chdir(folder_to_make)
    # Download Danmaku
    download_danmaku(cid, filename, is_export, probe_software)
    if is_export >= 1 and danmaku_only == 1:
        #if requested to stop
        convert_ass(filename, probe_software)
    if danmaku_only == 1:
        raise DanmakuOnlyException('INFO: Danmaku only')
    #Find video location
    print('INFO: Finding video location...')
    #try api
    data = find_video_address_api(cid, BILIGRAB_HEADER, oversea)
    if LOG_LEVEL == 1:
        print('Dumping info...')
        print('=======================DUMP DATA==================')
        print(data)
        print('========================DATA END==================')
    for l in data.split('\n'):  #In case shit happens
        if 'error.mp4' in l:
            print('WARNING: API header may be blocked! Using fake one instead...')
            data = find_video_address_api(cid, FAKE_HEADER, oversea)
            if LOG_LEVEL == 1:
                print('Dumping info...')
                print('=======================DUMP DATA==================')
                print(data)
                print('========================DATA END==================')
    rawurl = []
    originalurl = ''
    if oversea is '2':
        data = data.split('\n')
        for l in data:
            if 'oriurl' in l:
                originalurl = str(l[8:-9])
                print('INFO: Original URL is ' + originalurl)
                break
        if originalurl is not '':
            rawurl = find_link_flvcd(originalurl)
        else:
            print('WARNING: Cannot get original URL! Using falloff plan...')
            pass
    else:
        dom = parseString(data)
        for node in dom.getElementsByTagName('url'):
            if node.parentNode.tagName == "durl":
                rawurl.append(node.toxml()[14:-9])
                #print(str(node.toxml()[14:-9]))
            pass
    if len(rawurl) == 0:  #hope this never happen
        rawurl = find_link_flvcd(videourl)
        #flvcd
    vid_num = len(rawurl)
    if vid_num is 0:  # shit hit the fan
        rawurl = list(str(raw_input('ERROR: Cannot get download URL! If you know the url, please enter it now; URL1|URL2...'))).split('|')
    vid_num = len(rawurl)
    if vid_num is 0:  # shit really hit the fan
        print('FATAL: Cannot get video URL anyway!')
        exit()
    print('INFO: ' + str(vid_num) + ' videos in part ' + str(part_now) + ' to download, fetch yourself a cup of coffee...')
    for i in range(vid_num):
        video_link = rawurl[i]
        part_number = str(i)
        print('INFO: Downloading ' + str(i+1) + ' of ' + str(vid_num) + ' videos in part ' + str(part_now) + '...')
        #Call a function to support multiple download softwares
        download_video(part_number, download_software, video_link)
    concat_videos(concat_software, vid_num, filename)
    if is_export >= 1:
        try:
            convert_ass(filename, probe_software)
        except:
            print('WARNING: Problem with ASS convertion!')
            pass
    print('INFO: Part Done!')


#----------------------------------------------------------------------
def get_full_p(p_raw):
    """str->list"""
    p_list = []
    p_raw = p_raw.split(',')
    for item in p_raw:
        if '~' in item:
            #print(item)
            lower = 0
            higher = 0
            item = item.split('~')
            part_now = '0'
            try:
                lower = int(item[0])
            except:
                print('WARNING: Cannot read lower!')
            try:
                higher = int(item[1])
            except:
                print('WARNING: Cannot read higher!')
            if lower == 0 or higher == 0:
                if lower == 0 and higher != 0:
                    lower = higher
                elif lower != 0 and higher == 0:
                    higher = lower
                else:
                    print('WARNING: Cannot find any higher or lower, ignoring...')
                    #break
            mid = 0
            if higher < lower:
                mid = higher
                higher = lower
                lower = mid
            p_list.append(lower)
            while lower < higher:
                lower = lower + 1
                p_list.append(lower)
            #break
        else:
            try:
                p_list.append(int(item))
            except:
                print('WARNING: Cannot read "'+str(item)+'", abondon it.')
                #break
    p_list = list_del_repeat(p_list)
    return p_list

#----------------------------------------------------------------------
def check_dependencies_danmaku2ass(is_export):
    """int,str->int,str"""
    if is_export == 3:
        convert_ass = convert_ass_py3
        output = commands.getstatusoutput('python3 --help')
        if str(output[0]) == '32512' or not os.path.exists('danmaku2ass3.py'):
            err_input = str(raw_input('ERROR: danmaku2ass3.py DNE, python3 does not exist or not callable! Do you want to exit, use Python 2.x or stop the converting?(e/2/s)'))
            if err_input == 'e':
                exit()
            elif err_input == '2':
                convert_ass = convert_ass_py2
                is_export = 2
            elif err_input == 's':
                is_export = 0
            else:
                print('WARNING: Cannot read input, stop the converting!')
                is_export = 0
    elif is_export == 2 or is_export == 1:
        convert_ass = convert_ass_py2
        if not os.path.exists('danmaku2ass2.py'):
            err_input = str(raw_input('ERROR: danmaku2ass2.py DNE! Do you want to exit, use Python 3.x or stop the converting?(e/3/s)'))
            if err_input == 'e':
                exit()
            elif err_input == '3':
                convert_ass = convert_ass_py3
                is_export = 3
            elif err_input == 's':
                is_export = 0
            else:
                print('WARNING: Cannot read input, stop the converting!')
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
    
    python biligrab.py (-h) (-a) (-p) (-s) (-c) (-d) (-v) (-l) (-e) (-p) (-m)
    
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
    If the API is blocked, Biligrab would fake the UA.
    
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
    Set the desired download software.
    Biligrab supports ffmpeg by far.
    If not set, Biligrab will detect an avalable one;
    If none of those is avalable, Biligrab will quit.
    For more software support, please open an issue at https://github.com/cnbeining/Biligrab/issues/
    Make sure you include a *working* command line example of this software!
    
    -l: Default: 0
    Dump the log of the output for better debugging.
    
    -e: Default: 0
    Export Danmaku to ASS file.
    Fulfilled with danmaku2ass(https://github.com/m13253/danmaku2ass/tree/py2),
    Author: @m13253, GPLv3 License.
    *For issue with this function, if you think the problem lies on the danmaku2ass side,
    please open the issue at both projects.*
    If set to 1 or 2, Biligrab will use Danmaku2ass's py2 branch.
    If set to 3, Biligrab will use Danmaku2ass's master branch, which would require
    a python3 callable via 'python3'.
    If python3 not callable or danmaku2ass2/3 DNE, Biligrab will ask for action.
    
    -p: Default: None
    Set the probe software.
    Biligrab supports Mediainfo and FFprobe.
    If not set, Biligrab will detect an avalable one;
    If none of those is avalable, Biligrab will quit.
    For more software support, please open an issue at https://github.com/cnbeining/Biligrab/issues/
    Make sure you include a *working* command line example of this software!
    
    -m: Default: 0
    Only download the danmaku.
    ''')


#----------------------------------------------------------------------
if __name__=='__main__':
    is_first_run, is_export, danmaku_only = 0, 0, 0
    argv_list = []
    argv_list = sys.argv[1:]
    p_raw, vid, oversea, cookiepath, download_software, concat_software, probe_software = '', '', '', '', '', '', ''
    convert_ass = convert_ass_py2
    try:
        opts, args = getopt.getopt(argv_list, "ha:p:s:c:d:v:l:e:b:m:", ['help', "av",'part', 'source', 'cookie', 'download', 'concat', 'log', 'export', 'probe', 'danmaku'])
    except getopt.GetoptError:
        usage()
        exit()
    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
            exit()
        if o in ('-a', '--av'):
            vid = a
            try:
                argv_list.remove('-a')
            except:
                break
        if o in ('-p', '--part'):
            p_raw = a
            try:
                argv_list.remove('-p')
            except:
                break
        if o in ('-s', '--source'):
            oversea = a
            try:
                argv_list.remove('-s')
            except:
                break
        if o in ('-c', '--cookie'):
            cookiepath = a
            try:
                argv_list.remove('-c')
            except:
                print('INFO: No cookie path set, use default: ./bilicookies')
                cookiepath = './bilicookies'
                break
        if o in ('-d', '--download'):
            download_software = a
            try:
                argv_list.remove('-d')
            except:
                break
        if o in ('-v', '--concat'):
            concat_software = a
            try:
                argv_list.remove('-v')
            except:
                break
        if o in ('-l', '--log'):
            LOG_LEVEL = int(a)
            print('INFO: Log enabled!')
            try:
                argv_list.remove('-l')
            except:
                LOG_LEVEL = 0
                break
        if o in ('-e', '--export'):
            is_export = int(a)
            try:
                argv_list.remove('-e')
            except:
                is_export = 0
                break
        if o in ('-b', '--probe'):
            probe_software = a
            try:
                argv_list.remove('-b')
            except:
                break
        if o in ('-m', '--danmaku'):
            danmaku_only = int(a)
            try:
                argv_list.remove('-m')
            except:
                break
    if len(vid) == 0:
        vid = str(raw_input('av'))
        p_raw = str(raw_input('P'))
        oversea = str(raw_input('Source?'))
        cookiepath = './bilicookies'
    '''
    if len(vid) == 0:
        vid = str(raw_input('Please input: av'))
        if len(vid) == 0:
            print('Cannot download nothing!')
            exit()
    '''
    if len(cookiepath) == 0:
        cookiepath = './bilicookies'
    if len(p_raw) == 0:
        print('INFO: No part number set, download part 1.')
        p_raw = '1'
    if len(oversea) == 0:
        oversea = '0'
        print('INFO: Oversea not set, use original API(methon 0).')
    print('INFO: Your targe download is av' + vid + ', part ' + p_raw + ', from source ' + oversea)
    p_list = get_full_p(p_raw)
    cookies = read_cookie(cookiepath)
    global BILIGRAB_HEADER
    #deal with danmaku2ass's drama
    #Twice in case someone failed to check dependencies
    is_export, convert_ass = check_dependencies_danmaku2ass(is_export)
    is_export, convert_ass = check_dependencies_danmaku2ass(is_export)
    BILIGRAB_HEADER = {'User-Agent' : 'Biligrab / ' + str(VER) + ' (cnbeining@gmail.com)', 'Cache-Control': 'no-cache', 'Pragma': 'no-cache' , 'Cookie': cookies[0]}
    if LOG_LEVEL == 1:
        print('!!!!!!!!!!!!!!!!!!!!!!!\nWARNING: This log contains some sensive data. You may want to delete some part of the data before you post it publicly!\n!!!!!!!!!!!!!!!!!!!!!!!')
        print(BILIGRAB_HEADER)
        try:
            request = urllib2.Request('http://ipinfo.io/json', headers = FAKE_HEADER)
            response = urllib2.urlopen(request)
            data = response.read()
            print('INFO: Dumping info...')
            print('!!!!!!!!!!!!!!!!!!!!!!!\nWARNING: This log contains some sensive data. You may want to delete some part of the data before you post it publicly!\n!!!!!!!!!!!!!!!!!!!!!!!')
            print('=======================DUMP DATA==================')
            print(data)
            print('========================DATA END==================')
        except:
            print('WARNING: Cannot connect to IP-geo database server!')
    for p in p_list:
        reload(sys)
        sys.setdefaultencoding('utf-8')
        part_now = str(p)
        try:
            main(vid, p, oversea, cookies, download_software, concat_software, is_export, probe_software, danmaku_only)
        except DanmakuOnlyException:
            pass
    exit()


