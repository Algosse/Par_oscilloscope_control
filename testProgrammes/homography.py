"""
    Exemple code to do homography in python
    Usefull to redress pictures of the printer's plate and then calculate position on it
"""
"""

import cv2
import numpy as np

# Import the book
im_src = cv2.imread('homography_test.jpg').copy()
print(im_src.shape)
# Corners of the book
pts_src = np.array([[46,305],[202,428],[342,238],[204,164]]) # In order BL, BR, TR, TL, coords from x -> left, y -> bot
    
cv2.imshow('in',im_src)
pts_dst = np.array([[0,0],[599,0],[599,799],[0,799]]) # coord from a classic landmark

h,status = cv2.findHomography(pts_src, pts_dst)

im_out = cv2.warpPerspective(im_src, h, (600,800))

cv2.imshow("out",im_out[::,:])
cv2.waitKey(0)"""

import cv2
import numpy as np

def mouseHandler(event,x,y,flags,param):
    global im_temp, pts_src

    if event == cv2.EVENT_LBUTTONDOWN:
        cv2.circle(im_temp,(x,y),3,(0,255,255),5,cv2.LINE_AA)
        cv2.imshow("Image", im_temp)
        if len(pts_src) < 4:
        	pts_src = np.append(pts_src,[(x,y)],axis=0)


# Read in the image.
im_src = cv2.imread("trapeze.png")

# Destination image
height, width = 400, 300
im_dst = np.zeros((height,width,3),dtype=np.uint8)


# Create a list of points.
pts_dst = np.empty((0,2))
pts_dst = np.append(pts_dst, [(0,0)], axis=0)
pts_dst = np.append(pts_dst, [(width-1,0)], axis=0)
pts_dst = np.append(pts_dst, [(width-1,height-1)], axis=0)
pts_dst = np.append(pts_dst, [(0,height-1)], axis=0)

# Create a window
cv2.namedWindow("Image", 1)

im_temp = im_src
pts_src = np.empty((0,2))

cv2.setMouseCallback("Image",mouseHandler)


cv2.imshow("Image", im_temp)
cv2.waitKey(0)
print(pts_src)

tform, status = cv2.findHomography(pts_src, pts_dst)
im_dst = cv2.warpPerspective(im_src, tform,(width,height))

cv2.imshow("Image", im_dst)
cv2.waitKey(0)