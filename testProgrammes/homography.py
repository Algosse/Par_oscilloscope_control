"""
    Exemple code to do homography in python
    Usefull to redress pictures of the printer's plate and then calculate position on it
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

cv2.imshow("out",im_out[::-1,:])
cv2.waitKey(0)