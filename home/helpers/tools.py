'''
Created on 22.02.2020

@author: werner
'''

from datetime import datetime
import ftplib
from os import rename
from os.path import join
import shutil
import socket
import urllib.request
import logging

from PIL import Image, ImageDraw, ImageFont  # @UnresolvedImport
from http.client import RemoteDisconnected

logger = logging.getLogger('webcam.tools')


def test1():
    '''test log'''
    logger.info('in test1')


def getlastvisit():
    logger.info("get last visit")
    try:
        html = urllib.request.urlopen("http://xn--fr-xka.st/webcam/cam1/visited/lb.txt",None,10)
        visited = html.read()
        visited_parsed = datetime.strptime(visited.decode('ascii'),"%Y-%m-%d--%H-%M-%S")
    except ValueError as ve:
        logger.error("last visit ValueError %s",str(ve))
        return 60
    mynow = datetime.strftime(datetime.now(),"%Y-%m-%d--%H-%M-%S")

    if abs((visited_parsed-datetime.strptime(mynow,"%Y-%m-%d--%H-%M-%S")).total_seconds())<60 :
            myrefresh = 10
    else:
            myrefresh = 60
    #print (datetime.strptime(visited,"%Y-%m-%d--%H-%M-%S")-datetime.strptime(mynow,"%Y-%m-%d--%H-%M-%S")).total_seconds()
    print (myrefresh)
    return myrefresh


def get_image_from_webcam(config, picture):
    '''get image from webcam and store it in picture'''

    url = config.get('url')
    passman = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, url,
                         config.get('user'), config.get('password'))
    authhandler = urllib.request.HTTPDigestAuthHandler(passman)
    opener = urllib.request.build_opener(authhandler)
    urllib.request.install_opener(opener)

    got_image = 0

    logger.info("get url %s", url)
    for trycount in range(1, config.getint('maxretrycount') + 1):
        logger.info("get image try %s", trycount)
        try:
            with urllib.request.urlopen(url, None, 10) as response:
                with open(picture, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)
            got_image = 1
        except urllib.error.URLError as url_error:
            logger.error("URLError %s", url_error)
            got_image = 0
        except RemoteDisconnected as discerr:
            logger.error("RemoteDisconnected %s", discerr)
            got_image = 0
        if got_image == 1:
            logger.info("got image at try %s", trycount)
            break
    return got_image


def annotate_picture(picture, picture_annotated, do_crop=False):
    '''draw timestamp on image'''
    image_from_picture = Image.open(picture)
    
    if do_crop:
        logger.info("do_crop")
        left=250
        upper=400
        right=left+1140
        lower=1000
        im_crop = image_from_picture.crop((left, upper, right, lower))
        draw = ImageDraw.Draw(im_crop)
        font_size = 30
    else:
        logger.info("no crop")
        draw = ImageDraw.Draw(image_from_picture)
        font_size = 40
        
    font = ImageFont.truetype("Vera.ttf", font_size, encoding="unic")
    anno_time = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
    draw.text((22, 22), anno_time, fill='#202020', font=font)
    draw.text((21, 21), anno_time, fill='#000000', font=font)
    draw.text((20, 20), anno_time, fill='#A0A0F0', font=font)
    if do_crop:
        im_crop.save(picture_annotated)
    else:
        image_from_picture.save(picture_annotated)

def send_imge_to_webpage(config, webdir, filename, picture_annotated):
    '''use ftp to send image to web'''
    session_is_open = 0
    try:
        session = ftplib.FTP(config.get('server'), config.get('user'),
                             config.get('password'), timeout=10)
        session_is_open = 1
        session.cwd(webdir)
        mylist = session.nlst()
        file = open(picture_annotated, 'rb')
        session.storbinary('STOR ' + filename + '.tmp', file)
        file.close()
        session.rename(filename + '.tmp', filename)
        logger.info("list %s ", mylist)
    except socket.timeout as sock_error:
        session_is_open = 0
        rename(picture_annotated,
               join(config.get('retrydir'), filename))
        logger.error("sock error %s ", sock_error)
    except ftplib.all_errors as ftp_error:
        session_is_open = 0
        rename(picture_annotated,
               join(config.get('retrydir'), filename))
        logger.error("ftp error %s ", ftp_error)

    return (session_is_open, session)


def send_imge_to_webpage_wos(config, session, filename):
    '''use ftp with open session'''
    success = 0
    try:
        session.cwd(config.get('dirarch'))
        filehandler = open(join(config.get('retrydir'), filename), 'rb')
        session.storbinary('STOR ' + filename, filehandler)
        filehandler.close()
        success = 1
    except socket.timeout as sock_error:
        logger.error("sock error %s ", sock_error)
    except ftplib.all_errors as ftp_error:
        logger.error("ftp error %s ", ftp_error)

    return success
