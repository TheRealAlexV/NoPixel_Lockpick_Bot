# Import necessary libraries
import numpy as np  # Import NumPy library for numerical operations
import cv2  # Import OpenCV library for computer vision
import pyautogui  # Import PyAutoGUI library for automation
import mss  # Import MSS library for screen capturing
import ctypes  # Import ctypes for system metrics
import logging  # Import logging for event tracking
import datetime  # Import datetime for timestamping
import tkinter as tk  # Import Tkinter library for GUI
from tkinter.scrolledtext import ScrolledText  # Import ScrolledText widget for logging

# Define constants for different states of the program
RESET = 0  # Constant representing the RESET state
FOUND = 1  # Constant representing the FOUND state
INTERCEPTION = 2  # Constant representing the INTERCEPTION state

# Initialize variables for the state, the starting area of the target bar, the number to press,
# the screen width, and the previous area of the target bar
state = RESET  # Initialize state to RESET
starting_area = 0  # Initialize starting_area to 0
number = 0  # Initialize number to 0
screen_width = ctypes.windll.user32.GetSystemMetrics(0)  # Get the screen width
prev_area = 0  # Initialize prev_area to 0
pyautogui.FAILSAFE = False  # Disable failsafe to prevent unintentional termination
preview = True  # Enable frame preview
template_path_prefix = 'templates/RPGen/'  # Set the path prefix for number templates

# Set crop zones for the desktop version
zone = {"top": 657, "left": 1218, "width": 125, "height": 125}  # Set the zone for capturing the target bar
number_zone = {"top": 53, "left": 52, "width": 21, "height": 21}  # Set the zone for capturing the number

# Set colour ranges for the target bar for the desktop version
blue_bar_lower = np.array([103, 174, 162], dtype="uint8")  # Set lower bound of the blue color range
blue_bar_upper = np.array([107, 232, 209], dtype="uint8")  # Set upper bound of the blue color range

# Preload the number templates as grayscale images
templates = []  # Initialize an empty list to store number templates
for i, template_path in enumerate(['1.png', '2.png', '3.png']):  # Iterate over template paths
    templates.append(cv2.imread(f'{template_path_prefix}{template_path}', 0))  # Read and append grayscale templates

# Set up logging with timestamps
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')  # Configure logging

# Create a Tkinter window for logging
root = tk.Tk()  # Create a Tkinter root window
root.title("Log Window")  # Set the title of the window
root.attributes("-topmost", True)  # Keep the window always on top

# Create a scrolled text widget for logging
log_text = ScrolledText(root, state="disabled", wrap=tk.WORD)  # Create a scrolled text widget
log_text.pack(expand=True, fill="both")  # Pack the widget to expand and fill available space

# Function to append logs to the text widget
def append_log(message):
    log_text.configure(state="normal")  # Enable the text widget
    log_text.insert(tk.END, message + "\n")  # Insert the message into the text widget
    log_text.configure(state="disabled")  # Disable the text widget
    log_text.yview(tk.END)  # Auto-scroll to the bottom

# Main loop
while True:
    # Get a screenshot of the zone and convert it to HSV color space
    with mss.mss() as sct:  # Use MSS to capture the screen
        frame = cv2.cvtColor(np.array(sct.grab(zone)), cv2.COLOR_BGR2HSV)  # Convert the captured frame to HSV color space
    if preview:
        cv2.imshow('frame', frame)  # Display the frame
        cv2.waitKey(1)  # Wait for a key press (preview functionality)

    # Get the area of the target bar by applying a color mask and counting the white pixels
    mask = cv2.inRange(frame, blue_bar_lower, blue_bar_upper)  # Create a color mask
    area = np.sum(mask == 255)  # Count white pixels in the mask to determine the area of the target bar

    # Find the number to press by cropping the number zone and matching it with the templates
    if number == 0 or area != prev_area:
        number_crop = frame[number_zone["top"]:number_zone["top"] + number_zone["height"],
                      number_zone["left"]:number_zone["left"] + number_zone["width"]]  # Crop the frame to the number zone
        number_crop = cv2.cvtColor(number_crop, cv2.COLOR_HSV2BGR)  # Convert cropped frame to BGR color space
        img_gray = cv2.cvtColor(number_crop, cv2.COLOR_BGR2GRAY)  # Convert cropped frame to grayscale
        for i, template in enumerate(templates):  # Iterate over number templates
            res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)  # Match the template with the cropped frame
            threshold = 0.8  # Set a matching threshold
            loc = np.where(res >= threshold)  # Find locations where the template matches
            found = len(loc[0])  # Get the number of matches
            if found > 0:  # If matches are found
                number = i + 1  # Set the detected number
                log_message = f"Template {i + 1} found."  # Log the template found
                logging.debug(log_message)  # Log the message to the console
                append_log(log_message)  # Log the message to the Tkinter window
        prev_area = area  # Update the previous area

    # Update the state based on the area of the target bar
    if state == FOUND and area / starting_area <= 0.9:
        log_message = "Target bar is shrinking. Changing state to INTERCEPTION."  # Log state change
        logging.debug(log_message)  # Log the message to the console
        append_log(log_message)  # Log the message to the Tkinter window
        state = INTERCEPTION  # Update state
    elif state == RESET and area > 0:
        log_message = "Target bar has appeared. Changing state to FOUND."  # Log state change
        logging.debug(log_message)  # Log the message to the console
        append_log(log_message)  # Log the message to the Tkinter window
        state = FOUND  # Update state
        starting_area = area  # Update starting area
    elif area == 0 and (state == FOUND or state == INTERCEPTION):
        log_message = "Target bar has disappeared. Changing state to RESET.\n"  # Log state change
        logging.debug(log_message)  # Log the message to the console
        append_log(log_message)  # Log the message to the Tkinter window
        state = RESET  # Update state
        starting_area = 0  # Reset starting area

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
        log_message = f"Pressing key {key}. Changing state to RESET.\n"  # Log key press
        logging.debug(log_message)  # Log the message to the console
        append_log(log_message)  # Log the message to the Tkinter window
        pyautogui.press(f'{key}')  # Simulate key press
        state = RESET  # Update state
        number = 0  # Reset number
        key = "0"  # Reset key

    # Update the Tkinter window
    root.update_idletasks()  # Update Tkinter window idle tasks
    root.update()  # Update Tkinter window
