import serial
import time
import sys
import os
import json
import keyboard

#MOVETO is checking wrong stop?
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
#moveCamera
#when interupting mocve to, need to getposition....

# TESTarduino - need check stop during move

setts = True


camSettings = 'poseData/camSettings.json';

camdata = {}

if len(sys.argv) > 1:
    com = sys.argv[1]
else:
    com = 'COM4'
if len(sys.argv) > 2:
    br = sys.argv[2]
else:
    br = 115200

arduino = serial.Serial(port=com, baudrate=br, timeout=.1) 


'''
calibrate             returns complete
changeDirection       returns complete
forward               returns complete
backward              returns complete
goToFront             returns complete
goToBack              returns complete
figureCurrentPosition returns stepsFromBack
moveToStepxxxx        returns stepsFromBack
setTotalSteps         returns complete
setStepsFromBack      returns complete
setStepsFromFront     returns complete
getTotalSteps         returns totalSteps
getStepsFromBack      returns stepsFromBack
getStepsFromFront     returns stepsFromFront
'''
def printHelp():
    print("---VALID COMMANDS---")
    
    commands = [
        ["c :","run calibrate routine"],
        ["t :","set ticket top position"],
        ["multi :", "set scale multplier"],
        ["gott :", "go to ticket top position"],
        ["gotomm :", "go to position n mm back from top of ticket"],
        ["f :","goToFront"],
        ["b :","goToBack"],
        ["p :","run figure current position routine"],
        ["m :","move to step position"],
        ["sd :","set step delay"],
        ["st :","set total steps"],
        ["sf :","set steps from front"],
        ["sb :","set steps from back"],
        ["gt :","get total steps"],
        ["gf :","get steps from front"],
        ["gb :","get steps from back"],
        ["d :","print saved camera data"],
        ["s :", "save local camdata to file"],
        ["q :","close program"]

    ]
    col_width = max(len(row[0]) for row in commands) + 3

    for row in commands:
        print(f"{row[0]:<{col_width}} {row[1]}")



def write_read(x): 
    arduino.write(bytes(x, 'utf-8')) 
    time.sleep(0.05) 
    data = arduino.readline() 
    return data 

def write(x):
    arduino.write(bytes(x, 'utf-8'))

def write_wait_read(x):
    if(setts):
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

def saveCamData():
    with open(camSettings, 'w+') as f:
        json.dump(camdata, f, indent=4)

def getCamFileData():
    with open(camSettings, 'r') as f:
        c = json.load(f)
    return c
 

camdata = getCamFileData()
printHelp();
while True:
        k = input("input command code: ")

        if k == 'c' : 
            r = write_wait_read('calibrate')
            print(r)
            while True:
                s = input("save results(y/n)?")
                if s == 'y':
                    t = write_wait_read('getTotalSteps')
                    t = int(t.decode('utf-8').rstrip('\r\n'))
                    camdata['totalSteps'] = t
                    camdata['stepsFromBack'] = 0
                    camdata['stepsFromFront'] = t
                    saveCamData()
                    break
                elif s == 'n':
                    break

        elif k == 'f' :
            r = write_wait_read('goToFront')
            camdata['stepsFromFront'] = 0

            print(r)
        elif k == 'b' :
            r = write_wait_read('goToBack')
            camdata['stepsFromBack'] = 0
            print(r)
        elif k == 'p' :
            r = write_wait_read('figureCurrentPosition')
            print(f"steps from back: {r.decode('utf-8')}")
            while True:
                s = input("save results(y/n)?")
                if s == 'y':
                    t = write_wait_read('getTotalSteps')
                    t = int(t.decode('utf-8'))
                    camdata['stepsFromBack'] = int(r.decode('utf-8'))
                    if t:
                        camdata['totalSteps'] = t
                        camdata['stepsFromFront'] = t-camdata['stepsFromBack']
                    saveCamData()
                    break
                elif s == 'n':
                    break
        elif k == 'm' :
            s = input("input step position number: ")
            #r = write_wait_read(f'moveToStep{s}')
            r = write(f'moveToStep{s}')
            if r and not 'error' in r.decode('utf-8'):
                print(f"steps from back: {r.decode('utf-8')}")
                
                t = write_wait_read('getTotalSteps')
                t = int(t.decode('utf-8'))
                camdata['stepsFromBack'] = int(r.decode('utf-8'))
                if t:
                    camdata['totalSteps'] = t
                    camdata['stepsFromFront'] = t-camdata['stepsFromBack']
                saveCamData()
                    
            else:
                print(r)
        elif k == 'st' :
            d = getCamFileData()
            r = write_wait_read(f"setTotalSteps{d['totalSteps']}")
            print(r)

        elif k == 'sd' :
            d = getCamFileData()
            r = write_wait_read(f"setStepDelay{d['stepDelay']}")
            print(r)

        elif k == 'sf' :
            d = getCamFileData()
            r = write_wait_read(f"setStepsFromFront{d['stepsFromFront']}")
            print(r)

        elif k == 'sb' :
            d = getCamFileData()
            r = write_wait_read(f"setStepsFromBack{d['stepsFromBack']}")
            print(r)

        elif k == 'gt' :
            r = write_wait_read("getTotalSteps")
            print(r)
            camdata['totalSteps'] = r

        elif k == 'gf' :
            r = write_wait_read("getStepsFromFront")
            print(r)
            camdata['stepsFromFront'] = r

        elif k == 'gb' :
            r = write_wait_read("getStepsFromBack")
            print(r)
            camdata["stepsFromBack"] = r

        elif k == 'd' :
            d = getCamFileData()
            print(d)

        elif k == 's':
            saveCamData()

        elif k == 't':
            camdata['ticketTop'] = camdata["stepsFromBack"]
            saveCamData()

        elif k == 'gott':
            r = write_wait_read(f"moveToStep{camdata['ticketTop']}")
            print(r)
            camdata['stepsFromBack'] = camdata['ticketTop']
            camdata['stepsFromFront'] = camdata['totalSteps'] - camdata['stepsFromBack']
            saveCamData()
        elif k == 'multi':
            i = input('Enter number of steps per mm:')
            camdata['scaler'] = int(i)
            print(camdata)
            saveCamData()
        elif k == 'gotomm':
            m = input("input mm from top of ticket: ")

            s = int(m) * camdata['scaler'] + camdata['ticketTop']
            print(s)
            r = write_wait_read(f'moveToStep{s}')
            if r and not 'error' in r.decode('utf-8'):
                print(f"steps from back: {r.decode('utf-8')}")
                
                t = write_wait_read('getTotalSteps')
                t = int(t.decode('utf-8'))
                camdata['stepsFromBack'] = int(r.decode('utf-8'))
                if t:
                    camdata['totalSteps'] = t
                    camdata['stepsFromFront'] = t-camdata['stepsFromBack']
                saveCamData()
                    
            else:
                print(r)
        elif k == 'cs':
            setts = not setts
        elif k == 'q' : 
            os._exit(1)
while True: 
    if arduino.in_waiting > 0:
        data = arduino.read(arduino.in_waiting)
        print(data)
    #num = input("Enter a number: ") # Taking input from user 
    #value = write_read(num) 
    #print(value) # printing the value 