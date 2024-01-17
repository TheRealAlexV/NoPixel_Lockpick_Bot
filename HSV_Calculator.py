# coding: utf-8 # Set the encoding to utf-8

import cv2 # Import the OpenCV library for computer vision
import numpy as np # Import the NumPy library for numerical operations
import matplotlib.pyplot as plt # Import the Matplotlib library for plotting

def nothing(x): # Define a dummy function that does nothing
    pass

def hsv_calc(): # Define a function that calculates the HSV values for a given image
    cv2.namedWindow("Trackbars",) # Create a window named Trackbars
    cv2.createTrackbar("lh","Trackbars",0,179,nothing) # Create a trackbar for the lower hue value
    cv2.createTrackbar("ls","Trackbars",0,255,nothing) # Create a trackbar for the lower saturation value
    cv2.createTrackbar("lv","Trackbars",0,255,nothing) # Create a trackbar for the lower value value
    cv2.createTrackbar("uh","Trackbars",179,179,nothing) # Create a trackbar for the upper hue value
    cv2.createTrackbar("us","Trackbars",255,255,nothing) # Create a trackbar for the upper saturation value
    cv2.createTrackbar("uv","Trackbars",255,255,nothing) # Create a trackbar for the upper value value
    while True: 
        # Read lockpick template from a file. If using against a game that looks different; Take a screen shot and replace this image.
        frame = cv2.imread(r'screens\RPGen\lockpickminigame.png') 
        hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV) # Convert the image from BGR to HSV color space
        
        lh = cv2.getTrackbarPos("lh","Trackbars") # Get the lower hue value from the trackbar
        ls = cv2.getTrackbarPos("ls","Trackbars") # Get the lower saturation value from the trackbar
        lv = cv2.getTrackbarPos("lv","Trackbars") # Get the lower value value from the trackbar
        uh = cv2.getTrackbarPos("uh","Trackbars") # Get the upper hue value from the trackbar
        us = cv2.getTrackbarPos("us","Trackbars") # Get the upper saturation value from the trackbar
        uv = cv2.getTrackbarPos("uv","Trackbars") # Get the upper value value from the trackbar

        l_blue = np.array([lh,ls,lv]) # Create a numpy array for the lower blue color range
        u_blue = np.array([uh,us,uv]) # Create a numpy array for the upper blue color range
        mask = cv2.inRange(hsv, l_blue, u_blue) # Create a mask by thresholding the HSV image with the blue color range
        result = cv2.bitwise_or(frame,frame,mask=mask) # Apply the mask to the original image using bitwise or operation

        cv2.imshow("mask",mask) # Show the mask in a window
        cv2.imshow("result",result) # Show the result in a window
        key = cv2.waitKey(1) # Wait for a key press for 1 millisecond
        if key == 27: # If the key is the escape key
            break # Break the loop
    cap.release() # Release the capture object
    cv2.destroyAllWindows() # Destroy all the windows

hsv_calc()