#!/usr/bin/env python3
# -*- coding: iso-8859-1 -*-


#print("Content-Type: text/html")    # HTML is following
#print("")                             # blank line, end of headers

import cgi
import cgitb; cgitb.enable()

import glob, os

import datetime

import json
    


def header():
    print ("Content-Type: application/json;charset=iso-8859-1")
#   print "Content-Type: text/html;charset=iso-8859-1"
    print ("")


def nextimage(mymodus,mydir,mycurrent,myuhrzeit):

    myfiles = glob.glob(mydir + "/*.jpeg")

    if mymodus != "nearest":
        myfiles.sort()
        
        myindex = myfiles.index(mycurrent) if mycurrent in myfiles else None

        if myindex != None:
            if mymodus == "next" and myindex < (len(myfiles)-1):
                mynext = myfiles[myindex + 1]
            elif mymodus == "previous" and myindex > 0:
                mynext = myfiles[myindex - 1]
            else:
                if mymodus == "next":
                    myaction = "ni"
                else:
                    myaction = "pi"
                mynext = nextday(myaction,mycurrent,myuhrzeit)
        else:
            if mymodus == "next":
                myaction = "ni"
            else:
                myaction = "pi"
            mynext = nextday(myaction,mycurrent,myuhrzeit)
    else:
        mytarget = datetime.datetime.strptime(myuhrzeit,"%H-%M-%S")
        mynext = min(myfiles, key=lambda myx: abs(datetime.datetime.strptime(myx[-13:-5],"%H-%M-%S") - mytarget))
    
    return mynext    


def nextday(myaction,mycurrent,myuhrzeit):
    
    mydird = os.path.dirname(mycurrent)
    #../../webcamarchive_y-m-d/2020/2020-05/2020-05-01/2020-05-01--13-00-03.jpeg

    
    mydirm = os.path.dirname(mydird)
    mydiry = os.path.dirname(mydirm)
    mydir0 = os.path.dirname(mydiry)
    current_day = os.path.basename(mydird)



    move_to_day = datetime.datetime.strptime(current_day, "%Y-%m-%d")


    at_the_end = False

    if myaction[0] == "n":
        sign = 1
    else:
        sign = -1
    if myaction[1] == "q":
        delta = 42
    else:
        delta = 1
    
    cnt = 0
    while 1:
        cnt = cnt + 1
        if cnt>50:
            at_the_end = True
            break
        #myfilename = "./cam1/visited/lb3.txt" #+ timestampStr
        #myfile = open(myfilename,"a") 
        #myfile.write(current_day + " " + datetime.datetime.strftime(move_to_day, "%Y-%m-%d") + "\n")
        #myfile.close() 

        move_to_day = move_to_day + datetime.timedelta(days=(delta*sign))
        delta = 1
        
        if move_to_day>datetime.datetime.now():
            at_the_end = True
            break

        if move_to_day<datetime.datetime.strptime("2018-12-14","%Y-%m-%d"):
            at_the_end = True
            break

        newy = datetime.datetime.strftime(move_to_day,"%Y")
        newm = datetime.datetime.strftime(move_to_day,"%Y-%m")
        newd = datetime.datetime.strftime(move_to_day,"%Y-%m-%d")
        
        if not os.path.exists(os.path.join(mydir0, newy)):
            at_the_end = True
            break

        mynextdir = os.path.join(mydir0, newy, newm, newd)

        if os.path.exists(mynextdir):
            break



    if at_the_end == True:
        mynearest = mycurrent
    else:
        if myaction[1] == "i":
            if myaction == "pi":
                myuhrzeit = "23-59-59"
            else:
                myuhrzeit = "00-00-00"


        mynearest = nextimage("nearest",mynextdir,mycurrent,myuhrzeit)
            
    #mydirlist = [(mydir2 + "/" + filename) for filename in os.listdir(mydir2) if os.path.isdir(os.path.join(mydir2,filename))]
    #mydirlist.sort()
    
    #mynextdir = ""
    #myindex = mydirlist.index(mydir1)
    #if myaction[0] == "n" and myindex < (len(mydirlist)-1):
    #    mynextdir = mydirlist[myindex+1];
    #elif myaction[0] == "p" and myindex > 0:
    #    mynextdir = mydirlist[myindex-1]
    #    
    #if mynextdir != "":
    #    if myaction[1] == "i":
    #        if myaction == "pi":
    #            myuhrzeit = "23-59-59"
    #        else:
    #            myuhrzeit = "00-00-00"
    #    mynearest = nextimage("nearest",mynextdir,mycurrent,myuhrzeit)
    #else:
    #    mynearest = mycurrent
    
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
    myuhrzeit = mynext[-13:-5]
    myfound.append(myuhrzeit)

else:
    mynext = nextday(myaction,mycurrent,myuhrzeit)
    myfound.append(mynext.replace("../","../../"))
    myfound.append(myuhrzeit)    

dateTimeObj = datetime.datetime.now()
 
timestampStr = dateTimeObj.strftime("%Y-%m-%d--%H-%M-%S")
 
#myfilename = "/home/xnfrxkas/public_html/webcam/cam1/visited/" + timestampStr
#myfilename = "./cam1/visited/lb.txt" #+ timestampStr
#myfile = open(myfilename,"w") 
#myfile.write(timestampStr)
#myfile.close() 

json_string=json.dumps(myfound)
    
print (json_string)

