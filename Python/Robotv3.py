# Created by Fletcher Easton

import os;
import time;
import serial;
from Position import *;
import Motors;


def bounded(num, lower, upper):
    if(num > upper):
        return(upper);
    if(num < lower):
        return(lower);
    return(num);


class Robot:
    def __init__(self):
        self.motorSerial = None;
        self.position = Position(0,0);
        self.side = "Left";
        self.dataFile = "SensorData.db";
        self.atomicDataFile = "AtomicSensorData.db";

        self.home = Position(0, 0);

        self.phase = "Searching";

        self.speed = 25;
        self.frSpeed = self.speed;
        self.brSpeed = self.speed;
        self.blSpeed = self.speed;
        self.flSpeed = self.speed;
        self.xDirection = 1;
        self.rotation = 0;

        self.setupMotorSerial();
        self.readSideAndPosition();


    def setupMotorSerial(self):
        self.motorSerial = serial.Serial('/dev/ttyUSB0', 57600, timeout=0.1);

        time.sleep(5);

        while(self.motorSerial.in_waiting > 0):
            time.sleep(0.1);
            print(self.motorSerial.readline().decode());

        time.sleep(1);


    def readSideAndPosition(self):
        try:
            os.rename(self.dataFile, self.atomicDataFile);

            with open(self.atomicDataFile, "r") as f:
                self.side = f.readline().strip();
                readings = f.readline().strip().split(",");
                self.position = Position(float(readings[0]), float(readings[1]));
                self.rotation = float(f.readline().strip());
        except:
            pass;


    def moveToY(self, yPosition, exit, tolerance=3):
        if(abs(self.position.y - yPosition) > tolerance):
            if(self.position.y - yPosition > 0):
                Motors.setDirectionPosition(self.motorSerial, "RIGHT", abs(self.position.y - yPosition), self.speed);
            elif(self.position.y - yPosition < 0):
                Motors.setDirectionPosition(self.motorSerial, "LEFT", abs(self.position.y - yPosition), self.speed);
        else:
            Motors.stopMotors(self.motorSerial);
            time.sleep(0.1);
            self.phase = exit;


    def moveToX(self, xPosition, exit, tolerance=2):
        if(abs(self.position.x - xPosition) > tolerance):
            if(self.position.x - xPosition > 0):
                self.xDirection = -1;
                Motors.setMotorSpeed(self.motorSerial, self.frSpeed, self.brSpeed, -1 * self.blSpeed, -1 * self.flSpeed);
            elif(self.position.y - xPosition < 0):
                self.xDirection = 1;
                Motors.setMotorSpeed(self.motorSerial, -1 * self.frSpeed, -1 * self.brSpeed, self.blSpeed, self.flSpeed);

        else:
            Motors.stopMotors(self.motorSerial);
            time.sleep(0.1);
            self.phase = exit;


    def reorient(self, exit):
        Motors.rotate(self.motorSerial, -1 * self.rotation, self.speed);
        time.sleep(0.1);
        self.phase = exit;


    def updateMovement(self):
        if(abs(self.position.x - self.home.x) > 5):
            self.moveToX(self.home.x, "Searching", tolerance=5);
            self.phase = "X_Positioning";
        elif(abs(self.rotation) > 5):
            Motors.rotate(self.motorSerial, -1 * self.rotation / 2, self.speed);
            self.phase = "Rotating";
        elif(abs(self.position.y - self.home.y) > 5):
            self.moveToY(self.home.y, "Seraching", tolerance=5);
            self.phase = "Y_Positioning";
        else:
            self.phase = "Home";


    def updateRotation(self):
        max_speed_adjustment = self.speed;
        max_angle = 90;
        proportional_adjustment = self.rotation / max_angle *  max_speed_adjustment * self.xDirection;

        self.frSpeed = self.speed + proportional_adjustment;
        self.brSpeed = self.speed + proportional_adjustment;
        self.flSpeed = self.speed - proportional_adjustment;
        self.blSpeed = self.speed - proportional_adjustment;


    def stop(self):
        Motors.stopMotors(self.motorSerial);


    def printSpeeds(self):
        print("FR: {!r}".format(self.frSpeed));
        print("FL: {!r}".format(self.flSpeed));
        print("BR: {!r}".format(self.brSpeed));
        print("BL: {!r}".format(self.blSpeed));


if __name__ == '__main__':
    robot = Robot();

    while(True):
        robot.readSideAndPosition();
        robot.updateMovement();
        robot.updateRotation();
#        robot.printSpeeds();
        print(robot.position.toString() + " : " + str(robot.rotation));
        print(robot.phase);
