# Instant Replay
Delayed webcam playback with options to record and loop clips. Intended use is for live sports analysis.

## Requirements
* 2gb of ram
* multi-core processor preferred
* python 3.7 (64-bit) with numpy, opencv-python (cv2), and keyboard

## Settings
The following settings are imported from `settings.json`:  
**cameraIndex:** index of the camera device to use  
**fps:** framerate of the whole program  
**videoDelaySeconds:** how many seconds to delay the camera playback  
**loopedVideoLength:** number of seconds before the currently displayed frame to save. So if videoDelaySeconds is 10 and loopedVideoLength is also 10, saved videos will be from T-20 to T-20 seconds.  
**cameraRotations:** number of 90 degree rotations of the camera necessary for it to be upright  
**fullscreen:** start the program in fullscreen  

## Controls
**SPACE** - save and loop the last few seconds (depending on settings)  
**Q** - quit

## Note
This is still an early prototype for this program. The core functionality is there, but it's not very efficient and the interface is still fairly primitive.
