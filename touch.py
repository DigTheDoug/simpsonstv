#!/usr/bin/python3

import evdev
import logging
from python_vlc_http import HttpVLC
import time

# This is oddly swapped. X is actually the long dimension on the physical screen.
MAX_X = 480
MAX_Y = 640

# Defines left/right touch area
X_MARGIN = 100

# How far to seek fwd/back
SEEK_FWD = '+45'
SEEK_BACK = '-15'


# Commands here: https://github.com/MatejMecka/python-vlc-http
def Act(x: int, y: int, delta_x: int, delta_y: int):
    # Swipe right
    if delta_x > MAX_X / 2:
        logging.info("VLC command: playlist-next")
        controller.next_track()
    # Swipe left
    elif delta_x < -(MAX_X / 2):
        logging.info("VLC command: playlist-prev")
        controller.previous_track()
    # Right touch
    elif x > MAX_X - X_MARGIN:
        logging.info(f"VLC command: seek {SEEK_FWD}")
        controller.seek(SEEK_FWD)
    # Left touch
    elif x < X_MARGIN:
        logging.info(f"VLC command: seek {SEEK_BACK}")
        controller.seek(SEEK_BACK)
    # Middle touch
    else:
        logging.info("VLC command: cycle pause")
        controller.pause()


def main():
    logging.getLogger().setLevel(logging.INFO)
    device = evdev.InputDevice("/dev/input/event0")
    logging.info("Input device: %s", device)

    # Key event comes before location event. So assume first key down is in middle of screen
    x = int(MAX_X / 2)
    y = int(MAX_Y / 2)

    down_x = None
    down_y = None

    for event in device.read_loop():
        if event.type == evdev.ecodes.EV_KEY:
            if event.code == evdev.ecodes.BTN_TOUCH:
                if event.value == 0x0:
                    delta_x = x - down_x
                    delta_y = y - down_y
                    Act(x, y, delta_x, delta_y)
                if event.value == 0x1:
                    down_x = x
                    down_y = y
        elif event.type == evdev.ecodes.EV_ABS:
            # Screen is rotated, so X & Y are swapped from how the input reports them.
            if event.code == evdev.ecodes.ABS_MT_POSITION_X:
                y = MAX_Y - event.value
            elif event.code == evdev.ecodes.ABS_MT_POSITION_Y:
                x = MAX_X - event.value

# At one point this sleep was needed to ensure the VLC service has
# started already, not sure if it still is, but it's not hurting anything
time.sleep(3)

# The IP and password values here are defined in the start.sh script
controller = HttpVLC('http://127.0.0.1:9090', '', '1234')
main()