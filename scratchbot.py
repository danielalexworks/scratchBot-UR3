import urx
import time
import traceback
import helpers
import cobot
import settings
import programs
import threadManager
import ticket
import cameraTracker as cam


####################################################
#                                                  #
#                 TODO                             #
#                                                  #
####################################################
#make joints more ridged
#set TCP / payload
#set new positions
#figure for target force
#run force routine
#run align ticket
#text scratch

''' 
run align ticket
place ticket
check ticket with startingpose
move ticket to box 1
set offsets
test again
move ticket to box 5
move home 
ready
'''

	
#TODO get arc time

#TODO figure out whyoverscratching boxes
# bitw ? box size? accuracy? 
	
	#TEST ALL UI in PROD

	#TESTTODO estimatetime make better

														
#TODO try decreasing wait between force adjustments

	
#TODO fix UI lines when not in dbug mode

#TODO add startingPOS Routine to main program
#TODO parabolic motion	

	
							#gui 45 , make only work when ready


	

#TODO design new tool end

#TODO clear/set poses within GUI and update GUI	
			
			
#TODO make transition "animations / tricks" between boxes
	#TESTTODO make debugging switchable from front end
#TODO make settings / threads/ programs reference global programs list, rather than hard coding each one seperatly



##/????  ***trying to move: -0.02 in Z dimension

scratchyLength = 13

zPrepH = .5 
direction = 1

infile= 'poseData/cobotPos.csv'
isMotorOn = False

bumpX = 0
bumpY = 0

def shutdown():
	threadManager.stopThread()
	cobot.shutdown(rob)

def restartBot():
	global rob
	rob = cobot.initializeCobot(rob)

def moveTo(pose):
	a,v = getAV()
	print(f"a:{a} v:{v}")
	if pose in settings.getSett('poses'):

		if pose != 'startingPose':
			cobot.moveTo(rob,moves,pose,'joints',a,v)
		else:
			cobot.moveTo(rob,moves,pose,'transformations',a,v)
		
		return True
	else:
		print('||||||  FAILED TO FIND POSE  ||||||')
		return False

def getAV():
	a = settings.getSett('acceleration')
	v = settings.getSett('velocity')
	return a,v

def getSAV():
	a = settings.getSett('scratchAcceleration')
	v = settings.getSett('scratchVelocity')
	return a,v

def toggleMotor():
    if cobot.isMotorOn:
        cobot.motorOff(rob)  
    else:
        cobot.motorOn(rob) 

def togglePause(status = 'none'):
    threadManager.togglePause(status)

def setStartingPose():
	#cobot.startingPose(rob.getl())
	bugp('todo')

def setNewStartingPosition():
	global moves
	print("\n\nset new startingpose")
	cobot.setNewStartingPosition(rob, moves, infile)
	moves = cobot.getMovesFromFile(rob, infile)

def adjustStartingPose():
	global moves
	
	moves['startingPose'] = cobot.adjustStartingPose(rob,moves)
	

def adjustTCP(axis, value, direction):
	global bumpX,bumpY
	if axis == 'x':
		bumpX += (int(value) * int(direction))
	elif axis == 'y':
		bumpY += (int(value) * int(direction))

	if bumpX or bumpY:
		cobot.setBump(bumpX,bumpY)

#if zup up is called, check for manual adjustments,
#if exist, perform
def zUp(multi = 1):
	a,v = getAV()
	cobot.zUp(rob, multi)
	'''
	if bumpX or bumpY:
		print(f"BUUUUUUUUUUUUUUUMP {cobot.tx},{cobot.ty}" )
		cobot.moveXY(rob, bumpX, bumpY, a, v, 'position')
		print(f"BUUUUUUUUUUUUUUUMPED {cobot.tx},{cobot.ty}" )
		bumpX = 0
		bumpY = 0
	'''

def zDown(multi = 1):
	cobot.zDown(rob, multi)

def manualMove(d, axis):
	a,v = getAV()
	bugp(f"RT POSITION BEFORE MOVE: {cobot.getRelativePosition(rob)}")
	if axis == 'z':
		cobot.moveZ(rob, d, a, v)
	elif axis == 'y':
		cobot.moveY(rob, d, a, v, 'position')
	elif axis == 'x':
		cobot.moveX(rob, d, a, v, 'position')

	bugp(f"RT POSITION AFTER MOVE: {cobot.getRelativePosition(rob)}")

def manualRotate(d, axis):
	a,v = getAV()
	bugp('sbmr')
	cobot.manualRotate(rob,axis,d,a,v)

def enableFreeDrive(t = 20):
	if settings.getSett('status') == 'ready':
		rob.set_freedrive(True, timeout=t)
		return True
	else:
		return "error: program in progress"

def bugp(s):
	if settings.getSett('bugp'):
		print(s)

#move to ticket corner scratchposition 
#lift, get force target from lifted position
#return to scratch position, lift until target force reached again
#repeat for bottom corner
alignloc = 'tl'
def alignTicket(l):
	global alignloc
	a,v = getAV()
	print("\n\nALIGN TICKET")
	if alignloc == 'tl':
		print("\n\nalign TOP LEFT")
		moveTo('startingPose')
		#zUp()
		#targetForce = getForce()
		#time.sleep(1)
		#print(f"\n\n---0-0-0-0-0-0---TARGET FORCE: {targetForce}")
		#zDown()
		#print(f"FORCE REST : {targetForce}")
		#releaseTCPPressure()
		print("\n\n\n(((((((((((((((((((((((   )))))))))))))))))))))))")
		print("(             READY MARK ALIGN TICKET           )")
		print("(                TOP LEFT CORNER                )")
		print("(((((((((((((((((((((((   )))))))))))))))))))))))")
		alignloc = 'bl'
	else:
		zUp()
		print("\n\nalign BOTTOM LEFT")
		#zUp()
		time.sleep(1)
		cobot.moveY(rob, float(settings.getSett('ticket_height')), a, v, 'position')
		time.sleep(1)
		#targetForce = getForce()
		zDown()
		#releaseTCPPressure()
		#cobot.adjustForce(rob, targetForce = settings.getSett('forceRest'))
		print("\n\n\n(((((((((((((((((((((((   )))))))))))))))))))))))")
		print("(             READY MARK ALIGN TICKET           )")
		print("(               BOTTOM LEFT CORNER              )")
		print("(((((((((((((((((((((((   )))))))))))))))))))))))")
		alignloc = 'tl'

'''
def releaseTCPPressure():
	threshold = 10
	zUp()
	time.sleep(1)
	targetAngle = cobot.getForceAngle(rob)
	zDown()

	while abs(cobot.getForceAngle(rob) - targetAngle) > threshold:
		cobot.moveZ(rob, .2, 1, 1)
		time.sleep(0.5)
'''

#UNUSED
'''
def getForce():
	#print("------\n\n\nGETFORCE\n\n-----")
	matchTarget = 5
	matches = 0
	tightness = 3
	lastReading = 0
	while matches < matchTarget:
		r = cobot.getDebouncedForce(rob)
		#print(r)
		if abs( r - lastReading) < tightness:
			matches += 1
		else:
			matches = 0

		lastReading = r
		time.sleep(0.1)
		
	return lastReading
'''

def scratchIt(d, type='coin'):
	global direction
	bugp('\n\n\n+++++++++++++++++++++++++++++++++++++++++||')
	print(f"SCRATCHING AREA {type}_______________________________{str(d[5])} : {str(d[8])}")
	bugp('+++++++++++++++++++++++++++++++++++++++++||')
	bugp(f"gravity: {cobot.isGravity(rob)}")
	#starting the program puts cobot in startingPos
	#this puts cobot at start of actual scratch
	#if coin, this is at the corner (x, y-bw/2)
	#if dremel, (x-bw/2 , y-bw/2)
	goToScratchPosition(d, False, type)


	if(type == 'dremel'):
		#scratch Outline of scratch area
		scratchOutline(d)   
	
	
	#scratch inside of box
	
	if type =='dremel':
		scratchInterior(d)
	elif type =='coin':
		scratchInteriorCoin(d)

	

def scratchyMove(d,a,v,direction):
	sa,sv = getSAV()
	a,v = getSAV()
	bugp("\n\n||scratchy||")


	bugp(f"start: {cobot.tx},{cobot.ty}") #start: -0.078,-0.224
	#TODO shorten delay on scratchys
	numOsc = abs(int(d / (scratchyLength/2)))
	lastOsc = abs(d) - ( (numOsc-1) * (scratchyLength/2) )

	bugp(f"distance: {d}   scratchyLength: {scratchyLength}")
	bugp(f"numOsc: {numOsc}   lastOsc: {lastOsc}")

	#cobot.moveX(rob, scratchyLength * direction * 1, sa,sv)

	cobot.moveX(rob, d * direction, sa,sv)
	cobot.moveX(rob, d * direction*-1, sa,sv)
	s = 0
	#move forth and back less last
	#track until all scratched
	'''
	while s <  abs(d) - lastOsc:
		cobot.moveX(rob, scratchyLength * direction * 1, sa,sv)
		cobot.moveX(rob, scratchyLength * direction * -.5, sa,sv)
		#cobot.moveX(rob, scratchyLength * direction * -1, sa,sv)
		s += (scratchyLength * .5)

		print(f"++++++++++++++++++++++++++++++++++++++++position from start {s}")
	'''
	#cobot.moveX(rob, scratchyLength * direction * .5, sa,sv)

	bugp(f"end of regular oscillations distance traveled: {s}")
	bugp(f"left to do : {abs(d) - s} or numosc: {numOsc}")
	#if lastOsc:
	if 0:
		cobot.moveX(rob, (abs(d) - s) * direction, a,v)
		#cobot.moveX(rob, (abs(d) - s) * direction * -1, a,v)
		#cobot.moveX(rob, (abs(d) - s) * direction, a,v)
	
	bugp(f"end: {cobot.tx},{cobot.ty}") #end: -0.078,-0.212

def scratchInteriorCoin(d):
	global direction
	a,v = getSAV()

	#this should be (ticket size) - (x, y-bitw/2) 50
	bugp(f"\n\nSTARTING -- tx,ty : {cobot.tx},{cobot.ty}") #91,228
	#TODO REMOVE TEMP
	if settings.getSett('debugging'):
		#scratchOutline(d)
		bugp('scratch Outline')

	bw = settings.getSett('bitw')
	poff = settings.getSett('passOffset')
		
	zDown()
	#scratch line 1
	bugp(f"gravity: {cobot.isGravity(rob)}")
	bugp("\n\nFIRST LINE")
	scratchyMove(d[2], a, v, direction)
	bugp(f"gravity: {cobot.isGravity(rob)}")

	#if height of scratch box larger than width of bit
	# go back and forth to clear entire box
	#used to track passes to scratch entire box
	
	scratchH = d[3] - bw
	
	firstPass = True
	while( scratchH > 0 ):#or firstPass):
		#zUp(.5)
		direction = -direction
		if scratchH > bw - poff :	
			bugp("\n\nBW")		
			#cobot.moveY(rob, (bw-poff), a, v, 'position')			
			cobot.moveXYZ(rob, 0,(bw-poff),1, a, v, 'position')			
		elif firstPass:# and d[3] > d[2]:
			bugp("\n\nFIRST PASS")		
			#cobot.moveY(rob, (d[3] - bw), a, v, 'position')			
			cobot.moveXYZ(rob, 0,(d[3] - bw), 1, a, v, 'position')			
		else:
			bugp("\n\nFINAL PASS")		
			#cobot.moveY(rob, (scratchH - poff), a, v, 'position')			
			cobot.moveXYZ(rob, 0,(scratchH - poff),1, a, v, 'position')			

		zDown()
		scratchyMove((d[2]) * direction, a, v, direction)

		scratchH = scratchH - bw + poff
		firstPass = False

	bugp(f"\n\nENDING -- tx,ty : {cobot.tx},{cobot.ty}") #78, 212

	direction = - direction
	
	#raise cutter and turn off motor
	#zUp()

	#reset direction
	direction = 1


def scratchInterior(d):
	global direction
	a,v = getSAV()

	bw = settings.getSett('bitw')
	poff = settings.getSett('passOffset')

    #start motor and lower to cut depth if motor isn't already cutting
	#if not cobot.isMotorOn:
	#	toggleMotor()
	#	cobot.zDown(rob)
		
	zDown()
	#scratch line 1
	cobot.moveX(rob, d[2] - bw, a, v)

	

	#if height of scratch box larger than width of bit
	# go back and forth to clear entire box
	#used to track passes to scratch entire box
	scratchH = d[3] - bw
	firstPass = True
	while( scratchH > 0 or firstPass):

		direction = -direction
		if scratchH > bw - poff :	
			bugp("\nBW")		
			cobot.moveY(rob, (bw-poff), a, v)			
		elif firstPass:# and d[3] > d[2]:
			bugp("\nfirstpass")		
			cobot.moveY(rob, (d[3] - bw), a, v)			
		else:
			bugp("\nfinal")		
			cobot.moveY(rob, (scratchH - poff), a, v)			

		cobot.moveX(rob, (d[2] - bw) * direction, a, v)

		scratchH = scratchH - bw + poff
		firstPass = False

	direction = - direction
	
	#raise cutter and turn off motor
	zUp()
	cobot.motorOff(rob)

	#reset direction
	direction = 1
    


#travels to an area(d) and then scratches it
def goToScratchPosition(d, first=False, type='dremel'):
	#TODO REMOVE
    global direction
    global firstScratch
    global scratchTimer
    a,v = getAV()

    scratchTimer = 0
    cam.moveToMm(d[1]+d[3])
    time.sleep(2)

    #zUp()
    bugp(f"gravity: {cobot.isGravity(rob)}")


    #travel distance to start of area from current position
    # value - current distance from home + offset
    # center to center

    #adjustments may need to happen inside this??

    #mx,my = cobot.get2DTravelDistance(d)
    relPos = cobot.getRelativePosition(rob)
    bugp(f"\n\nRT POSITION BEFORE MOVE: {relPos}")
    mx,my = cobot.get2DTravelDistance(d, relPos)


    #mx,my = adjustForOffset(mx,my)
    #adjust for bitwidth if moving from home position. Otherwise, movement is relative, so shouldn't need to adjust.
    if cobot.tx == 0 and cobot.ty == 0:
    	mx,my = adjustForBitWidth(mx,my,.5,type)
    else:
    	mx,my = adjustForBitWidth(mx,my,.5,type)


    bugp(f"currentPosition (tx,ty): {cobot.tx*1000},{cobot.ty*1000}")
    bugp(f"GO TO POS (box): {d[0], d[1]}")
    bugp(f"travel adjusted: {mx} , {my}")
    bugp(f"bump adjusted: {mx+bumpX}, {my+ bumpY}")

    mx += bumpX
    my += bumpY

    #SPLIT
    #Starting Position
    #cobot.moveX(rob, mx, a, v, 'position')
    #cobot.moveY(rob, my, a, v, 'position')
    #TOGETHER
 	#cobot.moveXY(rob,mx,my,a,v,'position')
    #cobot.moveXYZ(rob,mx/2,my/2, 1 ,a,v,'position')

    '''
    #PROD VERSION
    if cobot.iszup:
    	cobot.moveXYZ(rob,mx,my, -1 ,a,v,'position')
    else:
    	cobot.moveXYZ(rob,mx,my, 1 ,a,v,'position')
    '''


    #EXPERIMENTAL
    zDown()

    cobot.moveArc(rob, mx,my,a,v,'position')

    #cobot.moveXYArc(rob,mx,my,a,v,'position')
    bugp(f"RT POSITION AFTER MOVE: {cobot.getRelativePosition(rob)}\n\n")


def adjustForOffset(x,y):
	offx = settings.getSett('offx')
	offy = settings.getSett('offy')

	return x + offx , y + offy

def adjustForBitWidth(x,y,percent = 1, type='dremel'):
	bw = settings.getSett('bitw')
	y = y+(bw*percent)
	if type == 'dremel':
		x = x+(bw*percent)

	return x, y

def scratchOutline(d):
    global scratchTimer
    global isMotorOn
    a,v = getSAV()

    bw = settings.getSett('bitw')

    #bugp("---scratch OUTLINE---")
    cobot.motorOn(rob)

    zDown()

    #time.sleep(.5)
    bugp(f"d2 - bw : {d[2]} - {bw} = {d[2]-bw}")
    cobot.moveX(rob, (d[2] - bw), a, v)

    cobot.moveY(rob, (d[3] - bw), a, v)

    cobot.moveX(rob, -1*(d[2] - bw), a, v)


    cobot.moveY(rob, -1* (d[3] - bw), a, v)

    #cobot.zUp(rob)

    #zUp()


    #time.sleep(.5)

    #raise cutter and turn off motor
    #tz, scratchTimer, isZHome = CNC.MoveZ(cnc, getSett('zprepoffset') * -1, tz, scratchTimer)
    #CNC.motorOff(cnc)
    #wait()
    #print("scratching OUTLINE complete")


def estimateTime():
	cobot.estimateTime = True
	cobot.estimatedTime = 0
	programs.startCurrentProgram()
	while cobot.estimateTime:
		pass

	print(f"\r\n\r\n\r\nTIME: {cobot.estimatedTime} seconds or {cobot.estimatedTime/60} minutes\r\n\r\n")
	return round(cobot.estimatedTime/60)




def moveToBox(box):
	areas = ticket.gatherScratchData(settings.getSett('scratchData'))
	
	bugp(areas)
	#zUp()
	moveTo('startingPose')
	#zUp()
	goToScratchPosition(areas[int(box) - 1])
	zDown()

def scratchABox(box):
	areas = ticket.gatherScratchData(settings.getSett('scratchData'))
	bugp(areas)
	moveTo('startingPose')
	scratchIt(areas[int(box)-1])
	moveTo("home")

def getMovesFromFile():
	global moves
	moves = cobot.getMovesFromFile(rob,infile)

####################################################
#                                                  #
#                 PROGRAM START                    #
#                                                  #
####################################################
firstScratch = True

settings.initializeSettings()
rob = cobot.initializeCobot()
if settings.getSett('activeCamera'):
	cam.initCamera()
	
#rob.send_program("popup(9)")
#time.sleep(2)
getMovesFromFile()

#if cobot.getCurrentPose(rob, moves, threshold=.02) != 'startingPos':
#	cobot.moveTo(rob,moves, 'startingPose', 'joints', a,v)
	

#move in box
#cobot.moveX(rob, .01, .1, .1)
#cobot.moveY(rob, .01, .1, .1)
#cobot.moveX(rob, -.01, .1, .1)
#cobot.moveY(rob, -.01, .1, .1)

#cobot.moveTo(rob,moves, 'home', 'joints', a,v)
#time.sleep(5)



#cobot.shutdown(rob)
