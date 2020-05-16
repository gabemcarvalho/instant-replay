import numpy as np
import cv2
import time
import keyboard
import threading
import json

# load settings
with open("settings.json") as settingsFile:
    settings = json.load(settingsFile)

C_BUFFER_SIZE = settings["bufferSize"]
C_FPS = settings["fps"]
C_LIVE_DELAY_SECONDS = settings["videoDelaySeconds"]
C_LOOP_SECONDS = settings["loopedVideoLength"]
C_CAMERA_ROTATIONS = settings["cameraRotations"]

C_LIVE_VIDEO_X = 20
C_LIVE_VIDEO_Y = 40

frameBuffer = []
pFront = 0
pLive = 0
playingLooped = False
lv = None
lvName = ""
frameCounter = 0

blackFrame = np.zeros((720, 1280, 3), np.uint8)

cap = cv2.VideoCapture(settings["cameraIndex"])

spacePressedLast = False
saving = False

cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("frame", cv2.WND_PROP_ASPECT_RATIO, cv2.WINDOW_KEEPRATIO)
if settings["fullscreen"] == True:
    cv2.setWindowProperty("frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

lastTime = time.time()
k = 0
fps = 0

def saveClip(startIndex, name, width, height, frameLength):
    global lv
    global playingLooped
    saving = True
    print("saving video...")
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(name + ".avi", fourcc, C_FPS, (width, height))
    for i in range(frameLength):
        index = (C_BUFFER_SIZE + startIndex + i) % C_BUFFER_SIZE
        if index > len(frameBuffer) - 1:
            print("couldn't save video!")
            out.release()
            saving = False
            break
        saveFrame = frameBuffer[index]
        out.write(saveFrame)
    out.release()
    print("saved " + name + ".avi, looping")
    playingLooped = True
    if lv != None:
        lv.release()
    lvName = name + ".avi"
    lv = cv2.VideoCapture(lvName)
    frameCounter = 0
    saving = False

while(True):
    ret, rawFrame = cap.read()
    rotFrame = np.rot90(rawFrame, C_CAMERA_ROTATIONS).copy()

    if len(frameBuffer) < C_BUFFER_SIZE:
        frameBuffer.append(rotFrame)
    else:
        frameBuffer[pFront] = rotFrame
    
    pLive = (C_BUFFER_SIZE + pFront - C_FPS * C_LIVE_DELAY_SECONDS) % C_BUFFER_SIZE
    if pLive > len(frameBuffer) - 1: pLive = 0
    liveFrame = frameBuffer[pLive]

    pFront = (pFront + 1) % C_BUFFER_SIZE

    displayFrame = blackFrame.copy()
    displayFrame[C_LIVE_VIDEO_Y:C_LIVE_VIDEO_Y+liveFrame.shape[0], C_LIVE_VIDEO_X:C_LIVE_VIDEO_X+liveFrame.shape[1], 0:3] = liveFrame

    thisTime = time.time()
    k += 1
    if thisTime - lastTime >= 1:
        fps = k
        k = 0
        lastTime = thisTime

    if keyboard.is_pressed("space") and spacePressedLast == False:
        if saving == True:
            print("Already saving a video!")
        else:
            # save a video in another thread
            length = C_FPS * C_LOOP_SECONDS;
            startI = (C_BUFFER_SIZE + pLive - length) % C_BUFFER_SIZE
            saveThread = threading.Thread(target=saveClip, args=(startI, str(int(lastTime)), liveFrame.shape[1], liveFrame.shape[0], length))
            saveThread.start()

    spacePressedLast = keyboard.is_pressed("space");

    if playingLooped == True and lv != None:
        if lv.isOpened():
            ret, rawLoopFrame = lv.read()
            frameCounter += 1
            if frameCounter == lv.get(cv2.CAP_PROP_FRAME_COUNT):
                    lv.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    frameCounter = 0
            if ret == True:
                displayFrame[C_LIVE_VIDEO_Y:C_LIVE_VIDEO_Y+rawLoopFrame.shape[0], C_LIVE_VIDEO_X+500:C_LIVE_VIDEO_X+500+rawLoopFrame.shape[1], 0:3] = rawLoopFrame

    # cv2.rectangle(displayFrame, (0, 0), (480, 20), (0, 0, 0), -1) # note: thickness of -1 fills rectangle
    cv2.putText(displayFrame, "Frames: " + str(len(frameBuffer)), (10, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))
    cv2.putText(displayFrame, "Front: " + str(pFront), (150, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))
    cv2.putText(displayFrame, "Showing: " + str(pLive), (250, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))
    cv2.putText(displayFrame, "FPS: " + str(fps), (400, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))
    cv2.putText(displayFrame, "PRESS 'Q' TO QUIT", (500, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))
    cv2.putText(displayFrame, "PRESS 'SPACE' TO SAVE 10 SECONDS", (700, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))

    if ret: cv2.imshow("frame", displayFrame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
