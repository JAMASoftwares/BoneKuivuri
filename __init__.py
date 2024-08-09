import os
import time
import json

# Read GPIO data from file:
GPIO_DICT_P9 = json.load(open("data/gpiop9.json"))
GPIO_DICT_P8 = json.load(open("data/gpiop8.json"))
AIN_DICT = json.load(open("data/analog.json"))
GPIOPATH = ("/sys/class/gpio")

# Verify dictionary content if needed
# print(GPIO_DICT.keys())
# print(GPIO_DICT.items())


# Function to export GPIO pins
def export_gpio_pins_from_dict(gpio_data, gpio_path):
    exported = []
    for key, values in gpio_data.items():
        gpio_pin_path = values["path"]
        # Make sure pin is exported
        if not os.path.exists(gpio_pin_path):
            try:
                with open(os.path.join(gpio_path, "export"), "w") as f:
                    f.write(values["gpio"][4:])
                exported.append(values["gpio"])
                print(f"Exported GPIO pin {values['gpio'][4:]}")
            except IOError as e:
                print(f"Error exporting GPIO pin {values['gpio'][4:]}: {e}")
    
    exported.sort()
    print("Init GPIO: Exported pins: ", exported)

# Function to set the direction of GPIO pins
def direct_gpio_pins_from_dict(gpio_data):
    set_out = []
    set_out_err = []
    for key, values in gpio_data.items():
        direction_path = os.path.join(values['path'], 'direction')
        try:
            # Read the current direction
            with open(direction_path, "r") as f:
                current_direction = f.read().strip()
            
            # Set direction to 'out' if it's not already 'out'
            if current_direction != "out":
                with open(direction_path, "w") as f:
                    f.write("out")
                set_out.append(values['gpio'])
        except IOError as e:
            set_out_err.append(values['gpio'])
            print(f"Error accessing GPIO pin {values['gpio'][4:]} direction: {e}")

    set_out.sort()
    set_out_err.sort()
    print("Init GPIO: Pin directions [out]: ", set_out)
    #print("Init GPIO: Pin direction setup failures: ", set_out_err)

# Export and Set pins out from dictionaries
export_gpio_pins_from_dict(GPIO_DICT_P9 | GPIO_DICT_P8, GPIOPATH)
time.sleep(1) # Allow some time for the system to set up the GPIO files
direct_gpio_pins_from_dict(GPIO_DICT_P9 | GPIO_DICT_P8)
