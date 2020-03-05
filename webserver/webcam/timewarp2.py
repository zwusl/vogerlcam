#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-


#print("Content-Type: text/html")    # HTML is following
#print("")                             # blank line, end of headers

import os
import glob
import datetime
import json
import cgi
import cgitb; cgitb.enable()



def header():
    '''header'''
    print("Content-Type: application/json;charset=iso-8859-1")
    #   print "Content-Type: text/html;charset=iso-8859-1"
    print("")


def nextimage(mymodus,mydir,mycurrent,myuhrzeit):

    myfiles = glob.glob(mydir + "/*_sm.jpg")

    if mymodus != "nearest":
        myfiles.sort()
    
        myindex = myfiles.index(mycurrent) if mycurrent in myfiles else None

        if myindex is not None:
            if mymodus == "next" and myindex < (len(myfiles)-1):
                mynext = myfiles[myindex + 1]
            elif mymodus == "previous" and myindex > 0:
                mynext = myfiles[myindex - 1]
            else:
                mynext = nextday(myaction,mycurrent,myuhrzeit)
        else:
            mynext = nextday(myaction,mycurrent,myuhrzeit)
    else:
        mytarget = datetime.datetime.strptime(myuhrzeit,"%H-%M-%S")
        mynext = min(myfiles,
                     key=lambda myx: abs(datetime.datetime.strptime(myx[-15:-7],
                                                                    "%H-%M-%S") - mytarget))

    return mynext


def nextday(myaction,mycurrent,myuhrzeit):
    mydir1 = os.path.dirname(mycurrent)
    mydir2 = os.path.dirname(mydir1)

    mydirlist = [(mydir2 + "/" + filename) for filename in os.listdir(mydir2)
                 if os.path.isdir(os.path.join(mydir2,filename))]
    mydirlist.sort()

    mynextdir = ""
    myindex = mydirlist.index(mydir1)
    if myaction[0] == "n" and myindex < (len(mydirlist)-1):
        mynextdir = mydirlist[myindex+1]
    elif myaction[0] == "p" and myindex > 0:
        mynextdir = mydirlist[myindex-1]

    if mynextdir != "":
        if myaction[1] == "i":
            if myaction == "pi":
                myuhrzeit = "23-59-59"
            else:
                myuhrzeit = "00-00-00"
        mynearest = nextimage("nearest",mynextdir,mycurrent,myuhrzeit)
    else:
        mynearest = mycurrent

    return mynearest




header()

myform = cgi.FieldStorage()

mycurrent0 = myform.getfirst("current", "")
mycurrent = mycurrent0.replace("../../","../")
myaction = myform.getfirst("action", "")
myuhrzeit = myform.getfirst("uhrzeit", "")

myfound = []

if myaction[1] == "i" :
    mydir1 = os.path.dirname(mycurrent)

    if myaction[0] == "p" :
        mymodus = "previous"
    else :
        mymodus = "next"

    mynext = nextimage(mymodus,mydir1,mycurrent,myuhrzeit)

    myfound.append(mynext.replace("../","../../"))
    myuhrzeit = mynext[-15:-7]
    myfound.append(myuhrzeit)

else:
    mynext = nextday(myaction,mycurrent,myuhrzeit)
    myfound.append(mynext.replace("../","../../"))
    myfound.append(myuhrzeit)

dateTimeObj = datetime.datetime.now()
 
timestampStr = dateTimeObj.strftime("%Y-%m-%d--%H-%M-%S")
 
#myfilename = "/home/xnfrxkas/public_html/webcam/cam1/visited/" + timestampStr
myfilename = "./cam1/visited/lb.txt" #+ timestampStr
myfile = open(myfilename,"w") 

myfile.write(timestampStr)

myfile.close()

json_string=json.dumps(myfound)

print(json_string)
