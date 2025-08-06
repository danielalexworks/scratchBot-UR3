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

#bottom 48 / 46
#top  16 / 12
###########################################
#----SETTINGS-----------------------------#
###########################################
debugging = False

####NEED TO SET FOR EACH TICKET
#barcode distance on current ticket bottom right edge
#not using
poffy = 19
poffx = 29

#NEED TO SET FOR EACH TICKET TYPE
#ticket csv
scratchData = "MI6M_ticketBoxes.csv"
#offset of ticket corner bit start
offy = -32 #-56 -58
offx = -2   #-60 -73
#template barcode distance from bottom right edge
#not using
toffy = 25
toffx = 29

#NEED TO SET FOR CHANGES IN CUTTING MACHINE
#width of cutting bit in mm
bitw = 8
#overlap of cut passes TODO dial in
passOffset = 0
#zheight for scratching
scratchz = -40.7 #be mindful of helper.zoffs if changing
#how far to stop above scrathz before motor startst
zprepoffset = -2 #TODO set prep height

#ADJUSTABLE FOR PERFORMANCE
#distance between z height adjustments for inconsistnet bed height
movementResolution = 8
#TODO speed
motorSpeed = 300
travelSpeed = 200
travelSpeedCut = 100

###################################################################
###################################################################

#misc
zadj = 0
#used to estimate time scratch takes to complete
scratchTimer = 0
cnc = True
direction = 1
isMotorOn = False
isZHome = True

#set home values ( max distance to travel to get back home)
#should add limit switches to cnc machine
hx = 250
hy = 150
hz = 45 #46

#used to track distance from home in order to
# know how to get back 
# & how to get to next scratch
tx = 0
ty = 0
tz = 0

#holder for imported scratch data
scratchArea = []

#travels to an area(d) and then scratches it
# if nohome, then returns home before and after scratch
# otherwise stays in position and travels directly to next area
def goToStartingPosition(d, nohome):
    global direction
    global tx,ty,tz
    global firstScratch
    global scratchTimer
    global isZHome
    global poffx,poffy

    scratchTimer = 0
    print("-----scratch this----")
    print(d)
    if nohome == False:
        tryHome();   
    print("tx,ty,tz: " + str(tx) + ',' + str(ty) + ',' + str(tz))

    #travel distance to start of area from current position
    # value - current distance from home + offset
    mx = d[0] - tx
    my = d[1] - ty
    mx += offx # + poffx)
    my += offy #+ poffy)

    print("============STARTING")
    #2,32
    print(mx)
    print(my)

    #if firstScratch:
    #my -= bitw /2

    #Starting Position
    MoveX( mx, 'positioning');
    MoveY( my, 'positioning');
    wait();

    
    bugp('***starting position')
    #if z is home go to z start
    if isZHome:
        bugp('***inital z height')
        MoveZ( scratchz - zprepoffset) 
        isZHome = False
        wait()


def scratchIt(d, nohome = True):
    global direction
    global tx,ty,tz
    global firstScratch
    global scratchTimer
    global isZHome
    global poffx,poffy

    goToStartingPosition(d, nohome)
    #start motor and lower to cut depth
    motorOn()
    bugp('***cutting z height')
    adjustZ()
    wait()
    #MoveZ( zprepoffset )

    time.sleep(1)
    
    #scratch line 1
    bugp("initial scratch X")
    MoveX(d[2] - bitw)
    wait()

    #used to track passes to scratch entire box
    scratchH = d[3] - bitw;
    #if height of scratch box larger than width of bit
    # go back and forth to clear entire box
    firstPass = True
    bugp("SH: " + str(scratchH))
    while( scratchH > 0 or firstPass):
        bugp("while----")
        direction = -direction
        if(scratchH > bitw - passOffset):
            bugp("bitw cut")
            MoveY( -1 * (bitw - passOffset), False)
        elif firstPass:# and d[3] > d[2]:
            MoveY( -1 * (d[3]-bitw) )
        else:
            bugp(str(scratchH) + " cut")
            MoveY(-1 * (scratchH - passOffset))
        wait()
        
        bugp('X Cut')
        MoveX( (d[2]-bitw) * direction )# - (bitw * t))
        wait()

        scratchH = scratchH - bitw + passOffset
        bugp("SH: " + str(scratchH))
        time.sleep(.1)
        firstPass = False

    direction = - direction
    bugp('Go back Y cut : ' + str( ((d[3]))  -bitw ) )
    bugp(d[3])
    
    #MoveY( ((d[3] ))  -bitw )
    bugp("y done")
    wait()
    time.sleep(.5)

    #raise cutter and turn off motor
    #adjustZ()
    MoveZ(zprepoffset * -1)
    motorOff()
    wait()
    print("scratching complete")
    
    #reset direction
    direction = 1;
    
    if nohome == False:
        tryHome();

    print("timer: " + str(round(scratchTimer,2)))


#wait for current operations to complete
def wait():
    global scratchTimer
    global debugging

    print("sleep: " + str(scratchTimer/10 ))
    if not debugging:
        time.sleep(scratchTimer/10)
    scratchTimer = 0
    

def bugp(msg):
    global debugging
    if bugp:
        print(msg)
#start up cnc
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

#send gcode command to machine
def send_gcode(command):
    if debugging == False:
        # Send the G-code command to the CNC machine
        cnc.write((command + '\n').encode())  # Send the command with a newline
        cnc.flush()  # Wait for the transmission to complete
        time.sleep(0.1)  # Pause to give time for processing

        # Read and print the response from the CNC
        response = cnc.readline().decode().strip()

        if(response != 'ok'):
            print(command)
            print(f"Response: {response}")

    else:
        #print(command)
        print(command)


#formulate gcode for X movement

def MoveX(x, t = 'move'):
    global tx
    global scratchTimer

    scratchTimer += abs(x)
   
    #check direction of movement
    #set zcheck resolution accordingly
    if x < 0:
        mres = -movementResolution
        neg = True
    else:
        mres = movementResolution
        neg = False

    #forumlate gcode in increments of resolution
    #or what's left over
    #adjust speed accordingly
    #adjust Z offset after each increment
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

        if t != 'gohome' and t != 'positioning':
            adjustZ()
        send_gcode(cmd)
        x -= mres
        
#see above
def MoveY(y, t = 'move'):
    global ty
    global scratchTimer

    scratchTimer += abs(y)

    if y < 0:
        mres = -movementResolution
        neg = True
    else:
        mres = movementResolution
        neg = False

    while (neg and y < 0) or (not neg and y > 0):
        bugp("y: " + str(y))
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

        if t != 'gohome' and t != 'positioning':
            adjustZ()
        send_gcode(cmd)
        y -= mres
  

def MoveZ(z, t = 'move'):
    global tz
    global scratchTimer
    #print("tz: " + str(tz))
    z = round(z,2)
    scratchTimer += abs(z)

    cmd = "G21G91Z" + str(z) + "F"
    if t == 'cut':
        cmd += str(100)
    else:
        cmd += str(600)

    send_gcode(cmd)
    tz = round(z + tz,2);
    #print("tz: " + str(tz))


def adjustZ():
    global scratchZ
    global zadj,tx,ty,tz
    global offx,offy

    '''
    zshift = helpers.getZoff(tx, ty, offx, offy, tz)
    zshift = zshift - zadj 
    zadj = zadj + zshift
    zadj = round(zadj, 2)
    zshift = round(zshift, 2)
    '''
    #print("adj tz: " + str(tz))
    targetZ = helpers.getZoff(tx, ty, offx, offy, tz)
    zshift = tz - targetZ
    #print("zadj:" + str(zadj))
    #print("zshift:" + str(zshift))
    if(zshift != 0):
        bugp("zadjust--")
        MoveZ(-zshift)

def motorOn(): 
    global isMotorOn
    isMotorOn = True
    send_gcode("M3 S" + str(motorSpeed))

def motorOff():
    global isMotorOn
    isMotorOn = False
    send_gcode("M5")

#move motors back to starting position 
#based on distance traveled in last move
def tryHome():
    global tx,ty,tz, firstScratch
    global isZHome

    firstScratch = True
    wait()
    print("tx,ty,tz: " + str(tx) + ',' + str(ty) + ',' + str(tz))
   
    #if there is distance from home, move back that distance
    if(abs(tx) + abs(tz) + abs(ty) > 0):
        print("trying to go home: YES")
        if tz and not isZHome:
            MoveZ(-tz)
            tz = 0
            isZHome = True
        if tx:
            MoveX(-tx, 'gohome')
            tx = 0
        if ty:
            MoveY(-ty, 'gohome')
            ty = 0
    else:
        print("try go home: NO")

#make motors all travel max distance to put at home position
def forceHome():
    global firstScratch
    global isZHome

    motorOff()
    MoveZ(hz)
    MoveX(hx)
    MoveY(hy)
    tx = 0
    ty = 0
    tz = 0
    isZHome = True
    firstScratch = True


#read scratch data from csv
def gatherScratchData(filename):


    l = []
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for r in reader:
            r[1] = -1 * int(r[1])
            r[0] = -1 * int(r[0])
            l.append([int(i) if idx != 4 else i for idx, i in enumerate(r)])
    return l


#scracth every area, choosen at random
def doAllRandom(areas):
    global firstScratch

    #make a list of all scratch areas
    remaining = list(range(0,len(areas)))

    #choose a random area,
    #scratch it
    #remove it from remaining, until remaining is empty
    #sleep may need to be adjusted, seems like a good number, though
    while len(remaining):        
        num = random.choice(remaining)
        print("========== Cutting # ::: " + str(num) + " ::: ==========")
        scratchIt(areas[num])
        wait()
        remaining.remove(num)
        #print(remaining)
        #time.sleep(scratchTimer/10 + 4)
        time.sleep(10)
        firstScratch = False

    tryHome()

#debugging = True
def scratchAllInOrder(areas):
    global firstScratch

    #make a list of all scratch areas
    remaining = list(range(0,len(areas)))

    #choose a random area,
    #scratch it
    #remove it from remaining, until remaining is empty
    #sleep may need to be adjusted, seems like a good number, though
    for num in range(0,len(areas)):
        print("========== Cutting # ::: " + str(num) + " ::: ==========")
        scratchIt(areas[num])
        wait()
        time.sleep(scratchTimer/10 + 4)
        #time.sleep(10)
        firstScratch = False

    tryHome()


def printHelp():
    print("---VALID COMMANDS---")

    commands = [
        ("x :","jog 10 on x-axis"),
        ("y :","jog 10 on y-axis"),
        ("z :","jog 1 on z-axis"),
        #("d :","change jog direction"),
        ("t :","try to go home (retrace stored steps to return home)"),
        ("r :","force return home (travel max distance to ensure home return)"),
        ("m :","turn cutting motor on / off"),
        #(f"1-{len(scratchArea)} :", "scratch ticket at area id"),
        ("s :", f"prompt input for scratch id 1-{len(scratchArea)}"),
        ("b :", "reset travel distance (rezero)"),
        ("h :","print this message"),
        ("a :", "scratch all in random order"),
        ("o :", "scratch all in order"),

        ("esc :","close program")
    ]
    col_width = max(len(row[0]) for row in commands) + 3

    for row in commands:
        print(f"{row[0]:<{col_width}} {row[1]}")

def testFun(a):
    print("THIS IS A TEST " + a )
## PROGRAM START ##

#debugging = True
#TODO might want to put instead scratch function 
#calculate offset for specific ticket
poffy = toffy - poffy
poffx = toffx - poffx
print("POFFS==============")
print(poffy)
print(poffx)

scratchArea = gatherScratchData(scratchData)

# Initialize CNC connection
initialize_cnc()
firstScratch = True



while True:
    print('command:', end=' ', flush=True)
    
    k = keyboard.read_key() 
    print(k)
    
    if k == 'x':
        MoveX(10)
    elif k == 'y':
        MoveY(10)
    elif k == 'z':
        MoveZ(1)
    elif k == 't':
        tryHome()
    elif k == 'r':
        forceHome()
    elif k == 'm':
        if isMotorOn:
            motorOff()  
        else:
            motorOn()      
    elif k == 'esc':
        exit()
    elif k == 'b':
        scratchBox()
    elif k == 'h':
        printHelp()
    elif k == 's':
        time.sleep(0.2)
        k2 = input('id:')
        if ((int(k2) or k2 == '0') and int(k2) >= 0) and int(k2) < len(scratchArea):
            scratchIt(scratchArea[int(k2)])
            firstScratch = False

    elif k == 'b':
        tz = 0
        ty = 0
        tx = 0
    elif k == 'a':
        doAllRandom(scratchArea)
    elif k == 'o':
        scratchAllInOrder(scratchArea)
    else:
        print("invalid command - try h for help")

    time.sleep(.2)

cnc.close()

