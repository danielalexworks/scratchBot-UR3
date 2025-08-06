import serial
import time
import math
import keyboard
import csv
import os
import sys
import random
import threading
import json

import CNC
import helpers
import programs
import threadManager

##+++++++++++++++++++++++++++++++++++TODO
#install limit switches

#TODO make start unpause program instead of restareting

#TODO make pause only pause program and not manual actions
#TODO limit commands that can be sent during program / during pause
#TODO fix if debugging changed in UI

#bottom 48 / 46
#top  16 / 12
###########################################
#----SETTINGS-----------------------------#
###########################################
settings = {}
debugging = 1

####NEED TO SET FOR EACH TICKET
#barcode distance on current ticket bottom right edge
#not using
poffy = 19
poffx = 29

port = "COM9"

defaultProgram = "numbers before prizes"
#defaultProgram = 'all'
#NEED TO SET FOR EACH TICKET TYPE
#ticket csv
scratchData = "MI6M_ticketBoxes.csv"
scratchData = "testTicket.csv"
#offset bit to corner of board
etbx = 6
etby = 8
#offset of ticket to back corner of board
offy = -40 #-56 -58
offx = 0   #-60 -73
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
direction = 1
isMotorOn = False
isZHome = True

programStatus = 'ready'
endNow = False



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
#_________________#
#    SETTINGS     #
#_________________#
def getSettingsData():
    #print("SETTINGS")
    #print(settings)
    return settings

def initializeSettings():
    global settings
    settings['debugging'] = {'value':debugging, 'type':'bool'}
    settings['scratchData'] = {'value':scratchData, 'type':'select',
        'options':['MI6M_ticketBoxes.csv','testTicket.csv']}
    settings['offy'] = {'value':offy, 'type':'float'}
    settings['offx'] = {'value':offx, 'type':'float'}
    settings['bitw'] = {'value':bitw, 'type':'float'}
    settings['passOffset'] = {'value':passOffset, 'type':'float'}
    settings['scratchz'] = {'value':scratchz, 'type':'float'}
    settings['zprepoffset'] = {'value':zprepoffset, 'type':'float'}
    settings['movementResolution'] = {'value':movementResolution, 'type':'float'}
    settings['motorSpeed'] = {'value':motorSpeed, 'type':'int'}
    settings['travelSpeed'] = {'value':travelSpeed, 'type':'int'}
    settings['travelSpeedCut'] = {'value':travelSpeedCut, 'type':'int'}
    settings['scratchOrder'] = {'value':defaultProgram, 'type':'select', 
        'options':['random', 'numbers before prizes', 'all']
        }
    settings['port'] = {'value':port, 'type':'string'}
    settings['status'] = {'value':programStatus, 'type':'status'}
    settings['filterIds'] = {'value':'', 'type':'string'}

def updateSettings(d):
    global cnc

    for k,v in d.items():
        setSett(k,v)

    if 'debugging' in d.keys():
        cnc = 0
        CNC.initialize_cnc()

def getSett(d):
    return settings[d]['value'];
def setSett(d, v):
    global settings
    settings[d]['value'] = v
#_________________#


#travels to an area(d) and then scratches it
# if nohome, then returns home before and after scratch
# otherwise stays in position and travels directly to next area
def goToStartingPosition(d, nohome):
    global direction
    global tx,ty,tz
    global firstScratch
    global scratchTimer
    global isZHome


    scratchTimer = 0
    print("-----scratch this----")
    print(d)
    if nohome == False:
        tryHome();   
    #print("tx,ty,tz: " + str(tx) + ',' + str(ty) + ',' + str(tz))

    #travel distance to start of area from current position
    # value - current distance from home + offset
    mx = d[0] - tx
    my = d[1] - ty
    mx += getSett('offx') + etbx# + poffx)
    my += getSett('offy') + etby#+ poffy)

    #print("============STARTING")
    #2,32
    #print(mx)
    #print(my)

    #if firstScratch:
    #my -= bitw /2

    #Starting Position
    tx, tz, scratchTimer = CNC.MoveX(cnc, mx, tx, tz, scratchTimer, 'positioning');
    ty, tz,scratchTimer = CNC.MoveY(cnc, my, ty, tz, scratchTimer, 'positioning');
    wait();

    
    bugp('***starting position')
    #if z is home go to z start
    if isZHome:
        bugp('***inital z height from HOME')
        tz, scratchTimer, isZHome = CNC.MoveZ(cnc, getSett('scratchz') - getSett('zprepoffset'), tz, scratchTimer ) 
        isZHome = False
        wait()

    #print("tx,ty,tz: " + str(tx) + ',' + str(ty) + ',' + str(tz))


def scratchOutline(d):
    global tx,ty,tz
    global scratchTimer
    global isMotorOn

    bugp("---scratch OUTLINE---")
    CNC.motorOn(cnc)
    isMotorOn = True
    bugp('***cutting z height')
    adjustZ('prep')
    #wait()

    #time.sleep(.5)

    tx, tz, scratchTimer = CNC.MoveX(cnc, d[2] - getSett('bitw'), tx, tz, scratchTimer)
    #wait()

    ty, tz,scratchTimer = CNC.MoveY(cnc,  -1 * (d[3]- getSett('bitw')), ty, tz, scratchTimer )
    #wait()

    tx, tz, scratchTimer = CNC.MoveX(cnc, -1 * (d[2] - getSett('bitw')), tx, tz, scratchTimer)
    #wait()

    ty, tz,scratchTimer = CNC.MoveY(cnc, (d[3]- getSett('bitw')), ty, tz, scratchTimer )
    #wait()

    #time.sleep(.5)

    #raise cutter and turn off motor
    #tz, scratchTimer, isZHome = CNC.MoveZ(cnc, getSett('zprepoffset') * -1, tz, scratchTimer)
    #CNC.motorOff(cnc)
    #wait()
    #print("scratching OUTLINE complete")




def scratchIt(d, nohome = True):
    global direction
    global tx,ty,tz
    global firstScratch
    global scratchTimer
    global isZHome
    global poffx,poffy

    print('+++++++++++++++++++++++++++++++++++++++++||')
    print('CUTTING AREA _______________________________' + str(d[5]) + " : " + str(d[8]))
    print('+++++++++++++++++++++++++++++++++++++++++||')

    goToStartingPosition(d, nohome)

    #scratch Outline of scratch area
    scratchOutline(d)    

    #start motor and lower to cut depth if motor isn't already cutting
    if not isMotorOn:
        CNC.motorOn(cnc)
        bugp('***cutting z height')
        adjustZ('prep')
        #wait()
        #MoveZ( zprepoffset )

        #time.sleep(.5)
        
    #scratch line 1
    bugp("initial scratch X")
    tx, tz, scratchTimer = CNC.MoveX(cnc, d[2] - getSett('bitw'), tx, tz, scratchTimer)
    #wait()

    #used to track passes to scratch entire box
    scratchH = d[3] - getSett('bitw');
    #if height of scratch box larger than width of bit
    # go back and forth to clear entire box
    firstPass = True
    bugp("SH: " + str(scratchH))
    while( scratchH > 0 or firstPass):
        bugp("while----")
        direction = -direction
        if(scratchH > getSett('bitw') - getSett('passOffset')):
            bugp("bitw cut")
            ty, tz,scratchTimer = CNC.MoveY(cnc,  -1 * (getSett('bitw') - getSett('passOffset')), ty, tz, scratchTimer, False)
        elif firstPass:# and d[3] > d[2]:
            ty, tz,scratchTimer = CNC.MoveY(cnc,  -1 * (d[3]- getSett('bitw')), ty, tz, scratchTimer )
        else:
            bugp(str(scratchH) + " cut")
            ty, tz,scratchTimer = CNC.MoveY(cnc, -1 * (scratchH - getSett('passOffset')), ty, tz, scratchTimer)
        #wait()
        
        bugp('X Cut')
        tx, tz, scratchTimer = CNC.MoveX(cnc,  (d[2] - getSett('bitw')) * direction ,tx, tz, scratchTimer)
        #wait()

        scratchH = scratchH - getSett('bitw') + getSett('passOffset')
        bugp("SH: " + str(scratchH))
        #time.sleep(.1)
        firstPass = False

    direction = - direction
    bugp('Go back Y cut : ' + str( ((d[3]))  - getSett('bitw') ) )
    bugp(d[3])
    
    #MoveY( ((d[3] ))  -bitw )
    bugp("y done")
    #wait()
    #time.sleep(.5)

    #raise cutter and turn off motor
    #adjustZ()
    tz, scratchTimer, isZHome = CNC.MoveZ(cnc, getSett('zprepoffset') * -1, tz, scratchTimer)
    CNC.motorOff(cnc)
    wait()
    #print("scratching complete")
    
    #reset direction
    direction = 1;
    
    if nohome == False:
        tryHome();

    #print("timer: " + str(round(scratchTimer,2)))


#wait for current operations to complete
def wait(t = False):
    global scratchTimer

    if t:
        scratchTimer = t

    #print("sleep: " + str(scratchTimer/10 ))
    if not debugging:
        time.sleep(scratchTimer/10)
    scratchTimer = 0




def bugp(msg):

    if False:
        print(msg)




def moveX(num):
    global tx, tz, scratchTimer
    tx, tz, scratchTimer = CNC.MoveX(cnc, num, tx, tz, scratchTimer)
def moveY(num):
    global ty, tz,scratchTimer
    ty, scratchTimer = CNC.MoveY(cnc, num, ty, tz, scratchTimer)
def moveZ(num):
    global tz, scratchTimer, isZHome
    tz, scratchTimer, isZHome = CNC.MoveZ(cnc, num, tz, scratchTimer)

def adjustZ(mode = False):
    global tz,scratchTimer, isZHome

    targetZ = helpers.getZoff(tx, ty, getSett('offx')+etbx, getSett('offy')+etby, tz)
    zshift = round(tz - float(targetZ),2)
   
    #if move is to prep for cutting, zshift the motor in place
    #else return shift value (False if no adjustment necessary)
    bugp("zadjust--  :  " + str(zshift))
    if mode == 'prep':
        tz, scratchTimer, isZHome = CNC.MoveZ(cnc, -zshift, tz, scratchTimer)
    else:
        return -zshift
  


def toggleMotor():
    global isMotorOn
    if isMotorOn:
        isMotorOn = CNC.motorOff(cnc)  
    else:
        isMotorOn = CNC.motorOn(cnc) 




#move motors back to starting position 
#based on distance traveled in last move
def tryHome():
    global tx,ty,tz, firstScratch, scratchTimer
    global isZHome

    firstScratch = True
    wait()
    #print("tx,ty,tz: " + str(tx) + ',' + str(ty) + ',' + str(tz))
   
    #if there is distance from home, move back that distance
    if(abs(tx) + abs(tz) + abs(ty) > 0):
        #print("trying to go home: YES")
        if abs(tz) and not isZHome:
            tz, scratchTimer, isZHome = CNC.MoveZ(cnc, -tz, tz, scratchTimer)
            tz = 0
            isZHome = True
        if abs(tx):
            tx, tz, scratchTimer = CNC.MoveX(cnc, -tx, tx, tz, scratchTimer, 'gohome')
            tx = 0
        if abs(ty):
            ty, tz,scratchTimer = CNC.MoveY(cnc, -ty, ty, tz, scratchTimer, 'gohome')
            ty = 0
        return "returned home"
    else:
        #print("try go home: NO")
        return "already home"


#make motors all travel max distance to put at home position
def forceHome():
    global firstScratch
    global isZHome, scratchTimer
    global tx,ty,tz

    CNC.motorOff(cnc)
    tz, scratchTimer, isZHome = CNC.MoveZ(cnc, hz,tz,scratchTimer, 'gohome')
    tx, tz, scratchTimer = CNC.MoveX(cnc, hx,tx,tz, scratchTimer, 'gohome')
    ty, tz, scratchTimer = CNC.MoveY(cnc, hy,ty, tz, scratchTimer, 'gohome')
    tx = 0
    ty = 0
    tz = 0
    isZHome = True
    firstScratch = True
    return "forced home"

def resetZero():
    global tx,ty,tz

    tx = 0
    ty = 0
    tz = 0

#read scratch data from csv
def gatherScratchData(filename):
    l = []
    with open('scratchData/' + filename, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for r in reader:
            r[1] = -1 * int(r[1])
            r[0] = -1 * int(r[0])

            l.append([int(i) if idx not in [4,5] else i for idx, i in enumerate(r)])
    return l

def getTicketInfo():
    #print("++++++++++++++++++++++")
    t = gatherScratchData(settings['scratchData']['value'])
    #print("----")
    #print("RETURNED TICKET INFO")
    return json.dumps(t)

def getScratchedInfo():
    #print('scratch info')
    if getSett('status') in ['in progress', 'paused']:
        return programs.remaining;
    elif programs.programComplete:
        return 'ready'
    else:
        return False



def getProgramStatus():
    return programStatus
def getScratchTimer():
    return scratchTimer

def setFirstScratch(v):
    global firstScratch
    firstScratch = v

#TODO DO NOT NEED
def setProgramStatus(s):
    setSett('status',s)
    
def endProgram():
    global endNow
    endNow = True

def togglePause(status = 'none'):
    if status == 'none':
        status = getSett('status')

    if status == 'in progress':
        setSett('status','paused')
        threadManager.pauseThread()
    elif status == 'paused':
        setSett('status','in progress')
        threadManager.unpauseThread()
   
    #print('status' + getSett('status'))

def checkPause():
    threadManager.checkPause()



def startCurrentProgram():
    global scratchArea
    scratchArea = gatherScratchData(getSett('scratchData'))
    threadManager.startProgram(settings['scratchOrder']['value'], scratchArea)

    

## PROGRAM START ##
#debugging = True
#TODO might want to put instead scratch function 
#calculate offset for specific ticket
poffy = toffy - poffy
poffx = toffx - poffx
#print("POFFS==============")
#print(poffy)
#print(poffx)

initializeSettings()
#scratchArea = gatherScratchData(getSett('scratchData'))
# Initialize CNC connection
cnc = CNC.initialize_cnc()
firstScratch = True
