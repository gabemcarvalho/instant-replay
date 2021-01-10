import json

with open("settings.json") as f:
    settings = json.load(f)

CAMERA_INDEX = settings["cameraIndex"]
CAMERA_WIDTH = settings["cameraWidth"]
CAMERA_HEIGHT = settings["cameraHeight"]
CAMERA_ROTATIONS = settings["cameraRotations"]
TARGET_FPS = settings["fps"]
LIVE_DELAY_SECONDS = settings["videoDelaySeconds"]
LOOP_SECONDS = settings["loopedVideoLength"]
BUFFER_SIZE = settings["fps"] * (1 + settings["videoDelaySeconds"] + settings["loopedVideoLength"])
FULLSCREEN = settings["fullscreen"]
FPS_OVERLAY = settings["fpsOverlay"]
CAP_GRAPHICS_FPS = settings["capGraphicsFps"]