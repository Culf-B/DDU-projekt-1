"""Prints the palm position of each hand, every frame. When a device is 
connected we set the tracking mode to desktop and then generate logs for 
every tracking frame received. The events of creating a connection to the 
server and a device being plugged in also generate logs. 
"""

import leap
import time
import math
import win32api, win32con

class MyListener(leap.Listener):
    def __init__(self):
        self.handpos = [0, 0, 0]
        self.handid = ""

    def move(self, prevPos, newPos):
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(4 * (newPos[0] - prevPos[0])), int(4 * (-(newPos[1] - prevPos[1]))), 0, 0)

    def on_connection_event(self, event):
        print("Connected")

    def on_device_event(self, event):
        try:
            with event.device.open():
                info = event.device.get_info()
        except leap.LeapCannotOpenDeviceError:
            info = event.device.get_info()

        print(f"Found device {info.serial}")

    def on_tracking_event(self, event):
        self.prevHandpos = self.handpos
        if len(event.hands) == 0:
            return

        # Check if with same id as previous is detected
        for hand in event.hands:
            if hand.id == self.handid:
                self.handpos = [int(hand.palm.position.x), int(hand.palm.position.y), int(hand.palm.position.z)]
                
                # Move the mouse
                self.move(self.prevHandpos, self.handpos)
                
                return # Now that the position is updated, we can exit the function
    
        # If we have not exited the function by now, the previosly tracked hand has disappered
        # Now we want to track the hand closest to the previous hands position
        self.closestHandIndex = 0
        self.closestHandDist = 1000000000
        self.currentIndex = 0
        self.currentDist = 0
        for hand in event.hands:
            self.currentDist = math.sqrt(abs((hand.palm.position.x - self.handpos[0]) ** 2 + (hand.palm.position.y - self.handpos[1]) ** 2 + (hand.palm.position.z - self.handpos[2] ** 2)))
            if self.currentDist < self.closestHandDist:
                self.closestHandIndex = self.currentIndex
                self.closestHandDist = self.currentDist
            self.currentIndex += 1

        # Update the hand
        self.handid = event.hands[self.closestHandIndex]
        self.handpos = [event.hands[self.closestHandIndex].palm.position.x, event.hands[self.closestHandIndex].palm.position.y, event.hands[self.closestHandIndex].palm.position.z]

        # Move the mouse
        self.move(self.prevHandpos, self.handpos)

def main():
    my_listener = MyListener()

    connection = leap.Connection()
    connection.add_listener(my_listener)

    running = True

    with connection.open():
        connection.set_tracking_mode(leap.TrackingMode.Desktop)
        while running:
            print(my_listener.handpos)
            time.sleep(0.1)


if __name__ == "__main__":
    main()