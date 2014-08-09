#!/usr/bin/env python
#coding:utf-8
# Author: Beining --<ACICFG>
# Purpose: Yet another danmaku and video file downloader of Bilibili. 
# Created: 12/10/2013
'''
Biligrab 0.86
Beining@ACICFG
cnbeining[at]gmail.com
http://www.cnbeining.com
MIT licence
'''

import sys
import os
from StringIO import StringIO
import gzip
import urllib
import urllib2
import sys
import commands
import hashlib
import getopt


from xml.dom.minidom import parse, parseString
import xml.dom.minidom

reload(sys)
sys.setdefaultencoding('utf-8')

global vid
global cid
global partname
global title
global videourl
global part_now
global is_first_run


global appkey
global secretkey
appkey='85eb6835b0a1034e';
secretkey = '2ad42749773c441109bdc0191257a664'



def list_del_repeat(list):
    """delete repeating items in a list, and keep the order.
    http://www.cnblogs.com/infim/archive/2011/03/10/1979615.html"""
    l2 = []
    [l2.append(i) for i in list if not i in l2]
    return(l2)

#----------------------------------------------------------------------
def find_cid_api(vid, p):
    """find cid and print video detail"""
    global cid
    global partname
    global title
    global videourl
    cookiepath = './bilicookies'
    try:
        cookies = open(cookiepath, 'r').readline()
        #print(cookies)
    except:
        print('Cannot read cookie, may affect some videos...')
        cookies = ''
    cid = 0
    title = ''
    partname = ''
    if str(p) is '0' or str(p) is '1':
        str2Hash = 'appkey=85eb6835b0a1034e&id=' + str(vid) + '&type=xml2ad42749773c441109bdc0191257a664'
        sign_this = hashlib.md5(str2Hash.encode('utf-8')).hexdigest()
        biliurl = 'https://api.bilibili.com/view?appkey=85eb6835b0a1034e&id=' + str(vid) + '&type=xml&sign=' + sign_this
        print(biliurl)
    else:
        str2Hash = 'appkey=85eb6835b0a1034e&id=' + str(vid) + '&page=' + str(p) + '&type=xml2ad42749773c441109bdc0191257a664'
        sign_this = hashlib.md5(str2Hash.encode('utf-8')).hexdigest()
        biliurl = 'https://api.bilibili.com/view?appkey=85eb6835b0a1034e&id=' + str(vid) + '&page=' + str(p) + '&type=xml&sign=' + sign_this
        #print(biliurl)
    videourl = 'http://www.bilibili.com/video/av'+ str(vid)+'/index_'+ str(p)+'.html'
    print('Fetching webpage...')
    try:
        request = urllib2.Request(biliurl, headers={ 'User-Agent' : 'Biligrab /0.8 (cnbeining@gmail.com)', 'Cache-Control': 'no-cache', 'Pragma': 'no-cache' , 'Cookie': cookies})
        response = urllib2.urlopen(request)
        data = response.read()
        dom = parseString(data)
        for node in dom.getElementsByTagName('cid'):
            if node.parentNode.tagName == "info":
                cid = node.toxml()[5:-6]
                print('cid is ' + cid)
                break
        for node in dom.getElementsByTagName('partname'):
            if node.parentNode.tagName == "info":
                partname = node.toxml()[10:-11].strip()
                print('partname is ' + partname)
                break
        for node in dom.getElementsByTagName('title'):
            if node.parentNode.tagName == "info":
                title = node.toxml()[7:-8].strip()
                print('Title is ' + title)
    except:  #If API failed
        print('ERROR: Cannot connect to API server!')


#----------------------------------------------------------------------
def find_cid_flvcd(videourl):
    """"""
    global vid
    global cid
    global partname
    global title
    print('Fetching webpage via Flvcd...')
    request = urllib2.Request(videourl, headers={ 'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36', 'Cache-Control': 'no-cache', 'Pragma': 'no-cache' })
    request.add_header('Accept-encoding', 'gzip')
    response = urllib2.urlopen(request)
    if response.info().get('Content-Encoding') == 'gzip':
        buf = StringIO( response.read())
        f = gzip.GzipFile(fileobj=buf)
        data = f.read()
    data_list = data.split('\n')
    #Todo: read title
    for lines in data_list:
        if 'cid=' in lines:
            cid = lines.split('&')
            cid = cid[0].split('=')
            cid = cid[-1]
            print('cid is ' + str(cid))
            break

#----------------------------------------------------------------------
def find_link_flvcd(videourl):
    """"""
    request = urllib2.Request('http://www.flvcd.com/parse.php?'+urllib.urlencode([('kw', videourl)]), headers={ 'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36', 'Cache-Control': 'no-cache', 'Pragma': 'no-cache' })
    request.add_header('Accept-encoding', 'gzip')
    response = urllib2.urlopen(request)
    data = response.read()
    data_list = data.split('\n')
    for items in data_list:
        if 'name' in items and 'inf' in items and 'input' in items:
            c = items
            rawurlflvcd = c[59:-5]
            rawurlflvcd = rawurlflvcd.split('|')
            return rawurlflvcd



#----------------------------------------------------------------------
def main(vid, p, oversea):
    global cid
    global partname
    global title
    global videourl
    global is_first_run
    videourl = 'http://www.bilibili.com/video/av'+ str(vid)+'/index_'+ str(p)+'.html'

    output = commands.getstatusoutput('ffmpeg --help')
    if str(output[0]) == '32512':
        print('FFmpeg does not exist! Trying to get you a binary, need root...')
        os.system('sudo curl -o /usr/bin/ffmpeg https://raw.githubusercontent.com/superwbd/ABPlayerHTML5-Py--nix/master/ffmpeg')
    output = commands.getstatusoutput('aria2c --help')
    if str(output[0]) == '32512':
        print('aria2c does not exist! Trying to get you a binary, need root... Thanks for @MartianZ \'s work.')
        os.system('sudo curl -o /usr/bin/aria2c https://raw.githubusercontent.com/MartianZ/fakeThunder/master/fakeThunder/aria2c')

    find_cid_api(vid, p)
    global cid
    if cid is 0:
        print('Cannot find cid, trying to do it brutely...')
        find_cid_flvcd(videourl)

    if cid is 0:
        is_black3 = str(raw_input('Strange, still cannot find cid... Type y for trying the unpredictable way, or input the cid by yourself, press ENTER to quit.'))
        if 'y' in str(is_black3):
            vid = vid - 1
            p = 1
            find_cid_api(vid-1, p)
            cid = cid + 1
        elif str(is_black3) is '':
            print('Cannot get cid anyway! Quit.')
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

    print('Fetching XML...')
    os.system('curl -o "'+filename+'.xml" --compressed  http://comment.bilibili.com/'+cid+'.xml')
    os.system('gzip -d '+cid+'.xml.gz')
    print('The XML file, ' + filename + '.xml should be ready...enjoy!')
    print('Finding video location...')
    #try api
    sign_this = hashlib.md5('appkey=' + appkey + '&cid=' + cid + secretkey.encode('utf-8')).hexdigest()
    if oversea == '1':
        try:
            request = urllib2.Request('http://interface.bilibili.com/v_cdn_play?appkey=' + appkey + '&cid=' + cid + '&sign=' + sign_this, headers={ 'User-Agent' : 'Biligrab /0.8 (cnbeining@gmail.com)', 'Cache-Control': 'no-cache', 'Pragma': 'no-cache' })
        except:
            print('ERROR: Cannot connect to CDN API server!')
    elif oversea is '2':
        #Force get oriurl
        try:
            request = urllib2.Request('http://interface.bilibili.com/player?appkey=' + appkey + '&cid=' + cid + '&sign=' + sign_this, headers={ 'User-Agent' : 'Biligrab /0.8 (cnbeining@gmail.com)', 'Cache-Control': 'no-cache', 'Pragma': 'no-cache' })
        except:
            print('ERROR: Cannot connect to original source API server!')
    else:
        try:
            request = urllib2.Request('http://interface.bilibili.com/playurl?appkey=' + appkey + '&cid=' + cid + '&sign=' + sign_this, headers={ 'User-Agent' : 'Biligrab /0.8 (cnbeining@gmail.com)', 'Cache-Control': 'no-cache', 'Pragma': 'no-cache' })
        except:
            print('ERROR: Cannot connect to normal API server!')
    response = urllib2.urlopen(request)
    data = response.read()
    rawurl = []
    originalurl = ''
    if oversea is '2':
        data = data.split('\n')
        for l in data:
            if 'oriurl' in l:
                originalurl = str(l[8:-9])
                print('Original URL is ' + originalurl)
                break
        if originalurl is not '':
            rawurl = find_link_flvcd(originalurl)
        else:
            print('Cannot get original URL! Using falloff plan...')
            pass
    else:
        dom = parseString(data)
        for node in dom.getElementsByTagName('url'):
            if node.parentNode.tagName == "durl":
                rawurl.append(node.toxml()[14:-9])
                #print(str(node.toxml()[14:-9]))
            pass
    if rawurl is []:  #hope this never happen
        rawurl = find_link_flvcd(videourl)
        #flvcd
    #print(rawurl)
    vid_num = len(rawurl)
    if vid_num is 0:
        print('Cannot get download URL!')
        exit()
    #print(rawurl)
    print(str(vid_num) + ' videos in part ' + str(part_now) + ' to download, fetch yourself a cup of coffee...')
    for i in range(vid_num):
        print('Downloading ' + str(i+1) + ' of ' + str(vid_num) + ' videos in part ' + str(part_now) + '...')
        #print('aria2c -llog.txt -c -s16 -x16 -k1M --out '+str(i)+'.flv "'+rawurl[i]+'"')
        os.system('aria2c -c -s16 -x16 -k1M --out '+str(i)+'.flv "'+rawurl[i]+'"')
        #os.system('aria2c -larialog.txt -c -s16 -x16 -k1M --out '+str(i)+'.flv "'+rawurl[i]+'"')
        #not debugging, not fun.
    f = open('ff.txt', 'w')
    ff = ''
    os.getcwd()
    for i in range(vid_num):
        ff = ff + 'file \'' + str(os.getcwd()) + '/'+ str(i) + '.flv\'\n'
    ff = ff.encode("utf8")
    f.write(ff)
    f.close()
    print('Concating videos...')
    os.system('ffmpeg -f concat -i ff.txt -c copy "'+filename+'".mp4')
    if os.path.isfile(str(filename+'.mp4')):
        os.system('rm -r ff.txt')
        for i in range(vid_num):
            os.system('rm -r '+str(i)+'.flv')
        print('Done, enjoy yourself!')
    else:
        print('ERROR: Cannot concatenative files, trying to make flv...')
        os.system('ffmpeg -f concat -i ff.txt -c copy "'+filename+'".flv')
        if os.path.isfile(str(filename+'.flv')):
            print('FLV file made. Not possible to mux to MP4, highly likely due to audio format.')
            os.system('rm -r ff.txt')
            for i in range(vid_num):
                os.system('rm -r '+str(i)+'.flv')
        else:
            print('ERROR: Cannot concatenative files, trying to make flv...')



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
                print('Cannot read lower!')
            try:
                higher = int(item[1])
            except:
                print('Cannot read higher!')
            if lower == 0 or higher == 0:
                if lower == 0 and higher != 0:
                    lower = higher
                elif lower != 0 and higher == 0:
                    higher = lower
                else:
                    print('Cannot find any higher or lower, ignoring...')
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
                print('Cannot read "'+str(item)+'", abondon it.')
                #break
    p_list = list_del_repeat(p_list)
    return p_list


#----------------------------------------------------------------------
def usage():
    """"""
    print('''Usage:
    
    python biligrab.py (-h) (-a) (-p) (-s)
    
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
       3) Other unknown reason(s) that stops Flvcd from parase the video.''')

#----------------------------------------------------------------------
if __name__=='__main__':
    is_first_run = 0
    argv_list = []
    argv_list = sys.argv[1:]
    p_raw = ''
    vid = ''
    oversea = ''
    try:
        opts, args = getopt.getopt(argv_list, "ha:p:s:", ['help', "av",'part', 'source'])
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
    if len(vid) == 0:
        vid = str(raw_input('av'))
        p_raw = str(raw_input('P'))
        oversea = str(input('Source?'))
    '''
    if len(vid) == 0:
        vid = str(raw_input('Please input: av'))
        if len(vid) == 0:
            print('Cannot download nothing!')
            exit()
    '''
    if len(p_raw) == 0:
        print('No part number set, download part 1.')
        p_raw = '1'
    if len(oversea) == 0:
        oversea = 0
        print('Oversea not set, use original API(methon 0).')
    print('Your targe download is av' + vid + ', part ' + p_raw + ', from source ' + oversea)
    p_list = get_full_p(p_raw)
    for p in p_list:
        reload(sys)
        sys.setdefaultencoding('utf-8')
        part_now = str(p)
        main(vid, p, oversea)
    exit()



'''
        data_list = data.split('\r')
        for lines in data_list:
            lines = str(lines)
            if '<url>' in lines:
                if 'youku'  in lines:
                    url = lines[17:-9]
                elif 'sina' in lines:
                    url = lines[16:-9]
                elif 'qq.com' in lines:
                    url = lines[17:-9]
                elif 'letv.com' in lines:
                    url = lines[17:-9]
                    break
                elif 'acgvideo' in lines:
                    url = lines[17:-9]
                    is_local = 1
                rawurl.append(url)
            if 'backup_url' in lines and is_local is 1:
                break'''