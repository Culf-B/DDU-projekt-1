import cv2
import numpy as np
import pyautogui
import win32api, win32con

# Define the lower and upper bounds for green color in HSV space
lower_green = np.array([40, 40, 40])
upper_green = np.array([80, 255, 255])

# Initialize video capture from webcam
cap = cv2.VideoCapture(0)

# Set a lower resolution for faster processing
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)  # Width of the frame
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)  # Height of the frame

# Get the screen size
screen_width, screen_height = pyautogui.size()

# Define the region of interest (ROI) for tracking (x, y, width, height)
roi_x, roi_y = 320, 240  # Top-left corner (x, y) of the ROI
roi_w, roi_h = 320, 240  # Width and height of the ROI

# Variables to track the previous position of the object
prev_x, prev_y = None, None
max_speed = 200  # Maximum allowed speed
movement_threshold = 5  # Minimum movement threshold to move the cursor

# Get the initial mouse position
current_mouse_x, current_mouse_y = win32api.GetCursorPos()

while True:
    # Read a new frame from the video
    ret, frame = cap.read()
    
    if not ret:
        break

    # Flip the frame horizontally (mirror effect)
    frame = cv2.flip(frame, 1)

    # Get the frame dimensions
    frame_height, frame_width, _ = frame.shape

    # Draw the ROI rectangle on the original frame (optional, for visualization)
    cv2.rectangle(frame, (roi_x, roi_y), (roi_x + roi_w, roi_y + roi_h), (255, 255, 255), 2)

    # Extract the region of interest (ROI) from the frame
    roi = frame[roi_y:roi_y + roi_h, roi_x:roi_x + roi_w]

    # Convert the ROI from BGR to HSV color space
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    
    # Create a mask for green color in the ROI
    mask = cv2.inRange(hsv_roi, lower_green, upper_green)

    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # If any contours were found, find the largest one and track it
    if contours:
        # Find the largest contour by area
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)
        
        # Set a minimum contour area to filter out noise
        if area > 500:  # Adjust this threshold based on your use case
            # Get the bounding box for the largest contour in the ROI
            x, y, w, h = cv2.boundingRect(largest_contour)

            # Calculate the center of the bounding box in the ROI
            obj_center_x = x + w // 2
            obj_center_y = y + h // 2

            # Calculate the movement speed between frames
            if prev_x is not None and prev_y is not None:
                # Adjust obj_center_x and obj_center_y to frame coordinates
                adjusted_center_x = roi_x + obj_center_x
                adjusted_center_y = roi_y + obj_center_y
                
                speed = np.sqrt((adjusted_center_x - prev_x) ** 2 + (adjusted_center_y - prev_y) ** 2)

                # Only track the object if the speed is below the maximum threshold
                if speed < max_speed and speed > movement_threshold:  # Check if object moved enough
                    # Draw a rectangle around the largest green object (adjusted to frame coordinates)
                    cv2.rectangle(frame, (roi_x + x, roi_y + y), (roi_x + x + w, roi_y + y + h), (255, 0, 0), 2)
                    cv2.putText(frame, "Tracking", (roi_x + x, roi_y + y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                    # Map the object's center position in the ROI to the screen coordinates
                    screen_x = int((obj_center_x) * screen_width * 1.2 / roi_w - screen_width * 0.1)
                    screen_y = int((obj_center_y) * screen_height * 1.2 / roi_h - screen_height * 0.1)

                    # Move the mouse cursor
                    #pyautogui.moveTo(screen_x, screen_y, duration=10)
                    #win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, screen_x, screen_y, 0, 0)
                    #win32api.SetCursorPos((screen_x, screen_y))
                    # Calculate the relative movement
                    relative_x = screen_x - current_mouse_x
                    relative_y = screen_y - current_mouse_y

                    # Move the mouse cursor relative to its current position
                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, relative_x, relative_y, 0, 0)

                    # Update the current mouse position
                    current_mouse_x, current_mouse_y = screen_x, screen_y

                    # Update the previous position
                    prev_x, prev_y = adjusted_center_x, adjusted_center_y

                else:
                    # If the object hasn't moved enough, do not move the cursor
                    cv2.putText(frame, "Minimal movement, not tracking", (100, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
            else:
                # Initialize the previous position
                prev_x, prev_y = roi_x + obj_center_x, roi_y + obj_center_y
        else:
            # Reset tracking if the object is too small
            prev_x, prev_y = None, None
    else:
        # Reset tracking if no green object is detected
        prev_x, prev_y = None, None

    # Display the frame with the tracked object
    cv2.imshow("Tracking", frame)
    
    # Exit if the user presses the Esc key
    if cv2.waitKey(1) & 0xFF == 27:
        break

# Release the video capture and close all windows
cap.release()
cv2.destroyAllWindows()
