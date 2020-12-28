import numpy as np
import cv2
import time
import keyboard
import threading
import json

# constants
LIVE_VIDEO_POS = (20, 40)
SAVE_DIRECTORY = "clips/"

# global variables
is_playing_looped = False
looped_video_capture = None
looped_video_current_frame_number = 0
saving = False

# load settings (these should probably be defined in a separate Settings)
with open("settings.json") as settingsFile:
    settings = json.load(settingsFile)

BUFFER_SIZE = settings["fps"] * (1 + settings["videoDelaySeconds"] + settings["loopedVideoLength"])
TARGET_FPS = settings["fps"]
LIVE_DELAY_SECONDS = settings["videoDelaySeconds"]
LOOP_SECONDS = settings["loopedVideoLength"]
CAMERA_ROTATIONS = settings["cameraRotations"]

def main():

    global looped_video_current_frame_number
    
    frame_buffer = []
    front_frame_number = 0
    showing_frame_number = 0

    black_frame = np.zeros((720, 1280, 3), np.uint8)

    main_video_capture = cv2.VideoCapture(settings["cameraIndex"])

    spacePressedLast = False

    cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("frame", cv2.WND_PROP_ASPECT_RATIO, cv2.WINDOW_KEEPRATIO)
    if settings["fullscreen"] == True:
        cv2.setWindowProperty("frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    last_time = time.time()
    frames_in_last_second = 0
    real_fps = 0

    while(True):
        ret, raw_frame = main_video_capture.read()
        rotated_frame = np.rot90(raw_frame, CAMERA_ROTATIONS).copy()

        if len(frame_buffer) < BUFFER_SIZE:
            frame_buffer.append(rotated_frame)
        else:
            frame_buffer[front_frame_number] = rotated_frame
        
        showing_frame_number = (BUFFER_SIZE + front_frame_number - TARGET_FPS * LIVE_DELAY_SECONDS) % BUFFER_SIZE
        if showing_frame_number > len(frame_buffer) - 1:
            showing_frame_number = 0
        showing_frame = frame_buffer[showing_frame_number]

        front_frame_number = (front_frame_number + 1) % BUFFER_SIZE

        display_frame = black_frame.copy()
        display_frame[LIVE_VIDEO_POS[1]:LIVE_VIDEO_POS[1]+showing_frame.shape[0], LIVE_VIDEO_POS[0]:LIVE_VIDEO_POS[0]+showing_frame.shape[1], 0:3] = showing_frame

        current_time = time.time()
        frames_in_last_second += 1
        if current_time - last_time >= 1:
            real_fps = frames_in_last_second
            frames_in_last_second = 0
            last_time = current_time

        if keyboard.is_pressed("space") and spacePressedLast == False:
            if saving == True:
                print("Already saving a video!")
            else:
                # save a video in another thread
                start_index = (BUFFER_SIZE + showing_frame_number - TARGET_FPS * LOOP_SECONDS) % BUFFER_SIZE
                saveThread = threading.Thread(target=save_clip, args=(frame_buffer, start_index, str(int(last_time)), showing_frame.shape[1], showing_frame.shape[0]))
                saveThread.start()

        spacePressedLast = keyboard.is_pressed("space")

        if is_playing_looped == True and looped_video_capture != None:
            if looped_video_capture.isOpened():
                ret, rawLoopFrame = looped_video_capture.read()
                looped_video_current_frame_number += 1
                if looped_video_current_frame_number == looped_video_capture.get(cv2.CAP_PROP_FRAME_COUNT):
                        looped_video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        looped_video_current_frame_number = 0
                if ret == True:
                    display_frame[LIVE_VIDEO_POS[1]:LIVE_VIDEO_POS[1]+rawLoopFrame.shape[0], LIVE_VIDEO_POS[0]+500:LIVE_VIDEO_POS[0]+500+rawLoopFrame.shape[1], 0:3] = rawLoopFrame

        # cv2.rectangle(display_frame, (0, 0), (480, 20), (0, 0, 0), -1) # note: thickness of -1 fills rectangle
        cv2.putText(display_frame, "Frames: " + str(len(frame_buffer)), (10, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))
        cv2.putText(display_frame, "Front: " + str(front_frame_number), (150, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))
        cv2.putText(display_frame, "Showing: " + str(showing_frame_number), (250, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))
        cv2.putText(display_frame, "FPS: " + str(real_fps), (400, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))
        cv2.putText(display_frame, "PRESS 'Q' TO QUIT", (500, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))
        cv2.putText(display_frame, "PRESS 'SPACE' TO SAVE 10 SECONDS", (700, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))

        if ret: cv2.imshow("frame", display_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    main_video_capture.release()
    cv2.destroyAllWindows()

def save_clip(frame_buffer, start_index, name, width, height):
        global looped_video_capture
        global is_playing_looped
        global saving
        global looped_video_current_frame_number
        saving = True
        print("saving video...")
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        out = cv2.VideoWriter(SAVE_DIRECTORY + name + ".avi", fourcc, TARGET_FPS, (width, height))
        for i in range(TARGET_FPS * LOOP_SECONDS):
            index = (BUFFER_SIZE + start_index + i) % BUFFER_SIZE
            if index > len(frame_buffer) - 1:
                print("couldn't save video!")
                out.release()
                saving = False
                break
            save_frame = frame_buffer[index]
            out.write(save_frame)
        out.release()
        print("saved " + name + ".avi, looping")
        is_playing_looped = True
        if looped_video_capture != None:
            looped_video_capture.release()
        looped_video_capture = cv2.VideoCapture(SAVE_DIRECTORY + name + ".avi")
        looped_video_current_frame_number = 0
        saving = False

if __name__ == '__main__':
    main()
