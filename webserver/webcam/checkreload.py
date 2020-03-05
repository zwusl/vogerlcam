#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
'''is called by webcam.js

writes in lb.txt
'''

import os
import datetime
import json
import cgi
import cgitb; cgitb.enable()


def header():
    '''header'''
    print("Content-Type: application/json;charset=iso-8859-1")
    #   print "Content-Type: text/html;charset=iso-8859-1"
    print("")


header()

myform = cgi.FieldStorage()

myuhrzeit = myform.getfirst("uhrzeit", "")
mydateisshown = datetime.datetime.strptime(myuhrzeit,"%Y-%m-%d--%H-%M-%S")
myfound = []

mywebcamtime = os.path.getmtime("webcam_0.jpeg")
mywebcamtime0 = datetime.datetime.fromtimestamp(mywebcamtime)
mywebcamtime1 = datetime.datetime.strftime(mywebcamtime0,"%Y-%m-%d--%H-%M-%S")
mydateishere = datetime.datetime.strptime(mywebcamtime1,"%Y-%m-%d--%H-%M-%S")


if  mydateishere > mydateisshown :
    myfound.append("neu")
    mystat = "neu"
    myfound.append(datetime.datetime.strftime(mydateishere,"%Y-%m-%d--%H-%M-%S"))
    myfound.append(datetime.datetime.strftime(mydateisshown,"%Y-%m-%d--%H-%M-%S"))
else:
    myfound.append("alt")
    mystat = "alt"
    myfound.append(datetime.datetime.strftime(mydateishere,"%Y-%m-%d--%H-%M-%S"))
    myfound.append(datetime.datetime.strftime(mydateisshown,"%Y-%m-%d--%H-%M-%S"))


dateTimeObj = datetime.datetime.now()

timestampStr = dateTimeObj.strftime("%Y-%m-%d--%H-%M-%S")

myfilename = "./cam1/visited/lb.txt" #+ timestampStr
myfile = open(myfilename,"w")
myfile.write(timestampStr)
myfile.close()

json_string=json.dumps(myfound)

print(json_string)
