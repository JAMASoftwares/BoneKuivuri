#!/usr/bin/env python
# ////////////////////////////////////////
# //	pushbutton.py
# //      Reads P9_42 and prints its value.
# //	Wiring:	Connect a switch between P9_42 and 3.3V
# //	Setup:	
# //	See:	
# ////////////////////////////////////////
import gpiod

cam_button = {"chip": "/dev/gpiochip3", "line": 7}  # P9_42
cam_led = {"chip": "/dev/gpiochip0", "line": 13}     # P8_11

def readCamButtonValue():
    chip_btn = gpiod.Chip(cam_button["chip"])
    line_btn = chip_btn.get_line(cam_button["line"])
    line_btn.request(consumer="cam-button", type=gpiod.LineRequest.DIRECTION_INPUT)
    button_state = line_btn.get_value()
    line_btn.release()
    chip_btn.close()

    chip_led = gpiod.Chip(cam_led["chip"])
    line_led = chip_led.get_line(cam_led["line"])
    line_led.request(consumer="cam-led", type=gpiod.LineRequest.DIRECTION_OUTPUT, default_vals=[0])
    if button_state:
        line_led.set_value(1)
    else:
        line_led.set_value(0)
    line_led.release()
    chip_led.close()

    return button_state
