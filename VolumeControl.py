import cv2 as cv
import time
import numpy as np

import HandDectectionModule as htm

######################################

from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)

#######################################

volRange = volume.GetVolumeRange() #(-96.0, 0.0, 0.125)
minVol = volRange[0]
maxVol = volRange[1]
volPercent = 0

#########################
wcam, hcam = 640, 480
#########################

cap = cv.VideoCapture(0)
cap.set(3,wcam)
cap.set(4,hcam)
ctime = 0
ptime = 0

detector = htm.handDetector(detectionCon=0.7)


while True:

    #Getting frames from camera
    success, img = cap.read()
    img = detector.findHands(img)

    lmlist = detector.findPosition(img,draw=False)
    if len(lmlist) != 0:

        # Getting Coordinates
        x1, y1 = lmlist[4][1], lmlist[4][2] # Tip of Thumb
        x2, y2 = lmlist[8][1], lmlist[8][2] # Tip of Index Finger
        cx,cy = (x1+x2)//2, (y1+y2)//2 # Centre of the line

        #Visual representation of process
        cv.circle(img,(x1,y1),10,(0,0,255),-1)
        cv.circle(img, (x2,y2), 10, (0, 0, 255), -1)
        cv.line(img,(x1,y1),(x2,y2),(0, 0, 255),3)
        cv.circle(img, (cx, cy), 10, (0, 0, 255), -1)

        #Calculating distance between tip of thumb and index finger
        distance = ((x2-x1)**2+(y2-y1)**2)**0.5

        if distance<=50:
            cv.circle(img, (cx, cy), 10, (0, 255,0), -1)

        # Hand Range = 220 to 20
        # Vol Range = -96 to 0

        #Linking Volume to the length between the two points
        vol1 = np.interp(distance,[50.0,160.0],[maxVol- 20,maxVol])
        vol2 = np. interp(distance,[20,50],[minVol,maxVol-20])

        #Adjustment of volume
        if distance<50:
            vol = vol2
        else:
            vol = vol1
        volume.SetMasterVolumeLevel(vol, None)

        #Sound Bar
        cv.rectangle(img,(50,20),(20,480-20),(0,255,0),2)
        temp = np.interp(vol,[minVol,maxVol],[0,440])
        volPercent = np.interp(vol,[minVol,maxVol],[0,100])
        cv.rectangle(img,(50,int(460-temp)),(20,460),(0,255,0),-1)


    #To get the Frame rate
    ctime = time.time()
    fps = 1/(ctime-ptime)
    ptime = ctime

    #Final Window
    img = cv.flip(img,1)
    cv.putText(img,'FPS: '+ str(int(fps)),(10,50),
               cv.FONT_HERSHEY_COMPLEX,1,(255,0,0),2)
    cv.putText(img, str(int(volPercent)) + '%', (wcam-150,50),
               cv.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
    cv.imshow('Volume Control',img)
    cv.waitKey(1)

