import numpy as np
import cv2
import time
import keyboard
import threading

C_BUFFER_SIZE = 1200
C_FPS = 30
C_LIVE_DELAY_SECONDS = 10 # 15

C_LIVE_VIDEO_X = 20
C_LIVE_VIDEO_Y = 40

aaaa = []
pFront = 0
pLive = 0

blackFrame = np.zeros((720, 1280, 3), np.uint8)

cap = cv2.VideoCapture(0)

spacePressed = False
saving = False

cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("frame", cv2.WND_PROP_ASPECT_RATIO, cv2.WINDOW_KEEPRATIO)
cv2.setWindowProperty("frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

lastTime = time.time()
k = 0
fps = 0

def save(startIndex, name, width, height, frameLength):
    saving = True
    print("saving video...")
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(name + ".avi", fourcc, C_FPS, (width, height))
    for i in range(frameLength):
        index = (C_BUFFER_SIZE + startIndex + i) % C_BUFFER_SIZE
        if index > len(aaaa) - 1:
            print("couldn't save video!")
            out.release()
            break
        saveFrame = aaaa[index]
        out.write(saveFrame)
    out.release()
    print("saved " + name + ".avi")
    saving = False

while(True):
    ret, rawFrame = cap.read()
    rotFrame = np.rot90(rawFrame).copy()

    if len(aaaa) < C_BUFFER_SIZE:
        aaaa.append(rotFrame)
    else:
        aaaa[pFront] = rotFrame
    
    pLive = (C_BUFFER_SIZE + pFront - C_FPS * C_LIVE_DELAY_SECONDS) % C_BUFFER_SIZE
    if pLive > len(aaaa) - 1: pLive = 0
    liveFrame = aaaa[pLive]

    pFront = (pFront + 1) % C_BUFFER_SIZE

    displayFrame = blackFrame.copy()
    displayFrame[C_LIVE_VIDEO_Y:C_LIVE_VIDEO_Y+liveFrame.shape[0], C_LIVE_VIDEO_X:C_LIVE_VIDEO_X+liveFrame.shape[1], 0:3] = liveFrame

    thisTime = time.time()
    k += 1
    if thisTime - lastTime >= 1:
        fps = k
        k = 0
        lastTime = thisTime

    # cv2.rectangle(displayFrame, (0, 0), (480, 20), (0, 0, 0), -1) # note: thickness of -1 fills rectangle
    cv2.putText(displayFrame, "Frames: " + str(len(aaaa)), (10, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))
    cv2.putText(displayFrame, "Front: " + str(pFront), (150, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))
    cv2.putText(displayFrame, "Showing: " + str(pLive), (250, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))
    cv2.putText(displayFrame, "FPS: " + str(fps), (400, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))
    cv2.putText(displayFrame, "PRESS 'Q' TO QUIT", (500, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))
    cv2.putText(displayFrame, "PRESS 'SPACE' TO SAVE 10 SECONDS", (700, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))

    if keyboard.is_pressed("space") and spacePressed == False:
        if saving == True:
            print("Already saving a video!")
        else:
            # save a video in another thread
            length = C_FPS * 10;
            startI = (C_BUFFER_SIZE + pLive - length) % C_BUFFER_SIZE
            saveThread = threading.Thread(target=save, args=(startI, str(int(lastTime)), 480, 640, length))
            saveThread.start()
        spacePressed = True;

    spacePressed = keyboard.is_pressed("space");

    if ret: cv2.imshow("frame", displayFrame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
