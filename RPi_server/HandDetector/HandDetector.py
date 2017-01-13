# import the necessary packages
import sys
print (sys.version)
from PiVideoStream import *
import time
import cv2
import numpy as np
import math
import random
import binascii
import struct
import vl6180 as i2c

# initialize the camera and grab a reference to the raw camera capture
FRAME_HEIGHT = 320
FRAME_WIDTH = 240
FRAME_RATE = 30

"""
camera = PiCamera()
camera.resolution = (FRAME_HEIGHT, FRAME_WIDTH)
camera.framerate = FRAME_RATE
camera.awb_mode="off"
camera.awb_gains = (0.9, 0.9)
rawCapture = PiRGBArray(camera, size=(FRAME_HEIGHT, FRAME_WIDTH))
"""

camera = PiVideoStream(resolution=(FRAME_HEIGHT, FRAME_WIDTH), framerate=FRAME_RATE, awb_gains=(1.8, 1.8), ISO=400)

# allow the camera to warmup

# initial min and max HSV filter values.
# these will be changed using trackbars
H_MIN = 0
H_MAX = 255
S_MIN = 0
S_MAX = 255
V_MIN = 0
V_MAX = 255
erode_size = 1
dilate_size = 1
e_i = 1
d_i = 1
# default capture width and height
# max number of objects to be detected in frame
MAX_NUM_OBJECTS=5;
# minimum and maximum object area
MIN_OBJECT_AREA = 20*20;
MAX_OBJECT_AREA = FRAME_HEIGHT*FRAME_WIDTH/1.5;
# names that will appear at the top of each window
windowName = "Original Image"
windowName1 = "HSV Image"
windowName2 = "Thresholded Image"
windowName3 = "After Morphological Operations"
trackbarWindowName = "Trackbars"

x = 0
y = 0
objectFound = False

wait = int(math.ceil(1000/FRAME_RATE))

"""
void on_trackbar( int, void* )
{//This function gets called whenever a
// trackbar position is changed
}
"""

def nothing(x):
    pass

def createTrackbars():
    # create window for trackbars
    cv2.namedWindow(trackbarWindowName);
    # create trackbars and insert them into window
    # 3 parameters are: the address of the variable that is changing when the trackbar is moved(eg.H_LOW),
    # the max value the trackbar can move (eg. H_HIGH),
    # and the function that is called whenever the trackbar is moved(eg. on_trackbar)
    cv2.createTrackbar("H_MAX", trackbarWindowName, H_MAX, 255, nothing)
    cv2.createTrackbar("S_MAX", trackbarWindowName, S_MAX, 255, nothing)
    cv2.createTrackbar("V_MAX", trackbarWindowName, V_MAX, 255, nothing)
    cv2.createTrackbar("H_MIN", trackbarWindowName, H_MIN, 255, nothing)
    cv2.createTrackbar("S_MIN", trackbarWindowName, S_MIN, 255, nothing)
    cv2.createTrackbar("V_MIN", trackbarWindowName, V_MIN, 255, nothing)
    cv2.createTrackbar("E_SIZE", trackbarWindowName, erode_size, 20, nothing)
    cv2.createTrackbar("D_SIZE", trackbarWindowName, dilate_size, 20, nothing)
    cv2.createTrackbar("E_ITER", trackbarWindowName, e_i, 3, nothing)
    cv2.createTrackbar("D_ITER", trackbarWindowName, d_i, 3, nothing)

def drawObject(frame):
    # use some of the openCV drawing functions to draw crosshairs
    # on your tracked image!
    # UPDATE:JUNE 18TH, 2013
    # added 'if' and 'else' statements to prevent
    # memory errors from writing off the screen (ie. (-25,-25) is not within the window!)

    cv2.circle(frame,(x,y),20,(0,255,0),2)
    if y-25 > 0:
        cv2.line(frame,(x,y),(x,y-25),(0,255,0),2)
    else:
        cv2.line(frame,(x,y),(x,0),(0,255,0),2)
    if y+25 < FRAME_HEIGHT:
        cv2.line(frame,(x,y),(x,y+25),(0,255,0),2)
    else:
        cv2.line(frame,(x,y),(x,FRAME_HEIGHT),(0,255,0),2)
    if x-25 > 0:
        cv2.line(frame,(x,y),(x-25,y),(0,255,0),2)
    else:
        cv2.line(frame,(x,y),(0,y),(0,255,0),2)
    if x+25 < FRAME_WIDTH:
        cv2.line(frame,(x,y),(x+25,y),(0,255,0),2)
    else:
        cv2.line(frame,(x,y),(FRAME_WIDTH,y),(0,255,0),2)
    cv2.putText(frame,"{0},{1}".format(x, y),(x,y+30),1,1,(0,255,0),2)

    return frame


def morphOps(thresh):
    # create structuring element that will be used to "dilate" and "erode" image.
    # the element chosen here is a 3px by 3px rectangle
    erodeElement = cv2.getStructuringElement(cv2.MORPH_RECT, (erode_size, erode_size))
    # dilate with larger element so make sure object is nicely visible
    dilateElement = cv2.getStructuringElement(cv2.MORPH_RECT, (dilate_size, dilate_size))
    # erode(thresh,thresh,erodeElement);
    thresh = cv2.erode(thresh, erodeElement, e_i);
    # dilate(thresh,thresh,dilateElement);
    thresh = cv2.dilate(thresh,dilateElement, d_i);

    return thresh

def trackFilteredObject(threshold, cameraFeed):
    # find contours of filtered image using openCV findContours function
    im2, contours, hierarchy = cv2.findContours(threshold, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    # use moments method to find our filtered object
    refArea = 0.0
    global x, y, objectFound
    objectFound = False
    if hierarchy is not None:
        #for i in range(len(contours)):
        #    cv2.drawContours(cameraFeed, contours, i, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), 1, 8, hierarchy)
        numObjects = hierarchy.shape[1]
        #print numObjects
        # if number of objects greater than MAX_NUM_OBJECTS we have a noisy filter
        if numObjects < MAX_NUM_OBJECTS:
            #print numObjects
            #for i in range(len(contours)):
            #    cv2.drawContours(cameraFeed, contours, i, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), 1, 8, hierarchy)
            counter = 0
            index = 0
            while counter < hierarchy.shape[1]:
                moment = cv2.moments(contours[index])
                area = moment["m00"]
                #print area
                # if the area is less than 20 px by 20px then it is probably just noise
                # if the area is the same as the 3/2 of the image size, probably just a bad filter
                # we only want the object with the largest area so we safe a reference area each
                # iteration and compare it to the area in the next iteration.
                if area > MIN_OBJECT_AREA and area > refArea:
                    x = moment["m10"] / area
                    y = moment["m01"] / area
                    objectFound = True
                    #print objectFound
                    refArea = area
                # let user know you found an object
                counter += 1
                index = hierarchy[0][index][0]
        if objectFound:
            cv2.putText(cameraFeed,"Tracking Object",(0,50),2,1,(0,255,0),2);
        # draw object location on screen
        # drawObject(x,y,cameraFeed)
        else:
            cv2.putText(cameraFeed,"TOO MUCH NOISE! ADJUST FILTER",(0,50),1,2,(0,0,255),2)

    return cameraFeed

import socket
import os, os.path

socketFile = "../communicate.sock"

if os.path.exists(socketFile):
    os.remove(socketFile)

print "Opening socket..."

server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind(socketFile)
server.listen(5)

print "Listen..."

conn, addr = server.accept()

print "Accept client!"
print "Initial camera and ToF..."
#createTrackbars()
camera.start()
#device_handler = i2c.init(1)
time.sleep(2)

print "Start detection!"

erode_size = 3
dilate_size = 8
e_i = 1
d_i = 2

firstTrans = True
#halfTime = True

# capture frames from the camera
while not camera.isStop():
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    image = camera.read()
    #if halfTime:
#	ToFDistance = i2c.get_distance(device_handler)
#	halfTime = False
#    else: halfTime = True
    #print ToFDistance
    #cv2.imshow(windowName, image)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    """
    H_MAX = cv2.getTrackbarPos("H_MAX", trackbarWindowName)
    H_MIN = cv2.getTrackbarPos("H_MIN", trackbarWindowName)
    S_MAX = cv2.getTrackbarPos("S_MAX", trackbarWindowName)
    S_MIN = cv2.getTrackbarPos("S_MIN", trackbarWindowName)
    V_MAX = cv2.getTrackbarPos("V_MAX", trackbarWindowName)
    V_MIN = cv2.getTrackbarPos("V_MIN", trackbarWindowName)
    erode_size = cv2.getTrackbarPos("E_SIZE", trackbarWindowName)
    dilate_size = cv2.getTrackbarPos("D_SIZE", trackbarWindowName)
    e_i = cv2.getTrackbarPos("E_ITER", trackbarWindowName)
    d_i = cv2.getTrackbarPos("D_ITER", trackbarWindowName)
    """

    #threshold = cv2.inRange(hsv, (H_MIN, S_MIN, V_MIN), (H_MAX, S_MAX, V_MAX))
    threshold = cv2.inRange(hsv, (23, 124, 45), (45, 232, 169))
    threshold = morphOps(threshold)
    #cv2.imshow(windowName3, threshold)
    temp = trackFilteredObject(threshold, image)
    #print temp
    #print objectFound
    if objectFound:
        #image = drawObject(temp)
        #print "sdfsdfsdfsdfsddfsdfsdfsdfsdfsdfsdfsdfsdfsdfsdfsdfsdfsdfsdfsdfsdfsdfsdfsdf"
	print "objectFound: {0}".format((x, y))
	
        if firstTrans:
            bax = struct.pack("f", x)
            bay = struct.pack("f", y)
            binary_string = "%s%s" % (bax, bay)
            #print "sending: {0}".format(binary_string)
            conn.send(binary_string)
            firstTrans = False
        else:
            data = conn.recv(32)
            if data:
                bax = struct.pack("f", x)
                bay = struct.pack("f", y)
                binary_string = "%s%s" % (bax, bay)
                #print "sending: {0}".format(binary_string)
                conn.send(binary_string)
                
    else:
        #image = temp
	print "None detected"
	
        if firstTrans:
            conn.send("None detected")
            firstTrans = False
        else:
            data = conn.recv(32)
            if data:
                conn.send("None detected")

    #cv2.imshow(windowName, image)
    #cv2.imshow(windowName1, hsv)
    #cv2.imshow("Contours", im2)
    #cv2.imshow(windowName3, threshold)

    key = cv2.waitKey(wait)

    # clear the stream in preparation for the next frame

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

#cv2.destroyAllWindows()
camera.stop()
conn.close()
