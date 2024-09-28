"""
HotwireBot: A Python script that uses computer vision to automate the hotwire/Lockpick circle minigame in QBCore servers.
This script detects the game state and automatically performs the required actions, making the hotwiring process more efficient and consistent.
"""

import numpy as np
import cv2
import pyautogui
import mss
import ctypes
import time

# Constants
RESET = 0
FOUND = 1

# Variables
state = RESET
starting_area = 0
pyautogui.FAILSAFE = False
preview = True
template_path_prefix = 'templates/'
zone = {"top": 647, "left": 1207, "width": 145, "height": 145}
number_zone = {"top": 58, "left": 58, "width": 30, "height": 30}
blue_bar_lower = np.array([104, 222, 194], dtype="uint8")
blue_bar_upper = np.array([104, 222, 194], dtype="uint8")
template = cv2.imread(f'{template_path_prefix}e.png', 0)

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

    if state == RESET and area > 0:
        log_text.append("Target bar has appeared. Changing state to FOUND.")
        state = FOUND
        starting_area = area
    elif state == FOUND and area < starting_area:
        log_text.append("Target bar is shrinking. Pressing key 'e'.")
        pyautogui.press('e')
        log_text.append("Changing state to RESET.")
        state = RESET
        starting_area = 0
        time.sleep(0.1)  # Add a small delay to avoid rapid key presses

    # Reset if area becomes 0
    if area == 0 and state != RESET:
        log_text.append("No bar detected. Resetting state.")
        state = RESET
        starting_area = 0

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