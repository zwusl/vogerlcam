#!/bin/bash


numprocesses=$(pgrep -c -f webcamloop.py)

if [[ $numprocesses -gt 0 ]] ; then
  echo "running"
else
  echo "Not running"
  cd /home/pi/webcam
  /usr/bin/python3 /home/pi/webcam/webcamloop.py -c /home/pi/webcam/webcam.ini
fi
