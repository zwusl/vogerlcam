#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-


#print("Content-Type: text/html")    # HTML is following
#print("")                             # blank line, end of headers

import cgi
import cgitb; cgitb.enable()

import glob, os

import datetime

import json
    


def header():
   print "Content-Type: application/json;charset=iso-8859-1"
#   print "Content-Type: text/html;charset=iso-8859-1"
   print ""


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
 
#myfilename = "/home/xnfrxkas/public_html/webcam/cam1/visited/" + timestampStr
myfilename = "./cam1/visited/lb.txt" #+ timestampStr
myfile = open(myfilename,"w") 
myfile.write(timestampStr)
myfile.close() 

#myfilename2 = "./cam1/visited/debug.txt" #+ timestampStr
#myfile = open(myfilename2,"a") 
#myfile.write(timestampStr + " " + mystat + " " + datetime.datetime.strftime(mydateishere,"%Y-%m-%d--%H-%M-%S") + " " + datetime.datetime.strftime(mydateisshown,"%Y-%m-%d--%H-%M-%S") + "\n")
#myfile.close() 

json_string=json.dumps(myfound)
    
print json_string

