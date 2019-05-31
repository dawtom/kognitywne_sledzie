#!/usr/bin/env python3

from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
                help="Path to the (optional) input video file.")
ap.add_argument("-b", "--buffer", type=int, default=64,
                help="Max buffer size for ball position history.")
args = vars(ap.parse_args())

# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
colorMin = (120, 90, 20)
colorMax = (145, 105, 255)
pts = deque(maxlen=args["buffer"])
frame = None
processed = None


def set_ball_color(event, x, y, flags, param):
    try:
        global colorMin, colorMax
        if event == cv2.EVENT_LBUTTONUP:
            if processed is not None:
                print(x, y, event, flags)
                pixel = processed[x, y]
                print('Picked color:', pixel, '(HSV)')
                colorMin = np.clip(pixel * [0.925, 0.7, 0.25], 0, 255)
                colorMax = np.clip(pixel * [1.075, 1.3, 1.75], 0, 255)
                pts.clear()
    except IndexError:
        print('Failed to change color due index errors')


cv2.namedWindow('Image')
cv2.setMouseCallback('Image', set_ball_color)

if not args.get("video", False):
    # if a video path was not supplied, grab the reference
    # to the webcam
    vs = VideoStream(src=0).start()
else:
    # otherwise, grab a reference to the video file
    vs = cv2.VideoCapture(args["video"])


def read_frame():
    # grab the current frame
    frame = vs.read()

    # handle the frame from VideoCapture or VideoStream
    return frame[1] if args.get("video", False) else frame


# allow the camera or video file to warm up
time.sleep(2.0)

try:
    while True:
        # grab the current frame
        frame = read_frame()

        # if we are viewing a video and we did not grab a frame,
        # then we have reached the end of the video
        if frame is None:
            break

        # resize the frame, blur it, and convert it to the HSV
        # color space
        frame = imutils.resize(frame, width=600)
        frame = cv2.flip(frame, 1)
        processed = cv2.GaussianBlur(frame, (11, 11), 0)
        processed = cv2.cvtColor(processed, cv2.COLOR_BGR2HSV)

        # construct a mask for the color "green", then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask
        mask = cv2.inRange(processed, colorMin, colorMax)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        # find contours in the mask and initialize the current
        # (x, y) center of the ball
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        center = None

        # only proceed if at least one contour was found
        if len(cnts) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
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
        cv2.imshow("Image", frame)
        # cv2.imshow("Processed", processed)
        cv2.imshow("Mask", mask)
        key = cv2.waitKey(1) & 0xFF

        # if the 'q' key is pressed, stop the loop
        if key == ord("q"):
            break
finally:
    if not args.get("video", False):
        # if we are not using a video file, stop the camera video stream
        vs.stop()
    else:
        # otherwise, release the camera
        vs.release()

    # close all windows
    cv2.destroyAllWindows()
