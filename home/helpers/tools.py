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

logger = logging.getLogger('webcamarch.tools')


def test1():
    '''test log'''
    logger.info('in test1')


def get_image_from_webcam(config):
    '''get image from webcam and store it in picture'''
    picture = config.get('picture')
    url = config.get('url')
    passman = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, url,
                         config.get('user'), config.get('password'))
    authhandler = urllib.request.HTTPDigestAuthHandler(passman)
    opener = urllib.request.build_opener(authhandler)
    urllib.request.install_opener(opener)

    got_image = 0

    for trycount in range(1, config.getint('maxretrycount') + 1):
        logger.info("get image try %s", trycount)
        if got_image == 1:
            break
        logger.info("get url %s", url)
        try:
            with urllib.request.urlopen(url, None, 10) as response:
                with open(picture, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)
            got_image = 1
        except urllib.error.URLError as url_error:
            logger.error("URLError %s", url_error)
            got_image = 0
    return got_image


def annotate_picture(picture, picture_annotated):
    '''draw timestamp on image'''
    image_from_picture = Image.open(picture)
    draw = ImageDraw.Draw(image_from_picture)
    font = ImageFont.truetype("Vera.ttf", 40, encoding="unic")
    anno_time = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
    draw.text((22, 22), anno_time, fill='#202020', font=font)
    draw.text((21, 21), anno_time, fill='#000000', font=font)
    draw.text((20, 20), anno_time, fill='#A0A0F0', font=font)
    image_from_picture.save(picture_annotated)


def send_imge_to_webpage(config, filename):
    '''use ftp to send image to web'''
    session_is_open = 0
    try:
        session = ftplib.FTP(config.get('server'), config.get('user'),
                             config.get('password'), timeout=10)
        session_is_open = 1
        session.cwd(config.get('dir'))
        mylist = session.nlst()
        file = open(config.get('picture_annotated'), 'rb')
        session.storbinary('STOR ' + filename, file)
        file.close()
        logger.info("list %s ", mylist)
    except socket.timeout as sock_error:
        session_is_open = 0
        rename(config.get('picture_annotated'),
               join(config.get('retrydir'), filename))
        print("sock error %s" % sock_error)
        logger.error("sock error %s ", sock_error)
    except ftplib.all_errors as ftp_error:
        session_is_open = 0
        rename(config.get('picture_annotated'),
               join(config.get('retrydir'), filename))
        logger.error("ftp error %s ", ftp_error)

    return (session_is_open, session)


def send_imge_to_webpage_wos(config, session, filename):
    '''use ftp with open session'''
    success = 0
    try:
        session.cwd(config.get('dir'))
        filehandler = open(join(config.get('retrydir'), filename), 'rb')
        session.storbinary('STOR ' + filename, filehandler)
        filehandler.close()
        success = 1
    except socket.timeout as sock_error:
        logger.error("sock error %s ", sock_error)
    except ftplib.all_errors as ftp_error:
        logger.error("ftp error %s ", ftp_error)

    return success
