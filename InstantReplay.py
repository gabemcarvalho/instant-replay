import numpy as np
import cv2
import time
import keyboard
import threading
import os
import pygame
from src.globalvar import *
import src.config as CONFIG
from src.video_stream import VideoStream

def main():
    #print(cv2.videoio_registry.getCameraBackends())
    global looped_video_current_frame_number
    
    frame_buffer = []
    front_frame_number = 0
    showing_frame_number = 0

    main_video_stream = VideoStream(src=CONFIG.CAMERA_INDEX, width=CONFIG.CAMERA_WIDTH, height=CONFIG.CAMERA_HEIGHT).start()
    saveThread = None

    space_pressed_last = False

    # configure pygame
    pygame.init()
    frame_width = CONFIG.CAMERA_WIDTH if (CONFIG.CAMERA_ROTATIONS % 2 == 0) else CONFIG.CAMERA_HEIGHT
    frame_height = CONFIG.CAMERA_HEIGHT if (CONFIG.CAMERA_ROTATIONS % 2 == 0) else CONFIG.CAMERA_WIDTH
    frame_size = (frame_width * 2, frame_height)
    pygame.display.set_caption("Instant Replay by Gabe Carvalho")
    if CONFIG.FULLSCREEN:
        screen = pygame.display.set_mode(frame_size, pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode(frame_size)
    font = pygame.font.Font("SpaceMono-Regular.ttf", 16)

    last_time = time.perf_counter()
    last_fps_time = last_time
    frames_in_last_second = 0
    real_fps = 0
    camera_fps = 0
    
    if not os.path.exists('clips'):
        os.makedirs('clips')

    while(True):
        # limit fps
        current_time = time.perf_counter()
        if CONFIG.CAP_GRAPHICS_FPS:
            time.sleep(max(last_time + 1.0 / CONFIG.TARGET_FPS - current_time - 0.002, 0.0)) # sleep until next frame
            while True:
                current_time = time.perf_counter()
                if current_time - last_time >= 1.0 / CONFIG.TARGET_FPS:
                    break
            last_time = current_time
        
        # read the framerate
        frames_in_last_second += 1
        if current_time - last_fps_time >= 1.0:
            real_fps = frames_in_last_second
            camera_fps = main_video_stream.read_fps()
            frames_in_last_second = 0
            last_fps_time = current_time
        
        # get the newest frame
        raw_frame = main_video_stream.read()
        
        rotated_frame = np.rot90(raw_frame, CONFIG.CAMERA_ROTATIONS).copy()
        rotated_frame = raw_frame

        if len(frame_buffer) < CONFIG.BUFFER_SIZE:
            frame_buffer.append(rotated_frame)
        else:
            frame_buffer[front_frame_number] = rotated_frame
        
        showing_frame_number = (CONFIG.BUFFER_SIZE + front_frame_number - CONFIG.TARGET_FPS * CONFIG.LIVE_DELAY_SECONDS) % CONFIG.BUFFER_SIZE
        if showing_frame_number > len(frame_buffer) - 1:
            showing_frame_number = 0
        showing_frame = frame_buffer[showing_frame_number]
        front_frame_number = (front_frame_number + 1) % CONFIG.BUFFER_SIZE
        
        # save a clip
        if keyboard.is_pressed("space") and space_pressed_last == False:
            if saving == True:
                print("Already saving a video!")
            else:
                start_index = (CONFIG.BUFFER_SIZE + showing_frame_number - CONFIG.TARGET_FPS * CONFIG.LOOP_SECONDS) % CONFIG.BUFFER_SIZE
                saveThread = threading.Thread(target=save_clip, args=(frame_buffer, start_index, str(int(last_time)), showing_frame.shape[1], showing_frame.shape[0]))
                saveThread.start()
        space_pressed_last = keyboard.is_pressed("space")

        # play looped clip
        if is_playing_looped == True and looped_video_capture != None:
            if looped_video_capture.isOpened():
                ret, raw_loop_frame = looped_video_capture.read()
                raw_loop_frame[:, :, [0, 2]] = raw_loop_frame[:, :, [2, 0]] # swap R and B channels
                looped_video_current_frame_number += 1
                if looped_video_current_frame_number == looped_video_capture.get(cv2.CAP_PROP_FRAME_COUNT):
                        looped_video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        looped_video_current_frame_number = 0
                if ret == True:
                    # assuming looped video is the same size as the camera stream
                    loop_surface = pygame.surfarray.make_surface(raw_loop_frame)
                    screen.blit(loop_surface, (frame_width + 1, 0))

        # draw to the screen
        live_camera_surface = pygame.surfarray.make_surface(showing_frame)
        screen.blit(live_camera_surface, (0, 0))
        
        if CONFIG.FPS_OVERLAY:
            text_string = " Camera FPS: " + str(camera_fps) + " | Graphics FPS: " + str(real_fps) + " "
            text_surface = font.render(text_string, True, (0, 0, 0), (255, 255, 255))
            screen.blit(text_surface, (0, 0))
        
        pygame.display.flip()
        
        # need some code to lock fps to 30

        if keyboard.is_pressed("esc"):
            break
    
    pygame.display.quit()
    main_video_stream.stop()
    if looped_video_capture != None:
        if looped_video_capture.isOpened():
            looped_video_capture.release();

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
            save_frame = frame_buffer[index].copy()
            save_frame[:, :, [0, 2]] = save_frame[:, :, [2, 0]] # swap R and B channels
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
