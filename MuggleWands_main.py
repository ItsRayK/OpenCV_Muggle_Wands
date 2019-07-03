# Application: OpenCV Muggle Wands
# Author: Rayyan Khan
# Date: 07/01/2019
#
# Description:  Create a magical experience with a webcam, infrared light, and wand.
#               This single script uses OpenCV to locate and track the brightest point in the frame.
#               The location data is then used to calculate the velocity the point has moved horizontally
#               and vertically. If the velocity is greater than the set threshold a move is registered.
#               The move can be one of UP, DOWN, LEFT, or RIGHT (Compound moves are currently a work in
#               progress).
#
#               The registered moves populate a queue of gestures from which a sequence (or spell) can be
#               verified. If a spell is triggered, the queue is cleared and will begin to repopulate with
#               new moves. However if no spell is recognized the queue will continue to populate until any
#               valid sequence matches.
#
# Dependencies: OpenCV, statistics, time
#
# Project State: Work In Progress (as of 07/02/19)

import cv2
import statistics
import time

cap = cv2.VideoCapture(0)
radius = 20
brightnessThreshold = 70

dataPointCount = 0
dataPoints = 5
xSampleSet = [0]*dataPoints
ySampleSet = [0]*dataPoints

avgx = 0
avgxPrev = 0

avgy = 0
avgyPrev = 0

dx = 0
dy = 0

velSampleCount = 0
velSamples = 5
xVelSampleSet = [0]*velSamples
yVelSampleSet = [0]*velSamples
avgxVel = 0
avgyVel = 0

velocityThreshold = 10

moveU = False
moveD = False
moveR = False
moveL = False

moveTimeout = 30
moveTimeoutCounter = moveTimeout
movementTimedout = False

UP    = 1
DOWN  = 2
LEFT  = 3
RIGHT = 4
CLR   = 5

maxGestures = 4
movesList = [CLR]*maxGestures

def title():
    print("Welcome to Muggle Wizardry 101: Wand Basics")
    print("Customize your own wand gestures!")
    print("The default is 4 move gestures.")
    print("Let's begin! (Try RIGHT,UP,LEFT,DOWN)")
    print("")

def clearMoveQueue():
    global movesList
    movesList = [CLR] * maxGestures

def queueMove(move):
    global movesList

    for i in range(len(movesList)-1):
        movesList[i] = movesList[i+1]

    movesList[-1] = move

def checkWandGesture(gestureList):
    validGesture = True
    if gestureList == [UP,RIGHT,DOWN,LEFT]:
        print("ACCIO!!!")

    elif gestureList == [UP,DOWN,UP,LEFT]:
        print("LUMOS!!!")

    elif gestureList == [UP,DOWN,UP,RIGHT]:
        print("NOX!!!")

    elif gestureList == [DOWN,RIGHT,UP,DOWN]:
        print("WINGARDIUM LEVIOSA!!!")

    elif gestureList == [RIGHT,UP,LEFT,DOWN]:
        print("ALOHOMORA!!!")

    else:
        validGesture = False

    if validGesture:
        clearMoveQueue()


title()

while True:
    ret, image = cap.read()

    # load the image and convert it to grayscale
    orig = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # the area of the image with the largest intensity value
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray)
    image = orig.copy()

    # isolate the x and y coordinates of the brightest area
    xSampleSet[dataPointCount] = maxLoc[0]
    ySampleSet[dataPointCount] = maxLoc[1]

    # calculate the average of x and y locations of brightest areas from the sample sets
    avgx = statistics.mean(xSampleSet)
    avgy = statistics.mean(ySampleSet)

    #print("Brightness: {0: <5}   X: {1: <5}   Y: {2: <5}".format(maxVal, avgx, avgy))
    if maxVal > brightnessThreshold:
        cv2.circle(image, (int(avgx),int(avgy)), radius, (0, 255, 0), 2)

        # increment sample set counter or reset counter
        dataPointCount += 1
        if dataPointCount >= dataPoints:
            dataPointCount = 0

        # populate average velocities
        xVelSampleSet[velSampleCount] = avgxPrev - avgx
        yVelSampleSet[velSampleCount] = avgyPrev - avgy

        avgxVel = statistics.mean(xVelSampleSet)
        avgyVel = statistics.mean(yVelSampleSet)

        #print("Average X Vel: {0: <5}   Average Y Vel: {1: <5}".format(int(avgxVel), int(avgyVel)))

        # +X Vel = RIGHT / +Y Vel = UP
        newMove = False
        if abs(avgxVel) > velocityThreshold:
            newMove = True
            if avgxVel > 0 and not moveR:
                moveU = False
                moveD = False
                moveL = False
                moveR = True
                #print("Moved RIGHT")
                queueMove(RIGHT)

            elif avgxVel < 0 and not moveL:
                moveU = False
                moveD = False
                moveR = False
                moveL = True
                #print("Moved LEFT")
                queueMove(LEFT)

        if abs(avgyVel) > velocityThreshold:
            newMove = True
            if avgyVel > 0 and not moveU:
                moveR = False
                moveL = False
                moveD = False
                moveU = True
                #print("Moved UP")
                queueMove(UP)

            elif avgyVel < 0 and not moveD:
                moveR = False
                moveL = False
                moveU = False
                moveD = True
                #print("Moved DOWN")
                queueMove(DOWN)

        if newMove:
            movementTimedout = False
            moveTimeoutCounter = moveTimeout
            checkWandGesture(movesList)

        # velocity sampling counter increment or reset
        velSampleCount += 1
        if velSampleCount >= velSamples:
            velSampleCount = 0

        # save last average for velocity calculation
        avgxPrev = avgx
        avgyPrev = avgy

    if not movementTimedout:
        moveTimeoutCounter -= 1
        if moveTimeoutCounter < 0:
            print("Move Timed Out!")
            moveU = False
            moveD = False
            moveR = False
            moveL = False
            movementTimedout = True
            clearMoveQueue()

    if cv2.waitKey(1) == ord('q'):
        break

    # display the results of our newly improved method
    mirrorImage = cv2.flip(image, 1)
    cv2.imshow("Wand Tracking", mirrorImage)

    time.sleep(0.05)

cap.release()
cv2.destroyAllWindows()