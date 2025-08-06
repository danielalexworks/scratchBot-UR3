import serial
import time
import math
import keyboard
import csv
import os
import sys
import random

import helpers
#import scratchers

#install limit switches

###########################################
#----SETTINGS-----------------------------#
###########################################
debugging = False

zheights = [[]]

#ticket csv
scratchData = "MI6M_ticketBoxes.csv"
outfile = "zoffsets_" + time.time() + ".csv"
#scratchData = "test.csv"
#offset of ticket corner bit start
offy = -32 #-56 -58
offx = -2   #-60 -73
#width of cutting bit in mm
bitw = 8
#overlap of cut passes TODO dial in
passOffset = 0
#zheight for scratching
scratchz = -43.7##might need to adjust for y position TODO
#how far to stop above scrathz before motor startst
zprepoffset = -2 #TODO set prep height
#distance between z height adjustments
movementResolution = 5

zadj = 0
scratchTimer = 0

cnc = True
travelSpeed = 200
travelSpeedCut = 100

jogDirection = 1
direction = 1
isMotorOn = False

#TODO speed
motorSpeed = 200

#set home values ( max distance to travel to get back home)
hx = 250
hy = 150
hz = 45 #46

tx = 0
ty = 0
tz = 0

#y 84
scratchArea = []

def wait():
    send_gcode("G4 P0")


def initialize_cnc():
    global cnc
    if debugging == False:
        cnc = serial.Serial('COM9', 115200, timeout=1)  # Update 'COM3' to your CNC's port
        print('initializing...')
        # Wait for the CNC controller to be ready
        time.sleep(2)  # Wait for 2 seconds to establish a connection
        cnc.write(b"\r\n\r\n")  # Send a newline to wake up GRBL
        time.sleep(2)  # Wait for GRBL to initialize
        cnc.flushInput()  # Flush any initial data in the serial buffer
        print('complete')
        goToStart()

def send_gcode(command):
    if debugging == False:
        # Send the G-code command to the CNC machine
        cnc.write((command + '\n').encode())  # Send the command with a newline
        cnc.flush()  # Wait for the transmission to complete
        time.sleep(0.1)  # Pause to give time for processing

        # Read and print the response from the CNC
        response = cnc.readline().decode().strip()
        if(response != 'ok'):
            print(f"Response: {response}")
    else:
        #print(command)
        m = 0



def MoveX(x, t = 'move'):
    global tx
    global jogDirection
    global scratchTimer

    scratchTimer += abs(x)
   
    if x < 0:
        mres = -movementResolution
        neg = True
    else:
        mres = movementResolution
        neg = False


    while (neg and x < 0) or (not neg and x > 0):
        if abs(x) > abs(mres):
            cmd = "G21G91X" + str(mres) + "F"
            tx += mres
        else:
            cmd = "G21G91X" + str(x) + "F"
            tx += x

        if t == 'cut':
            cmd += str(travelSpeedCut)
        else:
            cmd += str(travelSpeed)

        send_gcode(cmd)
        x -= mres
        

def MoveY(y, t = 'move'):
    global ty
    global jogDirection
    global scratchTimer

    scratchTimer += abs(y)

    if y < 0:
        mres = -movementResolution
        neg = True
    else:
        mres = movementResolution
        neg = False
    while (neg and y < 0) or (not neg and y > 0):
        if abs(y) > abs(mres):
            cmd = "G21G91Y" + str(mres) + "F"
            ty += mres
        else:
            cmd = "G21G91Y" + str(y) + "F"
            ty += y

        if t == 'cut':
            cmd += str(travelSpeedCut)
        else:
            cmd += str(travelSpeed)

        send_gcode(cmd)
        y -= mres
  

def MoveZ(z, t = 'move'):
    global tz
    global jogDirection
    global scratchTimer

    scratchTimer += abs(z)

    cmd = "G21G91Z" + str(z) + "F"
    if t == 'cut':
        cmd += str(100)
    else:
        cmd += str(600)

    send_gcode(cmd)
    tz += z;
    tz = round(tz, 2)
    #print(tz)


def motorOn():
    #print("M3 S" + str(motorSpeed))
    global isMotorOn

    isMotorOn = True
    send_gcode("M3 S" + str(motorSpeed))

def motorOff():
    global isMotorOn

    isMotorOn = False
    send_gcode("M5")

#move motors back to starting position base on distance traveled in last move
def tryHome():
    global tx,ty,tz, firstScratch

    firstScratch = True
    wait()
    print("tx,ty,tz: " + str(tx) + ',' + str(ty) + ',' + str(tz))
   
    if(abs(tx) + abs(tz) + abs(ty) > 0):
        print("trying to go home: YES")
        if tz:
            MoveZ(-tz)
            tz = 0
        if tx:
            MoveX(-tx)
            tx = 0
        if ty:
            MoveY(-ty)
            ty = 0

    else:
        print("try go home: NO")

def goToStart():
    MoveX(offx - 40)
    MoveY(offy - (bitw/2))
    MoveZ(scratchz)

def goToNext():
    global xrow,yrow 

    print('[' + str(xrow) + '][' + str(yrow) + '] = ' + str(tz))
   
    zheights[xrow].append(tz)

    yrow += 1
    if yrow > 11:
        xrow += 1
        yrow = 0
        MoveZ(2)
        MoveX(-8)
        MoveY(88)
        MoveZ(-2)
        zheights.append([])
    else:
        MoveY(-8)



## PROGRAM START ##

#debugging = True
xrow = 0
yrow = 0
# Initialize CNC connection
initialize_cnc()
firstScratch = True

dis = False
while True:
    print('command:', end=' ', flush=True)
    
    k = keyboard.read_key() 
    print(k)
    
    if k == 'n':
        goToNext()

    elif k == 't':
        tryHome()

    elif k == 'esc':
        exit()

    elif k == 'd':
        MoveZ(round(-0.05, 2))
    elif k == 'u':
        MoveZ(round(0.05, 2))
    elif k == 'm':
        if isMotorOn:
            motorOff()
        else:
            motorOn()

    elif k == 'b':
        if dis == False:
            MoveZ(5)
            dis = True
        else:
            MoveZ(-5)
            dis = False


    elif k == 'o':

        for i in range(0,len(zheights)):
            st = '['
            for j in range(0,len(zheights[i])):
                st += str(zheights[i][j]) + ','
            st = st[:-1] + '],'
            print(st)


        ##new stuff may not work?
        zheights = [[0] * len(zheights[0]) for _ in range(4)] + zheights

        with open(outfile, 'w', newline='') as c:
            writer = csv.writer(c)
            writer.writerows(zheights)


    time.sleep(.2)

cnc.close()

