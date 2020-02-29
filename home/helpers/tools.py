'''
Created on 22.02.2020

@author: werner
'''

import urllib.request
import shutil
from os import rename
from os.path import join
from datetime import datetime
import ftplib
import socket
from PIL import Image # Image, ImageDraw, ImageFont




def test1():
    print("test1")

def test2(config):
    print("test2")
    print(config.get('url'))
#     webcamurl = config.get('url')
#     webcamuser = config.get('user', 'admin')
#     webcampassword = config.get('password', fallback='admin')
#     maxretrycount = config.getint('maxretrycount')

def get_image_from_webcam(config):
    picture = config.get('picture')
    print("picture in " + picture)
    passman = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, config.get('url'),
                         config.get('user'), config.get('password'))
    authhandler = urllib.request.HTTPDigestAuthHandler(passman)
    opener = urllib.request.build_opener(authhandler)
    urllib.request.install_opener(opener)

    got_image = 0

    for trycount in range(1, config.getint('maxretrycount') + 1):
        print(f"get image try {trycount}")
        if got_image == 1:
            break
        print(config.get('url'))
        try:
            with urllib.request.urlopen(config.get('url'), None, 10) as response:
                with open(picture, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)
            got_image = 1
        except urllib.error.URLError as url_error:
            print("y%s" % url_error)
            got_image = 0
    return got_image

def annotate_picture(picture, picture_annotated):
    image_from_picture = Image.open(picture)
    draw = ImageDraw.Draw(image_from_picture)
    font = ImageFont.truetype("Vera.ttf", 40, encoding="unic")
    anno_time = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
    draw.text((22, 22), anno_time, fill='#202020', font=font)
    draw.text((21, 21), anno_time, fill='#000000', font=font)
    draw.text((20, 20), anno_time, fill='#A0A0F0', font=font)
    image_from_picture.save(picture_annotated)
    
def send_imge_to_webpage(config, filename):
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
        print(mylist)
    except socket.timeout as sock_error:
        session_is_open = 0
        rename(config.get('picture_annotated'), join(config.get('retrydir'), filename))
        print("sock error %s" % sock_error)
    except ftplib.all_errors as ftp_error:
        session_is_open = 0
        rename(config.get('picture_annotated'), join(config.get('retrydir'), filename))
        print("ftp error %s" % ftp_error)
    
    return (session_is_open, session)

def send_imge_to_webpage_wos(config, session, filename):
    success = 0
    try:
        session.cwd(config.get('dir'))
        filehandler = open(join(config.get('retrydir'), filename), 'rb')
        session.storbinary('STOR ' + filename, filehandler)
        filehandler.close()
        success = 1
    except socket.timeout as sock_error:
        print("%s" % sock_error)
    except ftplib.all_errors as ftp_error:
        print("%s" % ftp_error)
    
    return success
#         try:
#             session = ftplib.FTP(ftpserver, ftpuser, ftppassword, timeout=10)
#             session_is_open = 1
#             session.cwd(ftpdir)
#             mylist = session.nlst()
#             file = open(picture_annotated, 'rb')
#             session.storbinary('STOR ' + filename, file)
#             file.close()
#             print(mylist)
#         except socket.timeout as sock_error:
#             print("%s" % sock_error)
#             print("ftp error:", sys.exc_info()[0])
#             print(picture_annotated + " to " + join(retrydir, filename))
#             rename(picture_annotated, join(retrydir, filename))
#         except ftplib.all_errors as ftp_error:
#             print("%s" % ftp_error)
#             print("ftp error:", sys.exc_info()[0])
#             print(picture_annotated + " to " + join(retrydir, filename))
#             rename(picture_annotated, join(retrydir, filename))

