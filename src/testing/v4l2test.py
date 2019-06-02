"""
(v4l2 needs python 2)
do this thing: sudo modprobe v4l2loopback

update (may do python 3 yay)
https://github.com/jremmons/pyfakewebcam/blob/master/examples/flashing_doge.py

first do:
sudo modprobe v4l2loopback devices=1

then
v4l2-ctl--list-devices

find new fake device name

"""
import numpy as np
import pyfakewebcam as pfw
import time

blue = np.zeros((720,1280,3), dtype=np.uint8)
blue[:,:,2] = 255

red = np.zeros((720,1280,3), dtype=np.uint8)
red[:,:,0] = 255

cam = pfw.FakeWebcam('/dev/video2', 1280, 720)

while True:

    cam.schedule_frame(red)
    time.sleep(2)

    cam.schedule_frame(blue)
    time.sleep(2)