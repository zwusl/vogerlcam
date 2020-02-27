
import sys
import os
import ftplib
#import urllib
import urllib.request
from datetime import datetime
import shutil
import time
#import base64
from PIL import Image, ImageDraw, ImageFont
import configparser

import socket

def getlastvisit():
    print (datetime.strftime(datetime.now(),"%Y-%m-%d--%H-%M-%S - ") + "get last visit")
    try:
        html = urllib.request.urlopen("http://xn--fr-xka.st/webcam/cam1/visited/lb.txt",None,10)
        visited = html.read()
        visited_parsed = datetime.strptime(visited.decode('ascii'),"%Y-%m-%d--%H-%M-%S")
    except:
        return 60

    #if visited.decode('ascii') == "" :
    #    return 60

    mynow = datetime.strftime(datetime.now(),"%Y-%m-%d--%H-%M-%S")

    if abs((visited_parsed-datetime.strptime(mynow,"%Y-%m-%d--%H-%M-%S")).total_seconds())<60 :
            myrefresh = 10
    else:
            myrefresh = 60
    #print (datetime.strptime(visited,"%Y-%m-%d--%H-%M-%S")-datetime.strptime(mynow,"%Y-%m-%d--%H-%M-%S")).total_seconds()
    print (myrefresh)
    return myrefresh

filename = 'webcam_1' + '.jpeg'
filename0 = 'webcam_0' + '.jpeg'

picture = 'picture.jpeg'
picture_crop = 'picture_crop.jpeg'

config = configparser.ConfigParser()
config.read('webcamloop.ini')

localconfig = config['LOCAL']
picture = localconfig.get('picture','picture.jpeg')
picture_crop = localconfig.get('picture_crop','picture_crop.jpeg')

webcamconfig = config['WEBCAM']
webcamurl = webcamconfig.get('url','http://192.168.0.19/cgi-bin/snapshot.cgi?channel=channel1')
webcamuser = webcamconfig.get('user','admin')
webcampassword = webcamconfig.get('password',fallback='admin')
maxretrycount = webcamconfig.getint('maxretrycount')

ftpconfig = config['FTP']
ftpserver = ftpconfig.get('server')
ftpuser = ftpconfig.get('user','anonymous')
ftppassword = ftpconfig.get('password','None')
ftpdir = ftpconfig.get('dir')



#os.remove(filename)

while True:

    print (datetime.strftime(datetime.now(),"%Y-%m-%d--%H-%M-%S - ") + "get image from cam")


    webcamurl = "http://192.168.0.13/cgi-bin/snapshot.cgi?channel=channel1"


    passman = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, webcamurl, webcamuser, webcampassword)
    authhandler = urllib.request.HTTPDigestAuthHandler(passman)
    opener = urllib.request.build_opener(authhandler)
    urllib.request.install_opener(opener)

    gotImage = 0
    for trycount in range(1, maxretrycount + 1) :
        print (f"get image try {trycount}")
        if gotImage == 1 :
            break
        try:
            with urllib.request.urlopen(webcamurl,None,10) as response, open(picture, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
            gotImage = 1
        except:
            gotImage = 0

    if gotImage == 0:
        print ("giving up, did not get an image from cam, wait 5 sec")
        time.sleep(5)
        continue


    print (datetime.strftime(datetime.now(),"%Y-%m-%d--%H-%M-%S - ") + "crop an annotate image")


    im = Image.open(picture)
    left=250
    upper=400
    right=left+1140
    lower=1000
    im_crop = im.crop((left, upper, right, lower))
    draw  = ImageDraw.Draw(im_crop)
    font  = ImageFont.truetype("Vera.ttf", 30, encoding="unic")

    draw.text( (22,22), datetime.strftime(datetime.now(),"%Y-%m-%d %H:%M:%S"),fill='#202020',font=font)
    draw.text( (21,21), datetime.strftime(datetime.now(),"%Y-%m-%d %H:%M:%S"),fill='#000000',font=font)
    draw.text( (20,20), datetime.strftime(datetime.now(),"%Y-%m-%d %H:%M:%S"),fill='#A0A0F0',font=font)

    im_crop.save(picture_crop)


    print (datetime.strftime(datetime.now(),"%Y-%m-%d--%H-%M-%S - ") + "send image to Webpage")


    try:
        session = ftplib.FTP(ftpserver,ftpuser,ftppassword,timeout=10)
        session.cwd(ftpdir)
        file = open(picture_crop,'rb')
        session.storbinary('STOR ' + filename, file)
        file.close()
        session.rename(filename,filename0)
        session.quit()
    except socket.timeout as f:
        print ("%s" % f)
        print("socket error:", sys.exc_info()[0])
    except ftplib.all_errors as e:
        print ("%s" % e)
        print("ftp error:", sys.exc_info()[0])
    except:
        print("Unexpected error:", sys.exc_info()[0])


    print (datetime.strftime(datetime.now(),"%Y-%m-%d--%H-%M-%S - ") + " loop")

    time.sleep(4)

    for cnt in range(74):

            mywait = getlastvisit()
            if mywait == 60:
                    time.sleep(4)
            else:
                    break

