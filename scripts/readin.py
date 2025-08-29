import gpiod
from gpiod.line import Direction, Value
import os


def readAinValue():
    try:
        ain_path = "/sys/bus/iio/devices/iio:device0/in_voltage5_raw"
        with open(ain_path, "r") as f:
            raw_value = int(f.read().strip())

        # BeagleBone Black analog input max voltage is 1.8V (12 bit ADC: 0-4095)
        voltage = (raw_value / 4095.0) * 1.8

        return voltage

    except Exception as e:
        print(f"Error reading AIN5 voltage from sysfs: {e}")
        return 0.0



"""
#!/usr/bin/env python3
# //////////////////////////////////////
# 	analogin.py
# 	Reads the analog value of the light sensor.
# //////////////////////////////////////
import time
import os

pin = "2"  # light sensor, A2, P9_37

IIOPATH = "/sys/bus/iio/devices/iio:device0/in_voltage" + pin + "_raw"

print("Hit ^C to stop")

f = open(IIOPATH, "r")

while True:
    f.seek(0)
    x = float(f.read()) / 4096
    print("{}: {:.1f}%, {:.3f} V".format(pin, 100 * x, 1.8 * x), end="\r")
    time.sleep(0.1)
"""

# Bone  | Pocket | AIN
# ----- | ------ | ---
# P9_39 | P1_19  | 0
# P9_40 | P1_21  | 1
# P9_37 | P1_23  | 2
# P9_38 | P1_25  | 3
# P9_33 | P1_27  | 4
# P9_36 | P2_35  | 5
# P9_35 | P1_02  | 6
