import numpy as np
import cv2
import pyautogui
import mss
import ctypes

# Constants
RESET = 0
FOUND = 1
INTERCEPTION = 2

# Variables
state = RESET
starting_area = 0
number = 0
screen_width = ctypes.windll.user32.GetSystemMetrics(0)
prev_area = 0
pyautogui.FAILSAFE = False
preview = True
template_path_prefix = 'templates/RPGen/'
zone = {"top": 657, "left": 1218, "width": 125, "height": 125}
number_zone = {"top": 53, "left": 52, "width": 21, "height": 21}
blue_bar_lower = np.array([103, 190, 140], dtype="uint8")
blue_bar_upper = np.array([110, 234, 204], dtype="uint8")
templates = [cv2.imread(f'{template_path_prefix}{template_path}', 0) for template_path in ['1.png', '2.png', '3.png']]

# Create a window for logging
cv2.namedWindow('Logging', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Logging', 700, 400)
cv2.moveWindow('Logging', 0, 0)
cv2.setWindowProperty('Logging', cv2.WND_PROP_TOPMOST, 1)  # Set the window to be always on top

# Log history
log_history = []

# Font settings
font_size = 0.7
font_thickness = 1

# Line spacing
line_spacing = 20  # Adjust as needed

# Main loop
while True:
    with mss.mss() as sct:
        frame = cv2.cvtColor(np.array(sct.grab(zone)), cv2.COLOR_BGR2HSV)

    if preview:
        cv2.imshow('frame', frame)
        cv2.waitKey(1)

    mask = cv2.inRange(frame, blue_bar_lower, blue_bar_upper)
    area = np.sum(mask == 255)

    # Log to the window
    log_text = []

    if number == 0 or area != prev_area:
        number_crop = frame[number_zone["top"]:number_zone["top"] + number_zone["height"],
                      number_zone["left"]:number_zone["left"] + number_zone["width"]]
        number_crop = cv2.cvtColor(number_crop, cv2.COLOR_HSV2BGR)
        img_gray = cv2.cvtColor(number_crop, cv2.COLOR_BGR2GRAY)

        template_matched = False

        for i, template in enumerate(templates):
            if not template_matched:
                res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
                threshold = 0.8
                loc = np.where(res >= threshold)
                found = len(loc[0])

                if found > 0:
                    number = i + 1
                    # log_text.append(f"Template {i + 1} found.")
                    template_matched = True

        prev_area = area

    if state == RESET and area > 0:
        log_text.append("Target bar has appeared. Changing state to FOUND.")
        state = FOUND
        starting_area = area
    elif state == FOUND and area < starting_area:  # Check if the area is less than the starting area
        log_text.append("Target bar is shrinking. Changing state to INTERCEPTION.")
        state = INTERCEPTION
    elif state == INTERCEPTION and number != 0:
        key_mapping = {1: "q", 2: "w", 3: "e"}
        key = key_mapping.get(number, "0")
        log_text.append(f"Pressing key {key}. Changing state to RESET.")
        pyautogui.press(key)
        log_text.append(f"")
        state = RESET
        number = 0

    # Update log history
    log_history = log_text + log_history
    log_history = log_history[:10]  # Limit log history to the last 10 entries

    # Display the logging information
    log_display = np.zeros((400, 700, 3), dtype=np.uint8)
    y_pos = 20  # Initial position

    for log_line in log_history:
        cv2.putText(log_display, log_line, (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, font_size, (255, 255, 255), font_thickness)
        y_pos += line_spacing

    cv2.imshow('Logging', log_display)
    cv2.waitKey(1)