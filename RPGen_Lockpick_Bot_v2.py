# Import libraries for math, computer vision, button pressing, screen grabbing, and windows resolution
import numpy as np  # Math
import cv2  # Computer vision
import pyautogui  # Button pressing
import mss  # Screen grabbing
import ctypes  # Windows Get Resolution
import logging

# Define constants for different states of the program
RESET = 0  # The state when the program is waiting for the target bar to appear
FOUND = 1  # The state when the program has found the target bar and is tracking its area
INTERCEPTION = 2  # The state when the program has detected the target bar is shrinking and needs to press the correct key

# Initialize variables for the state, the starting area of the target bar, the number to press, the screen width, and the previous area of the target bar
state = RESET
starting_area = 0
number = 0
screen_width = ctypes.windll.user32.GetSystemMetrics(0)
prev_area = 0
pyautogui.FAILSAFE = False

preview = True  # If true, a window will show where the current zone is
template_path_prefix = 'templates/RPGen/'  # The path prefix for the number templates
# Set crop zones for the desktop version
zone = {"top": 657, "left": 1218, "width": 125, "height": 125}  # The zone around the bar
number_zone = {"top": 53, "left": 52, "width": 21, "height": 21}  # The zone around the number
# Set colour ranges for the bar for the desktop version
blue_bar_lower = np.array([103, 174, 162], dtype="uint8")
blue_bar_upper = np.array([107, 232, 209], dtype="uint8")
# Preload the number templates as grayscale images
templates = []
for i, template_path in enumerate(['1.png', '2.png', '3.png']):
    templates.append(cv2.imread(f'{template_path_prefix}{template_path}', 0))

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Main loop
while True:
    # Get a screenshot of the zone and convert it to HSV color space
    with mss.mss() as sct:
        frame = cv2.cvtColor(np.array(sct.grab(zone)), cv2.COLOR_BGR2HSV)
    if preview:
        cv2.imshow('frame', frame)  # Show the frame in a window
        cv2.waitKey(1)  # Wait for a key press

    # Get the area of the target bar by applying a color mask and counting the white pixels
    mask = cv2.inRange(frame, blue_bar_lower, blue_bar_upper)
    area = np.sum(mask == 255)

    # Update the state based on the area of the target bar
    if state == FOUND and area / starting_area <= 0.9:  # If the target bar is shrinking
        logging.debug("Target bar is shrinking. Changing state to INTERCEPTION.")
        state = INTERCEPTION  # Change the state to interception
    elif state == RESET and area > 0:  # If the target bar has appeared
        logging.debug("Target bar has appeared. Changing state to FOUND.")
        state = FOUND  # Change the state to found
        starting_area = area  # Set the starting area to the current area
    elif area == 0 and (state == FOUND or state == INTERCEPTION):  # If the target bar has disappeared
        logging.debug("Target bar has disappeared. Changing state to RESET.")
        state = RESET  # Change the state to reset
        starting_area = 0  # Reset the starting area

    # Find the number to press by cropping the number zone and matching it with the templates
    if number == 0 or area != prev_area:  # If the number is not set or the area has changed
        number_crop = frame[number_zone["top"]:number_zone["top"] + number_zone["height"],
                      number_zone["left"]:number_zone["left"] + number_zone["width"]]  # Crop the number zone from the frame
        number_crop = cv2.cvtColor(number_crop, cv2.COLOR_HSV2BGR)  # Convert the number crop to BGR color space
        img_gray = cv2.cvtColor(number_crop, cv2.COLOR_BGR2GRAY)  # Convert the number crop to grayscale
        for i, template in enumerate(templates):  # Loop through the templates
            res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)  # Apply template matching
            threshold = 0.8  # Set the similarity threshold
            loc = np.where(res >= threshold)  # Find the locations where the similarity is above the threshold
            found = len(loc[0])  # Count the number of matches
            if found > 0:  # If there is a match
                number = i + 1  # Set the number to the template index plus one
                logging.debug(f"Template {i + 1} found.")
        prev_area = area  # Update the previous area

    # Reassign numbers to letters
    if number == 1:  # If the number is 1
        key = "q"  # Set the key to q
    elif number == 2:  # If the number is 2
        key = "w"  # Set the key to w
    elif number == 3:  # If the number is 3
        key = "e"  # Set the key to e
    else:  # If the number is not valid
        key = "0"  # Set the key to 0

    # Press the key when in the right zone
    if state == INTERCEPTION and number != 0:  # If the state is interception and the number is valid
        logging.debug(f"Pressing key {key}. Changing state to RESET.")
        pyautogui.press(f'{key}')  # Press the key
        state = RESET  # Change the state to reset
        number = 0  # Reset the number
        key = "0"  # Reset the key
