'''
Biligrab Lite 0.21
Beining@ACICFG
cnbeining[at]gmail.com
http://www.cnbeining.com
MIT licence
'''

import sys
import os
from StringIO import StringIO
import gzip
import urllib2
import hashlib

from xml.dom.minidom import parseString

global vid
global cid
global partname
global title
global videourl
global part_now

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
    else:
        str2Hash = 'appkey=85eb6835b0a1034e&id=' + str(vid) + '&page=' + str(p) + '&type=xml2ad42749773c441109bdc0191257a664'
        sign_this = hashlib.md5(str2Hash.encode('utf-8')).hexdigest()
        biliurl = 'https://api.bilibili.com/view?appkey=85eb6835b0a1034e&id=' + str(vid) + '&page=' + str(p) + '&type=xml&sign=' + sign_this
        #print(biliurl)
    videourl = 'http://www.bilibili.tv/video/av'+ str(vid)+'/index_'+ str(p)+'.html'
    print('Fetching webpage...')
    print(biliurl)
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
                print('Title is ' + title.decode("utf-8"))
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
def main(vid, p, oversea):
    global cid
    global partname
    global title
    global videourl
    global is_first_run
    videourl = 'http://www.bilibili.tv/video/av'+ str(vid)+'/index_'+ str(p)+'.html'
    
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
    if len(partname) is not 0:
        filename = partname
    elif title is not '':
        filename = title
    else:
        filename = cid
    print('Fetching XML...')
    os.system((u'curl -o "'+filename+u'.xml" --compressed  http://comment.bilibili.cn/'+cid+u'.xml').encode(sys.stdout.encoding))
    os.system((u'gzip -d '+cid+u'.xml.gz').encode(sys.stdout.encoding))
    print(u'The XML file, ' + filename + u'.xml should be ready...enjoy!')
    #try api
    #


vid = str(raw_input('av'))
p_raw = str(raw_input('P'))
if p_raw == '':
    p_raw = '1'
oversea = '0'

p_list = []
p_raw = p_raw.split(',')

for item in p_raw:
    if '~' in item:
        #print(item)
        lower = 0
        higher = 0
        item = item.split('~')
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
            print('Cannot read "'+str(item)+'", abandon it.')
            #break


p_list = list_del_repeat(p_list)

global is_first_run
is_first_run = 0

part_now = '0'
print(p_list)
for p in p_list:
    print part_now
    part_now = str(p)
    main(vid, p, oversea)
exit()
