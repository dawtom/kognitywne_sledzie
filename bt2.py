from collections import deque
from concurrent.futures import ThreadPoolExecutor
from imutils.video import VideoStream
from audiogen import ToneGenerator
import numpy as np
import argparse
import cv2
import imutils
import time
import ctypes

user32 = ctypes.windll.user32
screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
                help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
                help="max buffer size")
args = vars(ap.parse_args())

# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the list of tracked points
greenLower = (25, 100, 50)
greenUpper = (70, 200, 200)
pts = deque(maxlen=args["buffer"])
full_screen_frame_width = screensize[0]
full_screen_frame_height = screensize[1]
step = int(full_screen_frame_width / 20)

# if a video path was not supplied, grab the reference to the webcam
if not args.get("video", False):
    vs = VideoStream(src=0).start()

# otherwise, grab a reference to the video file
else:
    vs = cv2.VideoCapture(args["video"])

# allow the camera or video file to warm up
time.sleep(2.0)
tmp_time = time.time()
amplitude = 3  # Amplitude of the waveform
generator = ToneGenerator()
another_generator = ToneGenerator()
executor = ThreadPoolExecutor(max_workers=300)


def get_frequency_from_x(x_coordinate, y_coordinate):
    octaves_number = 1.583333
    xmin = 0.0
    xmax = full_screen_frame_width
    x_to_octaves = ((float(x_coordinate * octaves_number))/xmax)
    part_of_tone = 1.0
    n_tones_from_base = int((x_to_octaves * 12.0 * part_of_tone))/part_of_tone
    base = 392.00 #G
    q = 1.0594630944

    amplitude_ = (-0.004) * y_coordinate + 3.5
    # print("Y={}, amplitude={}".format(y_coordinate, amplitude_))
    # print(amplitude_)
    #return base * (q ** n_tones_from_base), amplitude_
    n_tones_from_base = int(x_coordinate / step)

    return base * (q ** n_tones_from_base), amplitude_


def play(frequency, amp):
    generator = ToneGenerator()
    print(frequency)
    print(amp)
    generator.play(frequency[0], 0.1, amp)

    while generator.is_playing():
        pass


while True:
    # grab the current frame
    frame = vs.read()

    # handle the frame from VideoCapture or VideoStream
    frame = frame[1] if args.get("video", False) else frame

    soundNames = ['g', 'g#', 'a', 'a#', 'h', 'c','c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#', 'a', 'a#', 'h', 'c','c#','d']
    step = int(full_screen_frame_width / 20)
    xPosition = int(0.30 * step)
    tmp = 0

    frame = imutils.resize(frame, width=full_screen_frame_width, height=full_screen_frame_height)

    while tmp < full_screen_frame_width:
        cv2.line(frame, (tmp, 0), (tmp, frame.shape[1]), (255, 0, 0))
        tmp += step

    for soundName in soundNames:
        cv2.putText(frame, soundName, (xPosition, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        xPosition += step

    # if we are viewing a video and we did not grab a frame,
    # then we have reached the end of the video
    if frame is None:
        break

    # blur the image, and convert it to the HSV color space
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # construct a mask for the color "green", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    # find contours in the mask and initialize the current
    # (x, y) center of the object
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None

    # only proceed if at least one contour was found
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        # only proceed if the radius meets a minimum size
        if radius > 10:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(frame, (int(x), int(y)), int(radius),
                       (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)

        frequency, amplitude_ = get_frequency_from_x(center[0], center[1])
        p = executor.submit(play, (frequency,), amplitude_)

    # update the points queue
    pts.appendleft(center)
    # loop over the set of tracked points
    for i in range(1, len(pts)):
        # if either of the tracked points are None, ignore
        # them
        if pts[i - 1] is None or pts[i] is None:
            continue

        # otherwise, compute the thickness of the line and
        # draw the connecting lines
        thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
        cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)

    # show the frame to our screen
    cv2.namedWindow('Piano Tiles', cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Piano Tiles", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow("Piano Tiles", frame)
    key = cv2.waitKey(1) & 0xFF

    # if the 'q' or 'escape' key is pressed, stop the loop
    if key == ord("q") or key == 27:
        break

# if we are not using a video file, stop the camera video stream
if not args.get("video", False):
    vs.stop()

# otherwise, release the camera
else:
    vs.release()

# close all windows
cv2.destroyAllWindows()
