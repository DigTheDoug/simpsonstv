#!/usr/bin/python3

import logging
import RPi.GPIO as GPIO
import time
import os


def turnOnScreen():
    logging.info("turnOnScreen")
    # Enable audio
    os.system("raspi-gpio set 19 op a5")
    # Turn on screen backlight
    GPIO.output(18, GPIO.HIGH)


def turnOffScreen():
    logging.info("turnOffScreen")
    # Mute audio
    os.system("raspi-gpio set 19 ip")
    # Turn off screen backlight
    GPIO.output(18, GPIO.LOW)


def main():
    logging.getLogger().setLevel(logging.INFO)

    # Initial GPIO setup
    GPIO.setmode(GPIO.BCM)
    # Set pin 26 as input to monitor button press
    GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    # Set pin 18 as output to control screen backlight
    GPIO.setup(18, GPIO.OUT)

    turnOffScreen()
    screen_on = False

    while True:
        # If you are having and issue with the button doing the opposite of what you want
        # IE Turns on when it should be off, change this line to:
        # input = GPIO.input(26)
        input = not GPIO.input(26)
        if input != screen_on:
            screen_on = input
            if screen_on:
                turnOnScreen()
            else:
                turnOffScreen()
        time.sleep(0.3)


main()
