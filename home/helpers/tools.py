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
from http.client import RemoteDisconnected  # @UnresolvedImport

from PIL import Image, ImageDraw, ImageFont  # @UnresolvedImport


logger = logging.getLogger('webcam.tools')


def test1():
    '''test log'''
    logger.info('in test1')


def is_there_anybody_out_there(config):
    """get timestamp of last visit - returns wait 10/60"""
    logger.info("get last visit")
    last_visit_url = config.get('url')
    last_visit_format = config.get('format')
    try:
        html = urllib.request.urlopen(last_visit_url, None, 10)
        visited = html.read()
        visited_parsed = datetime.strptime(visited.decode('ascii'),
                                           last_visit_format)
    except ValueError as value_error:
        logger.error("last visit ValueError %s", str(value_error))
        return False
    mynow = datetime.strftime(datetime.now(), last_visit_format)

    we_have_a_visitor = abs(
        (visited_parsed - datetime.strptime(
            mynow, last_visit_format)).total_seconds()) < 60

    logger.info("refresh: %s", we_have_a_visitor)
    return we_have_a_visitor


def get_image_from_webcam(config, picture):
    '''get image from webcam and store it in picture'''

    url = config.get('url')
    passman = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, url,
                         config.get('user'), config.get('password'))
    authhandler = urllib.request.HTTPDigestAuthHandler(passman)
    opener = urllib.request.build_opener(authhandler)
    urllib.request.install_opener(opener)

    got_image = False

    logger.info("get url %s", url)
    for trycount in range(1, config.getint('maxretrycount') + 1):
        logger.info("get image try %s", trycount)

        try:
            with urllib.request.urlopen(url, None, 10) as response:
                with open(picture, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)
            got_image = True
        except RemoteDisconnected as http_error:
            logger.error("HTTPError %s", http_error)
            got_image = False
        except urllib.error.URLError as url_error:
            logger.error("URLError %s", url_error)
            got_image = False

        if got_image:
            logger.info("got image at try %s", trycount)
            break
    return got_image


def annotate_image(picture, picture_annotated,
                   do_crop=False, do_resize=False):
    '''draw timestamp on image'''
    image_from_picture = Image.open(picture)

    if do_crop:
        logger.info("do_crop")
        left = 250
        upper = 400
        right = left + 1140
        lower = 1000
        im_crop = image_from_picture.crop((left, upper, right, lower))
        font_size = 18
    else:
        logger.info("no crop")
        im_crop = image_from_picture
        font_size = 18

    if do_resize:
        font_size = 18
        size = 1140, 1140
        try:
            im_crop.thumbnail(size, Image.ANTIALIAS)
        except IOError:
            logger.error("cannot resize image")

    draw = ImageDraw.Draw(im_crop)
    font = ImageFont.truetype("Vera.ttf", font_size, encoding="unic")
    anno_time = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
    draw.text((12, 12), anno_time, fill='#202020', font=font)
    draw.text((11, 11), anno_time, fill='#000000', font=font)
    draw.text((10, 10), anno_time, fill='#A0A0F0', font=font)

    im_crop.save(picture_annotated)


def send_image_to_webpage(config, picture_annotated):
    '''use ftp to send image to web'''
    session_is_open = 0
    session = ""
    try:
        session = ftplib.FTP(config.get('server'), config.get('user'),
                             config.get('password'), timeout=10)
        session_is_open = 1
        session.cwd(config.get('dir'))

        if config.get('subdir') != '':
            formatted_subdir = datetime.strftime(datetime.now(),
                                                 config.get('subdir'))
            create_missing_dir(session, formatted_subdir)
            session.cwd(formatted_subdir)
        # mylist = session.nlst()

        filename = config.get('filename')
        if "%" in filename:
            filename = (datetime.strftime(datetime.now(), filename))
        file = open(picture_annotated, 'rb')
        session.storbinary('STOR ' + filename + '.tmp', file)
        file.close()
        session.rename(filename + '.tmp', filename)
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


def send_image_to_webpage_wos(config, session, filename):
    '''use ftp with open session'''
    success = 0
    try:
        session.cwd(config.get('dir'))

        if config.get('subdir') != '':
            formatted_subdir = datetime.strftime(datetime.now(),
                                                 config.get('subdir'))
            create_missing_dir(session, formatted_subdir)
            session.cwd(formatted_subdir)

        filehandler = open(join(config.get('retrydir'), filename), 'rb')
        session.storbinary('STOR ' + filename, filehandler)
        filehandler.close()
        success = 1
    except socket.timeout as sock_error:
        logger.error("sock error %s ", sock_error)
    except ftplib.all_errors as ftp_error:
        logger.error("ftp error %s ", ftp_error)

    return success


def create_missing_dir(session, dir_to_check):
    '''check or create dir'''
    use_mlsd = 1
    if use_mlsd:
        # if ftp server supports mlsd, use it,
        # nlst is marked as deprecated in ftplib
        # check if remotefoldername exists
        remotefoldername_exists = 0
        for name, facts in session.mlsd(".", ["type"]):
            if facts["type"] == "dir" and name == dir_to_check:
                remotefoldername_exists = 1
                break
        if remotefoldername_exists == 0:
            session.mkd(dir_to_check)
            logger.debug("folder does not exitst, ftp.mkd: %s",
                         dir_to_check)
        else:
            logger.debug("folder did exist: %s", dir_to_check)

    else:
        # nlst legacy support for ftp servers that
        # do not support mlsd e.g. vsftp
        items = []
        session.retrlines('LIST', items.append)
        items = map(str.split, items)
        dirlist = [item.pop() for item in items if item[0][0] == 'd']
        if dir_to_check not in dirlist:
            session.mkd(dir_to_check)
            logger.debug("folder does not exitst, ftp.mkd: %s", dir_to_check)
        else:
            logger.debug("folder did exist: %s", dir_to_check)
