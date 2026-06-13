#!/usr/bin/python3

import logging
import time
from python_vlc_http import HttpVLC
from evdev import InputDevice, list_devices, ecodes

# Match this to display_rotate in /boot/config.txt (0, 1, 2, or 3). 0 if not set.
DISPLAY_ROTATE = 0
MAX_X = 480
MAX_Y = 640
# Defines left/right touch area
X_MARGIN = 100
# How far to seek fwd/back
SEEK_FWD = '+45'
SEEK_BACK = '-15'

def transform_coords(event_x, event_y):
    if DISPLAY_ROTATE == 0:
        return event_x, event_y
    elif DISPLAY_ROTATE == 1:  # 90 degrees
        return event_y, MAX_X - event_x
    elif DISPLAY_ROTATE == 2:  # 180 degrees
        return MAX_X - event_x, MAX_Y - event_y
    elif DISPLAY_ROTATE == 3:  # 270 degrees
        return MAX_Y - event_y, event_x
    else:
        logging.warning("Invalid DISPLAY_ROTATE value: %d, defaulting to 0", DISPLAY_ROTATE)
        return event_x, event_y

# Devices may be assigned to different event streams
# depending on order, kernel etc. so using direct path like 'event0'
# isn't reliable.
# This loops through devices and looks for touchscreen capabilities (ABS_MT)
def find_touch_device(retries=10, delay=2):
    for attempt in range(retries):
        for path in list_devices():
            device = InputDevice(path)
            caps = device.capabilities()
            if ecodes.EV_ABS in caps:
                abs_codes = [code for code, _ in caps[ecodes.EV_ABS]]
                if ecodes.ABS_MT_POSITION_X in abs_codes and ecodes.ABS_MT_POSITION_Y in abs_codes:
                    return device
        logging.warning("Touchscreen not found, retrying in %ds (attempt %d/%d)", delay, attempt+1, retries)
        time.sleep(delay)
    raise RuntimeError("Touchscreen not found after %d attempts" % retries)

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
    logging.info("Starting touch.py")
    device = find_touch_device()
    logging.info("Input device: %s", device)
    
    # Key event comes before location event. So assume first key down is in middle of screen
    x = int(MAX_X / 2)
    y = int(MAX_Y / 2)
    down_x = None
    down_y = None
    abs_x = 0
    abs_y = 0
    
    for event in device.read_loop():
        if event.type == ecodes.EV_KEY:
            if event.code == ecodes.BTN_TOUCH:
                if event.value == 0x0:
                    delta_x = x - down_x
                    delta_y = y - down_y
                    Act(x, y, delta_x, delta_y)
                if event.value == 0x1:
                    down_x = x
                    down_y = y
        elif event.type == ecodes.EV_ABS:
            if event.code == ecodes.ABS_MT_POSITION_X:
                abs_x = event.value
                logging.debug("Raw ABS_X: %d", abs_x)
            elif event.code == ecodes.ABS_MT_POSITION_Y:
                abs_y = event.value
                logging.debug("Raw ABS_Y: %d", abs_y)
            x, y = transform_coords(abs_x, abs_y)
            logging.debug("Transformed x: %d, y: %d", x, y)

# At one point this sleep was needed to ensure the VLC service has
# started already, not sure if it still is, but it's not hurting anything
time.sleep(3)

# The IP and password values here are defined in the start.sh script
controller = HttpVLC('http://127.0.0.1:9090', '', '1234')
main()