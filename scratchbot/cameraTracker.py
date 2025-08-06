import serial
import time
import sys
import os
import json
import keyboard


#TODO
# add to settings - motor step delay, baudrate, COM port, ticket top
#UI
'''
go to front
go to back
go to ticket top
go to mm
figure position

'''

#NEED IN Scratchbot
#get camera out of the way for end and start etc
#moveCamera
#when interupting mocve to, need to getposition....

# TESTarduino - need check stop during move

camSettings = 'poseData/camSettings.json';

camdata = {}
arduino = False
com = "COM7"
br = 115200

def initCamera():
    global arduino
    global camdata
    arduino = serial.Serial(port=com, baudrate=br, timeout=.1) 
    camdata = getCamFileData()
    print("\n\r\nCAMERA INITIALIZED")
    print(camdata)
    pushSettings(camdata)

def pushSettings(d = False):
    if arduino:
        if not d:
            d = getCamFileData()
        write(f"setTotalSteps{d['totalSteps']}")
        time.sleep(.1)
        write(f"setStepsFromFront{d['stepsFromFront']}")
        time.sleep(.1)
        write(f"setStepsFromBack{d['stepsFromBack']}")
        time.sleep(.1)

def pullSettings(which = ['t','f','b']):
    global camdata
    if arduino:     
        if which.includes('t'):
            r = write_wait_read("getTotalSteps")
            camdata['totalSteps'] = int(r.decode('utf-8'))

        if which.includes('f'):
            r = write_wait_read("getStepsFromFront")
            camdata['stepsFromFront'] = int(r.decode('utf-8'))

        if which.includes('b'):
            r = write_wait_read("getStepsFromBack")
            camdata["stepsFromBack"] = int(r.decode('utf-8'))


def write_read(x): 
    arduino.write(bytes(x, 'utf-8')) 
    time.sleep(0.05) 
    data = arduino.readline() 
    return data 

def write(x):
    arduino.write(bytes(x, 'utf-8'))

def write_wait_read(x, wait = True):
    if(wait):
        arduino.reset_input_buffer()
        arduino.reset_output_buffer()
        arduino.write(bytes(x, 'utf-8')) 
        while True:
            if arduino.in_waiting > 0:
                data = arduino.read(arduino.in_waiting)
                return data
            time.sleep(1)
    else:
        write(x)
        return False

def goToBack(wait = False):
    global camdata
    if arduino:
        r = write_wait_read('goToBack', wait)
    
def goToFront(wait = False):
    global camdata
    if arduino:
        r = write_wait_read('goToFront', wait)
    

def saveCamData():
    with open(camSettings, 'w+') as f:
        json.dump(camdata, f, indent=4)

def getCamFileData():
    with open(camSettings, 'r') as f:
        c = json.load(f)
    return c
 
def getCurrentPosition():
    if arduino:
        r = write_wait_read('figureCurrentPosition')
        print(f"steps from back: {r.decode('utf-8')}")
        camdata['stepsFromBack'] = int(r.decode('utf-8'))
        camdata['stepsFromFront'] = camdata['totalSteps'] - camdata['stepsFromBack']
        saveCamData()

def goToTicketTop(wait = True):
    if arduino:
        moveToStep(camdata['ticketTop'] + (camdata['cameraTicketOffset'] * camdata['scaler']), wait)


def setTicketTop(mm):
    if arduino:
        pullSettings['b']
        camdata['ticketTop'] = camdata['stepsFromBack']
        saveCamData()

def moveToStep(step, wait = False):
    print(f"\r\n\r\nCAM TO STEP {step}")
    if arduino:
        r = write_wait_read(f"moveToStep{step}", wait)

def moveToMm(mm, wait = False):
    print(f"\r\n\r\nCAM TO {mm}")
    if arduino:
        s =  camdata['ticketTop'] - (camdata["cameraTicketOffset"] * camdata['scaler']) - (int(mm) * camdata['scaler'])
        moveToStep(s)


