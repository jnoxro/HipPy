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

systype = 1                        # 0 = pi, 1 = win
videodevice = '/dev/video2'



width = 640                        # choose raw image width
height = 480                       # choose raw image height
count = 0


from methods import *              # import our custom methods

if systype == 0:
    # import picamera libraries only if on the pi
    from picamera.array import PiRGBArray
    from picamera import PiCamera       # import library to interface pi camera

if systype == 1:
    import pyfakewebcam as pfw
    fakecam = pfw.FakeWebcam(videodevice, 1200, 700)

import cv2                              # import image processing library
import numpy as np                      # import numpy
import time                             # import time(for timing)

datalog = []
image = np.zeros([width, height])          # V E C T O R I Z E
imageprocessed = np.zeros([170,770])
letter,confidence = "",0
X,Y = 0,0

# setup
if systype == 0:
    camera = PiCamera()
    rawCapture = PiRGBArray(camera)
else:
    camera = cv2.VideoCapture(0)

letter,confidence = "",0

while True:

    if systype == 0:                           # if on pi
        image = getimg(camera, rawCapture)     # Capture image
    if systype == 1:                           # if on laptop
        _,image = getimgwin(camera)                    # capture image
    
    imageprocessed, tar, contour = procimg(image)   # process the image, Tar = True/False (target found?), contour(target outline)

    if tar:
        
        if count == 4:
            try:

                letter,confidence = doocr(imageprocessed)
                datalog.append((letter,confidence,X,Y))

            except Exception as e:
                print(e)
            
            count = 0
        
        count = count + 1

    composit = outimg(image,imageprocessed,letter,confidence)

    if systype == 1:
        #cv2.imshow("Out",composit)
        fakecam.schedule_frame(composit)

        k = cv2.waitKey(5) & 0xFF
        if k == 27:
            break


