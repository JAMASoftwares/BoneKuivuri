# BoneKuivuri - Embedded single board computer project (Beaglebone Black)

Python Flask application for industry process control using surveillance IP-camera snapshots

## Device info
Beaglebone Black (BeagleBoard.org)
Debian GNU/Linux 11 - Bullseye IoT Image 2023-09-02

## Techologies
- Python Flask web server application
- Web client application interface (HTML, CSS, JavaScript)

## Python (libraries and dependencies)
Program is running by Python 3.9.2

Adafruit_BBIO       1.2.0
Flask               1.1.2
Flask_Cors          4.0.1
Flask_SocketIO      5.3.6
Pillow              10.4.0
psutil              6.0.0
py_cpuinfo          9.0.0


## Functionalities
- System information checking, GPIO pin map, and Beaglebone Black gallery.
- Wep page to save IP-camera snapshot into the storage of Beaglebone Black.
- Web page to check and control triggered snapshots from the IP-camera.

## Manual and trigger based automated snapshots from the IP-camera based on the input signal
Flask application uses analog input GPIO pin for listening the voltage of connected circuit.
If value exceeds the pre-configured threshold value, IP-camera snapshot will be triggered with certain pre-conditions
1. Frequency of snapshots is limited
2. When signal voltage exceeds the configured threshold, snapshot will be triggered if a time stamp of previous snapshot is more than a minimum value (e.g. 60 minutes)
3. If the signal voltage remains permanently higher than the threshold new snapshot WILL NOT BE triggered, although configured minimum snapshot frequency value (e.g. 60 minutes) has been exceeded.
   
## Web interface for the review of IP-camera snapshot images and BBB system information.
