"""
Hex Image Processing with Python

Authors:
Ahmed Abbas
Jack Orton
"""
systype = 0                         #0 = pi, 1 = win
width = 640                         #choose raw image width
height = 480                        #choose raw image height


from methods import *               #import our custom methods
from picamera.array import PiRGBArray
from picamera import PiCamera       #import library to interface pi camera
import cv2                          #import image processing library
import numpy                        #import numpy
import time                         #import time(for timing)


image = np.zeros(width, height)          # V E C T O R I Z E 
imageprocessed = np.zeros(170,770)

#setup
camera = PiCamera()
rawCapture = PiRGBArray(camera)

while true:
    if systype == 0:                           #if on pi
        image = getimg(camera, rawCapture)     #Capture image
    if systype == 1:                           #if on lapop
        image = getimgwin()                    #capture image
    
    imageprocessed, tar, contour = procimg(image)   #process the image, Tar = True/False (target found?), contour(target outline)

    if tar:
        




