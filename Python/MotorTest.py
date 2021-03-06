# Created by Fletcher Easton

from Motors import *;
import time;
import serial;

motorSerial = serial.Serial('/dev/ttyUSB0', 57600, timeout=0.1);

time.sleep(5);

while(motorSerial.in_waiting > 0):
    time.sleep(0.1);
    print(motorSerial.readline().decode());

time.sleep(1);

setDirectionSpeed(motorSerial, "FORWARD", 100);

while(True):
    motorSerial.write(b"M");

    time.sleep(0.25);

    while(motorSerial.in_waiting > 0):
        time.sleep(0.1);
        print(motorSerial.readline().decode().strip());

