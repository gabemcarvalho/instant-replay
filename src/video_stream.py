from threading import Thread
import cv2

class VideoStream:
    def __init__(self, src=0):
        self.video_capture = cv2.VideoCapture(src)
        if isinstance(src, int):
            self.video_capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
            self.video_capture.set(cv2.CAP_PROP_FPS, 30)
            self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

        (self.grabbed, self.frame) = self.video_capture.read()
        self.frame_is_new = True
        self.stopped = False

    def start(self):
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        while True:
            if self.stopped:
                return
            (self.grabbed, self.frame) = self.video_capture.read()
            self.frame_is_new = True

    def read(self):
        self.frame_is_new = False
        return self.frame

    def stop(self):
        self.stopped = True
