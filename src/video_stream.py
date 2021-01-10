from threading import Thread
import cv2
import time

class VideoStream:
    def __init__(self, src=0, width=640, height=320):
        self.video_capture = cv2.VideoCapture(src, cv2.CAP_ANY)
        if isinstance(src, int):
            # MJPEG and YUYV are valid for the Logitech C270 webcam
            self.video_capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YUYV')) 
            self.video_capture.set(cv2.CAP_PROP_FPS, 30)
            self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.video_capture.set(cv2.CAP_PROP_EXPOSURE, 20)
            print("BACKEND: " + str(self.video_capture.get(cv2.CAP_PROP_BACKEND)))

        (self.grabbed, self.frame) = self.video_capture.read()
        self.frame_is_new = True
        self.stopped = False
        self.frames_in_last_second = 0

    def start(self):
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        while True:
            if self.stopped:
                return
            (self.grabbed, self.frame) = self.video_capture.read()
            self.frame[:, :, [0, 2]] = self.frame[:, :, [2, 0]] # swap R and B channels
            self.frame_is_new = True
            self.frames_in_last_second += 1

    def read(self):
        self.frame_is_new = False
        return self.frame

    def stop(self):
        self.stopped = True
        
    def read_fps(self):
        fps = self.frames_in_last_second
        self.frames_in_last_second = 0
        return fps
