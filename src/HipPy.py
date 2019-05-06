"""
Hex Image Processing with Python

Authors:
Ahmed Abbas
Jack Orton

steps: 
sudo modprobe v4l2loopback devices=1
v4l2-ctl --list-devices
find device name from list (called dummy device)
"""

import os
import sys
import threading                        # import threading for multithreading
import cv2                              # import image processing library
import numpy as np                      # import numpy
import time                             # import time(for timing)
from methods import *                   # import our custom methods


if os.uname()[4][:3] == 'arm':
    systype = 0                        # 0 = pi, 1 = win
elif sys.platform == 'linux':
    systype = 1
else:
    systype = 2


if systype == 0:

    # import picamera libraries only if on the pi
    from picamera.array import PiRGBArray
    from picamera import PiCamera       # import library to interface pi camera
    camera = PiCamera()
    rawCapture = PiRGBArray(camera)

elif systype == 1:

    import pyfakewebcam as pfw
    import subprocess
    num = '0'

    while int(num) < 10:

        try:
            videodevice = '/dev/video' + num
            fakecam = pfw.FakeWebcam(videodevice, 1200, 700)
            break
        except Exception as e:
            print("not /dev/video"+num, e)
            num = str(int(num)+1)

    if int(num) == 10:

        print(" Have you tried: \nsudo modprobe v4l2loopback devices=1\nv4l2-ctl - -list-devices\nfind device name from list(called dummy device)")
        sys.exit()

    # t = threading.Thread(target=subprocess.run,args=(['ffplay','/dev/video'+num],))
    # t.start()
    camera = cv2.VideoCapture(0)

else:  # systype = 2
    camera = cv2.VideoCapture(0)


width = 640                        # choose raw image width
height = 480                       # choose raw image height
count = 0
datalog = []
image = np.zeros([width, height])          # V E C T O R I Z E
imageprocessed = np.zeros([170, 770])
letter, confidence = "", 0
X, Y = 0, 0
letter, confidence = "", 0


def move(location, gps):
    """ code here for moving, will be moved to methods.py """

    print("im so moved", location, gps)


while True:

    if systype == 0:                           # if on pi
        image = getimg(camera, rawCapture)     # Capture image
    if systype == 1:                           # if on laptop
        _, image = getimgwin(camera)                    # capture image

    # process the image, Tar = True/False (target found?), contour(target outline)
    imageprocessed, tar, contour = procimg(image)

    if tar:

        if count == 4:
            try:

                letter, confidence = doocr(imageprocessed)
                if letter != ' ':
                    datalog.append((letter, confidence, X, Y))
                    datalog = confidence_sort(datalog)
                    print(datalog)
                    t1 = threading.Thread(target=move, args=(
                        (datalog[-1][2], datalog[-1][3])))
                    t1.start()
            except Exception as e:
                print(e)

            count = 0

        count = count + 1

    composit = outimg(image, imageprocessed, letter, confidence)

    if systype == 1:
        # cv2.imshow("Out",composit)
        fakecam.schedule_frame(composit)

        k = cv2.waitKey(5) & 0xFF
        if k == 27:
            break
