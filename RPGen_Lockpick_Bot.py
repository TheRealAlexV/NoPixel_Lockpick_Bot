import numpy as np
import cv2
import pyautogui
import mss
import ctypes
import logging
import datetime  # Import the datetime module for timestamps

# Define constants for different states of the program
RESET = 0
FOUND = 1
INTERCEPTION = 2

# Initialize variables for the state, the starting area of the target bar, the number to press, the screen width, and the previous area of the target bar
state = RESET
starting_area = 0
number = 0
screen_width = ctypes.windll.user32.GetSystemMetrics(0)
prev_area = 0
pyautogui.FAILSAFE = False
preview = True
template_path_prefix = 'templates/RPGen/'

# Set crop zones for the desktop version
zone = {"top": 657, "left": 1218, "width": 125, "height": 125}
number_zone = {"top": 53, "left": 52, "width": 21, "height": 21}

# Set colour ranges for the bar for the desktop version
blue_bar_lower = np.array([103, 174, 162], dtype="uint8")
blue_bar_upper = np.array([107, 232, 209], dtype="uint8")

# Preload the number templates as grayscale images
templates = []
for i, template_path in enumerate(['1.png', '2.png', '3.png']):
    templates.append(cv2.imread(f'{template_path_prefix}{template_path}', 0))

# Set up logging with timestamps
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Main loop
while True:
    # Get a screenshot of the zone and convert it to HSV color space
    with mss.mss() as sct:
        frame = cv2.cvtColor(np.array(sct.grab(zone)), cv2.COLOR_BGR2HSV)
    if preview:
        cv2.imshow('frame', frame)
        cv2.waitKey(1)

    # Get the area of the target bar by applying a color mask and counting the white pixels
    mask = cv2.inRange(frame, blue_bar_lower, blue_bar_upper)
    area = np.sum(mask == 255)

    # Find the number to press by cropping the number zone and matching it with the templates
    if number == 0 or area != prev_area:
        number_crop = frame[number_zone["top"]:number_zone["top"] + number_zone["height"],
                      number_zone["left"]:number_zone["left"] + number_zone["width"]]
        number_crop = cv2.cvtColor(number_crop, cv2.COLOR_HSV2BGR)
        img_gray = cv2.cvtColor(number_crop, cv2.COLOR_BGR2GRAY)
        for i, template in enumerate(templates):
            res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
            threshold = 0.8
            loc = np.where(res >= threshold)
            found = len(loc[0])
            if found > 0:
                number = i + 1
                logging.debug(f"Template {i + 1} found.")
        prev_area = area

    # Update the state based on the area of the target bar
    if state == FOUND and area / starting_area <= 0.9:
        logging.debug("Target bar is shrinking. Changing state to INTERCEPTION.")
        state = INTERCEPTION
    elif state == RESET and area > 0:
        logging.debug(f" ")
        logging.debug("Target bar has appeared. Changing state to FOUND.")
        state = FOUND
        starting_area = area
    elif area == 0 and (state == FOUND or state == INTERCEPTION):
        logging.debug("Target bar has disappeared. Changing state to RESET.")
        state = RESET
        starting_area = 0

    # Press the key when in the right zone
    if state == INTERCEPTION and number != 0:
        # Reassign numbers to letters
        if number == 1:
            key = "q"
        elif number == 2:
            key = "w"
        elif number == 3:
            key = "e"
        else:
            key = "0"
        logging.debug(f"Pressing key {key}. Changing state to RESET.")
        logging.debug(f" ")
        pyautogui.press(f'{key}')
        state = RESET
        number = 0
        key = "0"
