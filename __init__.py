import json
import os
from gpiod import LineSettings
from gpiod.line import Direction, Value
import gpiod


# Load GPIO dictionaries
GPIO_DICT_P8 = json.load(open("data/gpiop8.json"))
GPIO_DICT_P9 = json.load(open("data/gpiop9.json"))
AIN_DICT = json.load(open("data/analog.json"))

# Combine all pins
all_pins = GPIO_DICT_P8 | GPIO_DICT_P9

# Global dictionary to hold chip requests keyed by chip path
chip_requests = {}

def initialize_all_pins():
    """
    Initialize and request lines for all pins grouped by chip
    Set outputs to INACTIVE and store state, inputs store None state.
    """
    # Group pin configs by chip
    chip_configs = {}
    for pin_dict in [GPIO_DICT_P8, GPIO_DICT_P9]:
        for pin_name, pin_data in pin_dict.items():
            chip = pin_data["chip"]
            line_offset = pin_data["line"]
            dir_str = pin_data.get("dir", "").lower()
            if chip not in chip_configs:
                chip_configs[chip] = {}
            if dir_str == "out":
                chip_configs[chip][line_offset] = LineSettings(direction=Direction.OUTPUT, output_value=Value.INACTIVE)
                pin_data["state"] = '0'
            elif dir_str == "in":
                chip_configs[chip][line_offset] = LineSettings(direction=Direction.INPUT)
                pin_data["state"] = None

    # Request all lines per chip and store request objects globally
    for chip_path, config in chip_configs.items():
        request = gpiod.request_lines(chip_path, consumer="gpio-init", config=config)
        chip_requests[chip_path] = request

def toggle_pin(pin_name, pin_data):
    """
    Toggle the pin output value and update stored states
    Use existing request objects.
    """
    chip_path = pin_data["chip"]
    line_offset = pin_data["line"]

    request = chip_requests.get(chip_path)
    if request is None:
        raise RuntimeError(f"No request found for chip: {chip_path}")

    current_state = pin_data.get("state", Value.INACTIVE)
    new_state = Value.INACTIVE if current_state == Value.ACTIVE else Value.ACTIVE

    request.set_value(line_offset, new_state)

    # Update states in all dictionaries
    pin_data["state"] = new_state
    all_pins[pin_name]["state"] = new_state
    if pin_name in GPIO_DICT_P8:
        GPIO_DICT_P8[pin_name]["state"] = new_state
    elif pin_name in GPIO_DICT_P9:
        GPIO_DICT_P9[pin_name]["state"] = new_state

    return new_state

def read_pin_state(pin_data):
    """
    Read the pin value from the stored request.
    For output pins, reads the output state.
    For input pins, reads the input level.
    """
    chip_path = pin_data["chip"]
    line_offset = pin_data["line"]

    request = chip_requests.get(chip_path)
    if request is None:
        raise RuntimeError(f"No request found for chip: {chip_path}")

    val = request.get_value(line_offset)
    return val  # 0 or 1

# On program start
initialize_all_pins()

# Example usage
# state = read_pin_state(all_pins["P8_11"])
# toggle_pin("P8_11", all_pins["P8_11"])