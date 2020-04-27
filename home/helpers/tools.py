'''
Created on 22.02.2020

@author: werner
'''

from datetime import datetime
import ftplib
from os import listdir, rename
from os.path import isfile, join
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


def get_image_from_webcam(config, image_file):
    '''get image from webcam and store it in image_file'''

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
                with open(image_file, 'wb') as out_file:
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


def annotate_image(image_file, image_file_annotated,
                   do_crop=False, do_resize=False):
    '''draw timestamp on image'''
    image_object = Image.open(image_file)

    if do_crop:
        logger.info("do_crop")
        left = 250
        upper = 400
        right = left + 1140
        lower = 1000
        im_crop = image_object.crop((left, upper, right, lower))
    else:
        logger.info("no crop")
        im_crop = image_object

    if do_resize:
        logger.info("do_resize")
        size = 1140, 1140
        try:
            im_crop.thumbnail(size, Image.ANTIALIAS)
        except IOError:
            logger.error("cannot resize image")

    font_size = 18
    draw = ImageDraw.Draw(im_crop)
    font = ImageFont.truetype("Vera.ttf", font_size, encoding="unic")
    anno_time = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
    draw.text((12, 12), anno_time, fill='#202020', font=font)
    draw.text((11, 11), anno_time, fill='#000000', font=font)
    draw.text((10, 10), anno_time, fill='#A0A0F0', font=font)

    im_crop.save(image_file_annotated)


def send_image_to_webpage(config, image_file_annotated):
    '''use ftp to send image to web'''
    session_is_open = False
    session = ""
    an_error_happened = False
    filename = config.get('filename')
    if "%" in filename:
        filename = (datetime.strftime(datetime.now(), filename))
    try:
        session = ftplib.FTP(config.get('server'), config.get('user'),
                             config.get('password'), timeout=10)
        session_is_open = True

        # mylist = session.nlst()

        store_ftp(session, config, image_file_annotated, filename)

    except socket.timeout as sock_error:
        an_error_happened = True
        logger.error("sock error %s ", sock_error)
    except ftplib.all_errors as ftp_error:
        an_error_happened = True
        logger.error("ftp error %s ", ftp_error)

    if an_error_happened:
        if session_is_open:
            session.quit()
        if config.get('retrydir') != "":
            rename(image_file_annotated,
                   join(config.get('retrydir'), filename))
    else:
        retrydir = config.get('retrydir')
        if retrydir == "":
            if session_is_open:
                session.quit()
        else:
            logger.info("retry sending files")
            retry_sending(session, config)

    return session_is_open


def retry_sending(session, config):
    '''retry'''
    try:
        retrydir = config.get('retrydir')

        files = [fil for fil in listdir(retrydir)
                 if (isfile(join(retrydir, fil))
                     and fil.endswith('_sm.jpg'))]
        if not files:
            logger.info("no files to retry in %s", retrydir)
            session.quit()
        else:
            for filename in files:

                logger.info("retry sending %s", filename)

                store_ftp(session, config,
                          join(retrydir, filename),
                          filename)

                rename(join(retrydir, filename),
                       join(retrydir, filename) + 'xxx')

            session.quit()
    except socket.timeout as sock_error:
        logger.error("sock error %s ", sock_error)
    except ftplib.all_errors as ftp_error:
        logger.error("ftp error %s ", ftp_error)



def store_ftp(session, config, full_name, save_as):
    '''store in ftp'''

    change_to_target_dir(session, config.get('dir'), config.get('subdir'))

    file_handler = open(full_name, 'rb')
    session.storbinary('STOR ' + save_as + '.tmp', file_handler)
    file_handler.close()
    session.rename(save_as + '.tmp', save_as)


def change_to_target_dir(session, cwddir, subdir):
    '''change dir'''
    session.cwd(cwddir)

    if subdir != '':
        split_subdir = subdir.split("-")
        for split_count in range(0, len(split_subdir)):
            sublevel = "-".join(split_subdir[0:split_count + 1])
            formatted_sublevel = datetime.strftime(datetime.now(),
                                                   sublevel)
            create_missing_dir(session, formatted_sublevel)
            logger.debug("changing to dir: %s", formatted_sublevel)
            session.cwd(formatted_sublevel)


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
