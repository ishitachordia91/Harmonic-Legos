#python color_tracking.py --video balls.mp4
#python color_tracking.py

# import the necessary packages
from collections import deque
import numpy as np
import argparse
import imutils
import cv2
import serial
import pdb
import time

class ShapeDetector:
    def __init__(self):
		pass
 
    def detect(self, img):
        # initialize the shape name and approximate the contour
        num_rectangles = 0
        rectangle_colors = []
        points = []
        original_img = img.copy()
        #pdb.set_trace()
        # first change the color to grayscale to work with one channel and blur it
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray,(5,5),0)
        #cv2.imshow("foreground", gray)

        #find the edges
        edges = cv2.Canny(gray, 10, 50, apertureSize=5)
        pdb.set_trace()
        #bin = cv2.dilate(bin, None) makes the edges thicker

        #find the counters
        _, contours, _ = cv2.findContours(gray, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            cnt_len = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * cnt_len, True)
            if len(approx) == 4:
                num_rectangles += 1
                center_x, center_y = self.centroidnp(approx[:, 0])
                # Original image is BGR color space
                r = original_img[center_y, center_x, 2]
                g = original_img[center_y, center_x, 1]
                b = original_img[center_y, center_x, 0]
                cv2.circle(gray,(center_y,center_x),8,(r,g,b),-1)
                rectangle_colors.append((r,g,b))
                points.append(approx)
        #cv2.imshow("gray", gray)
        print "color is", rectangle_colors
        return num_rectangles, rectangle_colors, points

    def find_squares(self, img):
        img = cv2.GaussianBlur(img, (5, 5), 0)
        num_rectangles = 0
        rectangle_colors = []
        points = []
        original_img = img.copy()
        draw_img = img.copy()
        for gray in cv2.split(img):
            for thrs in xrange(0, 255, 26):
                if thrs == 0:
                    bin = cv2.Canny(gray, 0, 50, apertureSize=5)
                    bin = cv2.dilate(bin, None)
                else:
                    _retval, bin = cv2.threshold(gray, thrs, 255, cv2.THRESH_BINARY)
                bin, contours, _hierarchy = cv2.findContours(bin, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
                for cnt in contours:
                    cnt_len = cv2.arcLength(cnt, True)
                    cnt = cv2.approxPolyDP(cnt, 0.02*cnt_len, True)
                    if len(cnt) == 4 and cv2.contourArea(cnt) > 1800 and cv2.isContourConvex(cnt):
                        points.append(cnt)
                        num_rectangles += 1
                        center_x, center_y = self.centroidnp(cnt[:, 0])
                        # Original image is BGR color space
                        r = int(original_img[center_y, center_x, 0])
                        g = int(original_img[center_y, center_x, 1])
                        b = int(original_img[center_y, center_x, 2])
                        cv2.circle(draw_img,(center_x,center_y),8,(0,0,0),-1)
                        rectangle_colors.append((r,g,b))
        #pdb.set_trace()
        #cv2.imshow("gray", draw_img)
        return num_rectangles, rectangle_colors, points

    def detectColor(self, img):

        num_rectangles = 0
        rectangle_colors = []
        points = []
        original_img = img.copy()
        draw_img = img.copy()
        
        # define the lower and upper boundaries of the colors in the HSV color space
        lower = {'red':(140, 44, 100), 'green':(40, 82, 89), 'blue':(70, 80, 90), 'yellow':(2, 19, 89)} #assign new item lower['blue'] = (93, 10, 0)
        upper = {'red':(190,250,250), 'green':(100,255,255), 'blue':(140,255,255), 'yellow':(70,255,255)}
        test = {'red':(186,255,255)}
        # define standard colors for circle around the object
        colors = {'red':(0,0,255), 'green':(0,255,0), 'blue':(255,0,0), 'yellow':(0, 255, 217)}
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        #for key, value in test:
        for key, value in upper.items():
            # construct a mask for the color from dictionary`1, then perform
            # a series of dilations and erosions to remove any small
            # blobs left in the mask
            kernel = np.ones((9,9),np.uint8)
            mask = cv2.inRange(hsv, lower[key], upper[key])
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            #cv2.imshow("mask", mask)
            
            # find contours in the mask and initialize the current
            # (x, y) center of the ball
            _, contours, _ = cv2.findContours(mask.copy(), cv2.RETR_LIST,
                cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                num_rectangles += 1
                center_x, center_y = self.centroidnp(cnt[:, 0])
                # Original image is BGR color space
                r = int(original_img[center_y, center_x, 0])
                g = int(original_img[center_y, center_x, 1])
                b = int(original_img[center_y, center_x, 2])
                cv2.circle(draw_img,(center_x, center_y),8,(255,255,255),-1)
                rectangle_colors.append((r,g,b))
                points.append(cnt)

        cv2.imshow("gray", draw_img)
        print "num_rectangles", num_rectangles, "bu colors", len(rectangle_colors), "num pts", len(points)
        return num_rectangles, rectangle_colors, points
                    

    def centroidnp(self, arr):
        length = arr.shape[0]
        sum_x = np.sum(arr[:, 0])
        sum_y = np.sum(arr[:, 1])
        return sum_x/length, sum_y/length
                    
def denoise(frame):
    frame = imutils.resize(frame, width=600)
    frame = cv2.GaussianBlur(frame, (5, 5), 0)
    return frame
    


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
    help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
    help="max buffer size")
args = vars(ap.parse_args())
 

# define the final array of notes in order
rgb_sequence = []


# if a video path was not supplied, grab the reference
# to the webcam
if not args.get("video", False):
    camera = cv2.VideoCapture(0)
    
# otherwise, grab a reference to the video file
else:
    camera = cv2.VideoCapture(args["video"])

#camera.__setattr__(cv2.CV_CAP_PROP_FPS, 60)#
camera.set(cv2.CAP_PROP_FPS, 2)
#get first frame, which serves as our background
(grabbed, bg) = camera.read()
if(grabbed):
    shapeDetector = ShapeDetector()
    #num_rectangles = 2
    #rectangle_colors = []
    #rectangle_points = []
    #sq = shapeDetector.find_squares(denoise(bg))
    num_rectangles, rectangle_colors, rectangle_points = shapeDetector.detectColor(denoise(bg))

while(True):
    # Get the current frame
    (grabbed, frame) = camera.read()

    # If we did not grab a frame,then we have reached the end of the video
    if not grabbed:
        break

    # Find the rectangles in the current frame
    curr_num_rectangles, curr_rectangle_colors, curr_rectangle_points = shapeDetector.detectColor(denoise(frame))
    newColor = None

    # Added a block
    if(num_rectangles < curr_num_rectangles):
        for idx, point in enumerate(curr_rectangle_points):
            #pdb.set_trace()
            addedBlock = True
            for curr_point in rectangle_points:
                if np.all(point == curr_point):
                    addedBlock = False
            if(addedBlock):
                newColor = curr_rectangle_colors[idx]
                rgb_sequence.append(newColor)

    # Removed a block
    elif (num_rectangles > curr_num_rectangles):
        for idx, point in enumerate(rectangle_points):
            #pdb.set_trace()
            removedBlock = True
            for curr_point in curr_rectangle_points:
                if np.all(point == curr_point):
                    removedBlock = False
            if(removedBlock):
                #Remove the most recent occurence
                currColor = rectangle_colors[idx]
                #pdb.set_trace()
                if (currColor in rgb_sequence):
                    rgb_sequence.reverse()
                    rgb_sequence.remove(currColor)
                    rgb_sequence.reverse()
     
    rectangle_points = curr_rectangle_points
    num_rectangles = curr_num_rectangles
    rectangle_colors = curr_rectangle_colors
    #serial.write(newColor)
    time.sleep(0.1)
    
    key = cv2.waitKey(1) & 0xFF
    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break
 
# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
