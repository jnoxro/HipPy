"""
(v4l2 needs python 2)
do this thing: sudo modprobe v4l2loopback

"""
import fcntl, sys, os
print("imported fcntl, sys and os")
import v4l2
print("imported v4l2")


print(__name__)

if __name__ == "__main__":
    devName = '/dev/video2'
