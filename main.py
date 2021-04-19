import cv2 as cv
import matplotlib as plt
import numpy as np

VIDEO_SOURCE = "/dev/video1"
FULLSCREEN = False
WINDOW_NAME = "Pi Sentry Gun"
WIDTH, HEIGHT = 1920, 1080


# capture the camera input
print("starting capture... ", end='')
cap = cv.VideoCapture(VIDEO_SOURCE)
# set the name of the window
cv.namedWindow(WINDOW_NAME)
# set the window to fullscreen if needed
if FULLSCREEN:
    cv.setWindowProperty(WINDOW_NAME, cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)
print("done!")

# this will run if we can't open the camera
if not cap.isOpened():
    print("Cannot open camera.")
    exit(1)

while True:
    # capture a frame
    ret, frame = cap.read()

    # if frame is read correctly, ret is True.
    if not ret:
        print("Can't receive frame (stream end?). Exiting...")
        exit(0)

    # resize image so that it fits the fullscreen window
    # we don't need to do this if we aren't fullscreen
    if FULLSCREEN:
        frame = cv.resize(frame, dsize=(WIDTH, HEIGHT), interpolation=cv.INTER_LINEAR)

    # show the image on the window
    cv.imshow(WINDOW_NAME, frame)

    if cv.waitKey(1) == ord('q'):
        break

# when done, release capture
cap.release()
cv.destroyAllWindows()
