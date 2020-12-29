import json

with open("settings.json") as f:
    settings = json.load(f)

CAMERA_INDEX = settings["cameraIndex"]
BUFFER_SIZE = settings["fps"] * (1 + settings["videoDelaySeconds"] + settings["loopedVideoLength"])
TARGET_FPS = settings["fps"]
LIVE_DELAY_SECONDS = settings["videoDelaySeconds"]
LOOP_SECONDS = settings["loopedVideoLength"]
CAMERA_ROTATIONS = settings["cameraRotations"]
FULLSCREEN = settings["fullscreen"]