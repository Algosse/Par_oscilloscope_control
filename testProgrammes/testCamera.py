import numpy as np
import cv2
from PIL import Image

# Capture le flux vidéo

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if cap != None and cap.isOpened():

    while (True):

        if cap.grab():
            # Capture frame-by-frame
            ret, frame = cap.read()
            # Our operations on the frame come here
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Display the resulting frame
            cv2.imshow('frame', gray)
        else:
            print("Error: can't grab camera image")
            break
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

else:
    print('camera non connectée')

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
