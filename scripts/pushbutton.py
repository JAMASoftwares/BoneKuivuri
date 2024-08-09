#!/usr/bin/env python
# ////////////////////////////////////////
# //	pushbutton.py
# //      Reads P9_42 and prints its value.
# //	Wiring:	Connect a switch between P9_42 and 3.3V
# //	Setup:	
# //	See:	
# ////////////////////////////////////////
import Adafruit_BBIO.GPIO as GPIO

cam_button = "P9_42"
cam_led = "P8_11"
GPIO.setup(cam_button, GPIO.IN)
GPIO.setup(cam_led, GPIO.OUT)


def readCamButtonValue():

    button_state = GPIO.input(cam_button)
    if button_state:
        GPIO.output(cam_led, GPIO.HIGH)
    else:
        GPIO.output(cam_led, GPIO.LOW)
    return button_state
