"""
Hex Image Processing with Python

Authors:
Ahmed Abbas
Jack Orton

steps: 
sudo modprobe v4l2loopback devices=1
v4l2-ctl --list-devices
find device name from list (called dummy device)

run from terminal with "nice -n -10 python3 HipPy.py" for best resulst (lower number means higher priority, -20 max)
"""

import os
import sys
import threading                        # import threading for multithreading
import cv2                              # import image processing library
import numpy as np                      # import numpy
import time                             # import time(for timing)
from methods import *                   # import our custom methods
import imutils                          #image capture library with #threading (much faster pi image capture)
from imutils.video import VideoStream   #thrreeaddinngg
import pigpio                           #GPIO for software serial

if os.uname()[4][:3] == 'arm':
    systype = 0                        # 0 = pi, 1 = win
elif sys.platform == 'linux':
    systype = 1
else:
    systype = 2


if systype == 0:

    """old image capture, may not be needed"""
    # import picamera libraries only if on the pi
   # from picamera.array import PiRGBArray
   # from picamera import PiCamera       # import library to interface pi camera
   # camera = PiCamera()
   # camera.resolution = (640, 480)
   # rawCapture = PiRGBArray(camera)

    """new #supercool image capture - needs testing"""
    vidstream = VideoStream(src=0, usePiCamera=True, resolution=(640,480), framerate=32).start()
    time.sleep(1.0)



elif systype == 1:

    """og image capture"""
    #camera = cv2.VideoCapture(0)

    """new #supercool image capture"""
    vidstream = VideoStream(src=0, usePiCamera=False, resolution=(640,480), framerate=32).start()
#    time.sleep(2.0)


else:  # systype = 2
    camera = cv2.VideoCapture(0)

#if systype == 0:
#    RX = 18
#    TX = 23
#    pi = pigpio.pi()
#    pi.set_mode(RX, pigpio.INPUT)
#    pi.set_mode(TX, pigpio.OUTPUT)
#    pi.wave_clear()


#import pyfakewebcam as pfw
#import subprocess
#num = '1' #start from 1 so video0 (picam) isnt used - we can set device manually to avoid th need for this later on
#while int(num) < 10:
#    try:
        #videodevice = '/dev/video' + num
        #fakecam = pfw.FakeWebcam(videodevice, 1280, 720)
print("--------------- HipPy RUNNING") #mario 4 lyf
#        pass
#        break
#    except Exception as e:
        #print("not /dev/video"+num, e)
        #num = str(int(num)+1)
#        pass

#if int(num) == 10:
#    print(" Have you tried: \nsudo modprobe v4l2loopback devices=1\nv4l2-ctl - -list-devices\nfind device name from list(called dummy device)")
#    sys.exit()


file = open("log.txt","w")
file.write("START\n\n")
file.close

width = 640                        # choose raw image width
height = 480                       # choose raw image height
count = 0
datalog = []
image = np.zeros([width, height], dtype=np.uint8)          # V E C T O R I Z E  -- causing erros with pi cam removed 4 testing
imageprocessed = np.zeros([80, 250], dtype=np.uint8)
#composit = np.zeros([720, 1280], dtype=np.uint8)
composit = np.ndarray((720, 1280, 3), dtype=np.uint8)
letter, confidence = "", 0
X, Y = 0, 0
letter, confidence = "", 0
fps, fpsold, fpsproc, fpsprocold = 0, 0, 0, 0
num, compcount = 0, 0
lat,long = 2.00,2.00
path = r'ramdrive/'


def move(location, gps):
    """ code here for moving, will be moved to methods.py """

    # print("im so moved", location, gps)

#def getgps():
#    pi.wave_clear()
#    pi.wave_add_serial(TX, 9600, 'tar')
#    tarwave = pi.wave_create()
#    print("sending GPS request")
#    pi.wave_send_once(tarwave)
#    rec = 0
#    data = ''
#    #time.sleep(1)
#    pi.bb_serial_read_open(RX, 9600, 8)
#    time.sleep(1)
#    reqtime = time.time()
#    while 1:
#        print("waiting for response")
#        (rec, data) = pi.bb_serial_read(RX)    
#        if rec:
#            pi.bb_serial_read_close(RX)
#            return data
#        time.sleep(0.5)
   
    



while True:
    begintime = time.time()

    if systype == 0:                           # if on pi
        #og method
        #image = getimg(camera, rawCapture)     # Capture image
        #rawCapture.truncate(0)

        #new - needs testing - should increase fps by a decent amount (when tesseract not running):
        image = vidstream.read()

    if systype == 1:                           # if on laptop
        #og:
        #_, image = getimgwin(camera)                    # capture image

        #new
        image = vidstream.read()
        image = np.uint8(imutils.resize(image, width=640)) #only needed when not using picam
    
    

    # process the image, Tar = True/False (target found?), contour(target outline)
    imageprocessed, tar, contour = procimg(image)

    if tar:
        count = count + 1

        if count == 10:
            count = 0
            
            try:
                #gpscoords = getgps().decode()
                
                #if not gpscoords == '':
                   # print("gps received :)")
                   # print(gpscoords)
                   # long,lat = [float(x) for x in gpscoords.split(",")]
                #else:
                   # long,lat = 5,5
                
                #for i in range(20):
                    # print(long,lat)
    
                file = open("log.txt","r")
                tardata = file.readlines()[-1].rstrip('\n')
                print("---------------", tardata)
                try:
                    letter,lat,long = [x for x in tardata.split(",")]  #tardata.split(",")  
                except:
                    print("--------------- Unable to parse log")
                #file.seek(0,0)
                #letter = file.read()[-2]                    
                file.close()    
                name = r'ocrimg' + str(num) + r'.png'
                print("--------------- Image saved to ram?: ", cv2.imwrite(os.path.join(path,name),imageprocessed))
                num = num + 1
                
    
                if letter != ' ' and letter != '' and letter != '\n':
                    datalog.append((letter, confidence, X, Y))
                    datalog = confidence_sort(datalog)
                    print("---------------",datalog)
                    t1 = threading.Thread(target=move, args=(
                           (datalog[-1][2], datalog[-1][3])))
                    t1.start()

            except Exception as e:
                print("---------------",e)


    composit = outimg(image, imageprocessed, lat, long, letter, confidence, fps, fpsproc)

    endtime1 = time.time()    ##uncomment for processing fps

    if systype == 0:
        #fakecam.schedule_frame(composit)

        fwstart = time.time()

        #fakecam.schedule_frame(composit) #ew
        #try:
        #    name2 = r'img' + str(compcount) + r'.bmp'
        #    #print(str(name2))
        #    #print(str(path))
        #    cv2.imwrite(os.path.join(path,name2), composit) 
        #    compcount = compcount+1
        #    #print(compcount)
        #    if compcount >= 100:
        #        name3 = r'img' + str(compcount-100) + r'.bmp'
        #        os.remove(os.path.join(path,name3))
        #except Exception as e:
        #    print(e)
        
        name2 = r'img' + str(1) + r'.bmp'
        cv2.imwrite(os.path.join(path,name2), composit)

        fwend = time.time()

    if systype == 1:
        
        fwstart = time.time()
        #cv2.imshow("Out",composit)
        #print('bloop')
        fakecam.schedule_frame(composit)
        fwend = time.time()
        # print(fwend-fwstart)

    endtime2 = time.time()    ##uncomment for actual fps
    frametime = endtime2 - begintime
    processingtime = endtime1 - begintime
    fpsold = fps
    fpsprocold = fpsproc
    fps = 1/frametime
    fpsproc = 1/processingtime
    fps = round((fps + fpsold)/2)
    fpsproc = round((fpsproc + fpsprocold)/2)
#   print(fps)
    
    
    
    

    
