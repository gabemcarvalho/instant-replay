import numpy as np
import cv2
import time
import keyboard
import threading
from src.globalvar import *
import src.config as CONFIG
from src.video_stream import VideoStream

def main():

    global looped_video_current_frame_number
    
    frame_buffer = []
    front_frame_number = 0
    showing_frame_number = 0

    black_frame = np.zeros((720, 1280, 3), np.uint8)

    main_video_stream = VideoStream(src=CONFIG.CAMERA_INDEX).start()

    # main_video_capture = cv2.VideoCapture(CONFIG.CAMERA_INDEX)
    # main_video_capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
    # main_video_capture.set(cv2.CAP_PROP_FPS, 30)
    # main_video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    # main_video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

    space_pressed_last = False

    cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("frame", cv2.WND_PROP_ASPECT_RATIO, cv2.WINDOW_KEEPRATIO)
    if CONFIG.FULLSCREEN == True:
        cv2.setWindowProperty("frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    last_time = time.time()
    frames_in_last_second = 0
    real_fps = 0

    while(True):
        while True:
            if main_video_stream.frame_is_new:
                break
        raw_frame = main_video_stream.read()
        
        rotated_frame = np.rot90(raw_frame, CONFIG.CAMERA_ROTATIONS).copy()

        if len(frame_buffer) < CONFIG.BUFFER_SIZE:
            frame_buffer.append(rotated_frame)
        else:
            frame_buffer[front_frame_number] = rotated_frame
        
        showing_frame_number = (CONFIG.BUFFER_SIZE + front_frame_number - CONFIG.TARGET_FPS * CONFIG.LIVE_DELAY_SECONDS) % CONFIG.BUFFER_SIZE
        if showing_frame_number > len(frame_buffer) - 1:
            showing_frame_number = 0
        showing_frame = frame_buffer[showing_frame_number]

        front_frame_number = (front_frame_number + 1) % CONFIG.BUFFER_SIZE

        display_frame = black_frame.copy()
        display_frame[LIVE_VIDEO_POS[1]:LIVE_VIDEO_POS[1]+showing_frame.shape[0], LIVE_VIDEO_POS[0]:LIVE_VIDEO_POS[0]+showing_frame.shape[1], 0:3] = showing_frame

        current_time = time.time()
        frames_in_last_second += 1
        if current_time - last_time >= 1:
            real_fps = frames_in_last_second
            frames_in_last_second = 0
            last_time = current_time

        if keyboard.is_pressed("space") and space_pressed_last == False:
            if saving == True:
                print("Already saving a video!")
            else:
                # save a video in another thread
                start_index = (CONFIG.BUFFER_SIZE + showing_frame_number - CONFIG.TARGET_FPS * CONFIG.LOOP_SECONDS) % CONFIG.BUFFER_SIZE
                saveThread = threading.Thread(target=save_clip, args=(frame_buffer, start_index, str(int(last_time)), showing_frame.shape[1], showing_frame.shape[0]))
                saveThread.start()

        space_pressed_last = keyboard.is_pressed("space")

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

        cv2.imshow("frame", display_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # main_video_capture.release()
    main_video_stream.stop()
    cv2.destroyAllWindows()

def save_clip(frame_buffer, start_index, name, width, height):
        global looped_video_capture
        global is_playing_looped
        global saving
        global looped_video_current_frame_number
        saving = True
        print("saving video...")
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        out = cv2.VideoWriter(SAVE_DIRECTORY + name + ".avi", fourcc, CONFIG.TARGET_FPS, (width, height))
        for i in range(CONFIG.TARGET_FPS * CONFIG.LOOP_SECONDS):
            index = (CONFIG.BUFFER_SIZE + start_index + i) % CONFIG.BUFFER_SIZE
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
