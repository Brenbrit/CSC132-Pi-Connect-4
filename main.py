import cv2 as cv
import matplotlib as plt
import matplotlib.pyplot as pyplot
import numpy as np

VIDEO_SOURCE = "/dev/video1"
WINDOW_NAME = "CV Test"

ASSETS_DIR = "assets/"
LEFT_ARROW = ASSETS_DIR + "left-arrow.png"
RIGHT_ARROW = ASSETS_DIR + "right-arrow.png"
UP_ARROW = ASSETS_DIR + "up-arrow.png"
DOWN_ARROW = ASSETS_DIR + "down-arrow.png"

# function to capture mouse buttons
def capture_event(event, x, y, flags, params):

    # event is mouse click
    # x, y are location of left mouse click
    if event == cv.EVENT_LBUTTONDBLCLK:
        print("Mouse down at ({},{})".format(x, y))

# function to overlay images of different sizes
# useful for buttons on the display
# This code is mostly taken from Christian Garcia's
# answer on StackOverflow, huge thanks to him!
# https://stackoverflow.com/a/54058766
def overlay_image(background, overlay, x, y):

    # get data about background image
    background_width = background.shape[1]
    background_height = background.shape[0]

    # if the foreground image is to be placed out of bounds,
    # we don't need to do any more processing - just return
    # the background.
    if x >= background_width or y >= background_height:
        return background

    # get some data about the foreground pic
    w = overlay.shape[1]
    h = overlay.shape[0]

    # if the overlay image will be outside the bounds of the background,
    # then cut off the bottom.
    if x + w > background_width:
        w = background_width - x
        overlay = overlay[:, :w]

    # if the right side of the overlay image will be out of bounds,
    # cut it off. This is just like above.
    if h + y > background_height:
        h = background_height - y
        overlay = overlay[:h]

    if overlay.shape[2] < 4:
        overlay = np.concatenate(
                [
                    overlay,
                    np.ones((overlay.shape[0], overlay.shape[1], 1), dtype = overlay.dtype) * 255
                ],
                axis = 2
                )

        overlay_image = overlay[..., :3]
        mask = overlay[..., 3:] / 255.0

        background[y:y+h, x:x+w] = (1.0 - mask) * background[y:y+h, x:x+w] + mask * overlay_image

        return background


print("starting capture... ", end='')
cap = cv.VideoCapture(VIDEO_SOURCE)
cv.namedWindow(WINDOW_NAME)
print("done!")

print("Loading buttons... ", end='')
left_button = cv.imread(LEFT_ARROW)
right_button = cv.imread(RIGHT_ARROW)
up_button = cv.imread(UP_ARROW)
down_button = cv.imread(DOWN_ARROW)
print("done!")

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

    # left button code
    frame = overlay_image(frame, left_button, 0, frame.shape[0] - 64)
    # up button
    frame = overlay_image(frame, up_button, 64, frame.shape[0] - 128)
    # down button
    frame = overlay_image(frame, down_button, 64, frame.shape[0] - 64)
    # right button
    frame = overlay_image(frame, right_button, 128, frame.shape[0] - 64)

    cv.imshow(WINDOW_NAME, frame)

    if cv.waitKey(1) == ord('q'):
        break

# when done, release capture
cap.release()
cv.destroyAllWindows()
