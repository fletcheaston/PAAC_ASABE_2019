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

        self.neutralY = 55;
        self.nextPosition = Position(0, 0);
        self.phase = "Wait";
        self.xDirection = 1;

        self.speed = 50;
        self.frSpeed = self.speed;
        self.brSpeed = self.speed;
        self.blSpeed = self.speed;
        self.flSpeed = self.speed;
        self.rotation = 0;

        self.setupMotorSerial();
        self.readSideAndPosition();

        self.taskPositions = [Position(30, 15), Position(10, 90), Position(40, 15), Position(20, 90), Position(50, 15), Position(30, 90), Position(60, 15), Position(40, 90), Position(70, 15), Position(50, 90)];
        self.taskCount = 0;

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


    def moveToPosition(self, position):
        self.nextPosition = position;
        self.phase = "GoToNeutral";


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


    def moveToX(self, xPosition, exit, tolerance=3):
        if(abs(self.position.x - xPosition) > tolerance):
            if(self.position.x - xPosition > 0):
                Motors.setDirectionPosition(self.motorSerial, "BACKWARD", abs(self.position.x - xPosition), self.speed);
            elif(self.position.x - xPosition < 0):
                Motors.setDirectionPosition(self.motorSerial, "FORWARD", abs(self.position.x - xPosition), self.speed);
        else:
            Motors.stopMotors(self.motorSerial);
            time.sleep(0.1);
            self.phase = exit;


    def reorient(self, exit):
        Motors.rotate(self.motorSerial, -1 * self.rotation, self.speed);
        time.sleep(0.1);
        self.phase = exit;


    def updateMovement(self):
        if(self.phase == "Wait"):
            pass;

        elif(self.phase == "GoToNeutral"):
            self.moveToY(self.neutralY, "TraverseNeutral", tolerance=5);

        elif(self.phase == "TraverseNeutral"):
            self.moveToX(self.nextPosition.x, "WallMash", tolerance=2);

        elif(self.phase == "WallMash"):
            if(self.nextPosition.y < self.position.y):
                self.phase = "WallMashBottom";
            else:
                self.phase = "WallMashTop";
        elif(self.phase == "WallMashTop"):
            self.moveToY(95, "ExitNeutral", tolerance=3);
        elif(self.phase == "WallMashBottom"):
            self.moveToY(0, "ExitNeutral", tolerance=3);

        elif(self.phase == "ExitNeutral"):
            self.moveToY(self.nextPosition.y, "ReadjustX", tolerance=3);

        elif(self.phase == "ReadjustX"):
            self.moveToX(self.nextPosition.x, "Wait", tolerance=1);


    def updateRotation(self):
        max_speed_adjustment = 20;
        max_angle = 90;
        proportional_adjustment = self.rotation / max_angle *  max_speed_adjustment * self.xDirection;

        self.frSpeed = self.speed + proportional_adjustment;
        self.brSpeed = self.speed + proportional_adjustment;
        self.flSpeed = self.speed - proportional_adjustment;
        self.blSpeed = self.speed - proportional_adjustment;


    def stop(self):
        Motors.stopMotors(self.motorSerial);


if __name__ == '__main__':
    robot = Robot();

    while(True):
        time.sleep(0.1);
        robot.readSideAndPosition();
        robot.updateMovement();
        robot.updateRotation();

        print(robot.position.toString() + " : " + str(robot.rotation));
        print("Next Position: " + robot.taskPositions[robot.taskCount - 1].toString());
        print(robot.phase);

#        if(abs(robot.rotation) > 5):
 #           Motors.rotate(robot.motorSerial, -1 * robot.rotation / 2, robot.speed);
  #          time.sleep(0.25);

        if(robot.phase == "Wait"):
            if(robot.taskCount < len(robot.taskPositions)):
                robot.moveToPosition(robot.taskPositions[robot.taskCount]);
                robot.taskCount = robot.taskCount + 1;
