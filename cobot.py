import urx
import time
import csv
import os
import traceback
import math
import settings
import json
import frame
import math3d
import numpy as np
import copy
#import draw

scratchTimer = 0
tx = 0
ty = 0
tz = 0


isMotorOn = False
iszup = False 
travelZHeight = 10 #mm

cutlines = []

startingPose = []
originalStartingPose = {}

estimateTime = False
estimatedTime = 0

bumpX = 0
bumpY = 0

def bugp(s):
    if settings.getSett('bugp'):
        print(s)

def setBump(x,y):
    global bumpX,bumpY
    bumpX += (x/1000.00)
    bumpY += (y/1000.00)

def setPayload(bot, loaded = False):
    addedForce = .5635
    if not settings.getSett('debugging'):
        p = settings.getPayload()
        p['x'] = round(p['x'] / 1000, 6)
        p['y'] = round(p['y'] / 1000, 6)
        p['z'] = round(p['z'] / 1000, 6)
        if loaded:
            bot.set_payload(p['weight'] + addedForce, (p['x'],p['y'],p['z']) )
        else:
            bot.set_payload( p['weight'], (p['x'],p['y'],p['z']) )


#CONNECT TO COBOT THROUGH ETHERNET
def initializeCobot(bot = False):
    print(f"botob {bot}")
    if bot:
        bot.send_program("set_tool_voltage(0)")
        bot.stop()
        print('stopping cobot')
        bot.close()

    if not settings.getSett('debugging'):
        cnt = 0

        while cnt < 10:
            try:
                tcp = settings.getTCP()
                
                tcp['x'] = round(tcp['x'] / 1000, 6)
                tcp['y'] = round(tcp['y'] / 1000, 6)
                tcp['z'] = round(tcp['z'] / 1000, 6)
               
                print('...trying to start bot...')
                rob = urx.Robot(settings.getSett('ip'), True)    
                time.sleep(.5)
                #lil marker
                #rob.set_tcp((0, 62/1000, 99.3/1000 , 0.349, 0, 0))
                #pencil
                rob.set_tcp( (tcp['x'], tcp['y'], tcp['z'] , tcp['rx'], tcp['ry'], tcp['rz']) )
                setPayload(rob, False)
                #rigidcoin
                #rob.set_tcp((0, 0, 142/1000 , 0, 0, 0))
                #probe
                #rob.set_tcp((66/1000, 0, 118/1000 , 0, 0,0.174))

                print('tcp set')     
                print('payload set')
                time.sleep(0.2)
                print(" .---.  .----. .----.  .----.  .---.    .-..-. .-..-. .---. .-.  .--.  .-.   .-. .---. .----..----. ")
                print("/  ___}/  {}  \\| {}  }/  {}  \\{_   _}   | ||  `| || |{_   _}| | / {} \\ | |   | |{_   / | {_  | {}  \\")
                print("\\     }\\      /| {}  }\\      /  | |     | || |\\  || |  | |  | |/  /\\  \\| `--.| | /    }| {__ |     /")
                print(" `---'  `----' `----'  `----'   `-'     `-'`-' `-'`-'  `-'  `-'`-'  `-'`----'`-' `---' `----'`----' ")

                print(rob)
                if settings.getSett('poweredTool'):
                    rob.send_program("set_tool_voltage(12)")
                time.sleep(1)
                print(rob)

                return rob


            except Exception as e:

                traceback.format_exc()
                cnt += 1
                print(f"fail {cnt}")
                time.sleep(1)

        if cnt == 5 :
            print('failed to connect')
            os._exit(1)
    else:
        print(".----. .----..----. .-. .-. .---.  .---. .-..-. .-. .---. ")
        print("| {}  \\| {_  | {}  }| { } |/   __}/   __}| ||  `| |/   __}")
        print("|     /| {__ | {}  }| {_} |\\  {_ }\\  {_ }| || |\\  |\\  {_ }")
        print("`----' `----'`----' `-----' `---'  `---' `-'`-' `-' `---' ")
        return False



def wait(bot):
    global estimatedTime
    global scratchTimer
    time.sleep(1)
    #print(f"timer: {scratchTimer}")
    #if not settings.getSett('debugging'):
    if not estimateTime and not settings.getSett('debugging'):
        time.sleep(scratchTimer *1.4)
    elif estimateTime:
        estimatedTime += (scratchTimer *1.4)

    scratchTimer = 0
    
def waitForPose(bot, targetPose , it = .01, allt = .01):
    while True:
        currentPose = bot.getl()
        dx = abs(targetPose[0] - currentPose[0])
        dy = abs(targetPose[1] - currentPose[1])
        dz = abs(targetPose[2] - currentPose[2])

        bugp(f"diff: {dx},{dy},{dz}")
        if dx+dy+dz < allt:
            bugp("DONE MOVING")
            return True

def waitForTranslation(bot, cpos, tpos, it = 0.1, allt = .01):
    while True:
        now = bot.getl()
        dx = abs(cpos[0] + tpos[0] - now[0])
        dy = abs(cpos[1] + tpos[1] - now[1])
        dz = abs(cpos[2] + tpos[2] - now[2])

        bugp(f"diff: {dx},{dy},{dz}")
        if dx+dy+dz < allt:
            bugp("DONE MOVING")
            return True



#shutdown connection and end python program
def shutdown(bot):
    if bot:
        bot.send_program("set_tool_voltage(0)")
        bot.stop()
        print('stopping cobot')
        bot.close()
    
    print('robot shutdown')
    os._exit(1)

#gather named positions created from running cobotPositionGrabber.py
def getMovesFromFile(bot,filename):
    global startingPose
    global originalStartingPose

    moves = {}
    poses = []
    with open(filename, newline ='') as f:
        reader = csv.reader(f)
        labels = next(reader) 
        row = 0
        for r in reader:
            moves[r[0]] = {
             labels[1].strip(): list(map(float, r[1].strip('[]').split(','))),
             labels[2].strip(): list(map(float, r[2].strip('[]').split(',')))
            }
            poses.append(r[0])

        bugp(f"MOVE BEFORE ZTRANS : {moves}")
        #TODO NO LONGER USING ALIGNER
        originalStartingPose = copy.deepcopy(moves['startingPose'])
        print(f"op {originalStartingPose['transformations']}")
        moves['startingPose'] = getAlignerTranslatedPose(bot, moves['startingPose'])
        print(f"op {originalStartingPose['transformations']}")
        print(f"mspp {moves['startingPose']['transformations']}")
        startingPose = moves['startingPose']


    #print(f"MOVE AFTER ZTRANS : {moves}")
    settings.setPossiblePoses(poses)
    return moves


def rotateTool():
    bugp('rotatetool')


#move to named positions created from running cobotPositionGrabber.py
def moveTo(bot, moves, label, space='transformations', a = .1, v = .1):
    global tx,ty,tz
    bugp(bot)

    if getCurrentPose(bot, moves, 0.03) == label:
        bugp(f"**POSITION aleady at {label}")
    else:
        bugp(f"**MOVING TO {label}**")
        if not settings.getSett('debugging'):
            if space == 'transformations':
                prgstr = "movej(p"
                prgstr += str(moves[label]['transformations'])
                prgstr += f", a={a}, v={v}, r=0)"
                if not estimateTime:
                    bot.send_program(prgstr)
                addToScratchTimer(getPoseMovementTime(bot, moves[label]['joints'], a, v))
            elif space == 'joints':
                if not estimateTime:
                    bot.movej(moves[label][space], wait=False, acc = a, vel = v)
                addToScratchTimer(getPoseMovementTime(bot, moves[label][space], a, v))

            if label == 'startingPose':
                tx = 0
                ty = 0
                tz = 0
        elif settings.getSett('debugging'):
            addToScratchTimer(5) #estimate move to Pose time if debugging and cannot get actual bot position

        wait(bot)

        #waitForPose(bot, moves[label]['transformations'])


    #input()
#checks current position against named positions created from running cobotPositionGrabber.py
#returns named position or False if no matching position found within threshold
def getCurrentPose(bot, moves, threshold = .03):
    bugp(f"moves: {moves}")
    if not settings.getSett('debugging'):
        c = bot.getl()
        
        labels = list(moves.keys())

        for l in labels:
            bugp(l)
            for val1, val2 in zip(c, moves[l]['transformations']):
                diff = abs(val1 - val2)
                if diff > threshold:
                    break

            else:
                bugp(f"CURRENT POSITION: {l}")
                return l

        else:
            return False #maybe return c. instead?
    else:
        bugp("debug--Get Current Position")
        return False



#tx,ty are the position of the TCP in relation to start point
def get2DTravelDistance(toxy, fromxy = False):
    global tx,ty
    # /100 to translate to mm for urx
    #ox = settings.getSett('offx')
    #oy = settings.getSett('offy')
    #bw = settings.getSett('bitw')

    #if not passing a second point, use the current stored position of the tool relative to the starting point
    if not fromxy:
        fromxy = [tx,ty]

    mx = toxy[0] - (round(fromxy[0],6)*1000)
    my = toxy[1] - (round(fromxy[1],6)*1000)
    #mx =   (t[0]*1000) - f[0]
    #my =   (t[1]*1000) - f[1]
    bugp(f"2D x {toxy[0]} - {fromxy[0]*1000} = {mx}")
    bugp(f"2D y {toxy[1]} - {fromxy[1]*1000} = {my}")
    
    print(f"GOTO -------- - - -- -- - - - -- - - -- -- {round(mx,2)},{round(my,2)}")
    return round(mx,2),round(my,2)

def get2DTravelDistanceOLD(f, t = False):
    global tx,ty
    # /100 to translate to mm for urx
    #ox = settings.getSett('offx')
    #oy = settings.getSett('offy')
    #bw = settings.getSett('bitw')

    #if not passing a second point, use the current stored position of the tool relative to the starting point
    if not t:
        t = [tx,ty]

    mx = f[0] - (t[0]*1000)
    my = f[1] - (t[1]*1000)
    #mx =   (t[0]*1000) - f[0]
    #my =   (t[1]*1000) - f[1]
    #print(f"2D x {f[0]} - {t[0]*1000} = {mx}")
    #print(f"2D y {f[1]} - {t[1]*1000} = {my}")
    
    bugp(f"GOTO -------- - - -- -- - - - -- - - -- -- {round(mx,3)},{round(my,3)}")
    return round(mx,3),round(my,3)


def zUp(bot, multi = 1,a = .5, v=.5):
    global iszup
    if not iszup:
        bugp("ZUP")
        moveZ(bot, travelZHeight * multi, a,v)
        iszup = True
        setPayload(bot, False)
    else:
        bugp('already ZUP')

def zDown(bot, multi = 1,a = .5, v=.5):
    global iszup
    if iszup:
        bugp("ZDOWN")
        moveZ(bot,  -1*travelZHeight * multi, a,v)
        iszup = False

        setPayload(bot,True)
       
    else:
        bugp("already ZDOWN")


def manualRotate(bot, axis,d,a,v):
    bugp('cb mr')
    pose = bot.get_pose()
    bugp(f"pose {pose}")
    if axis == 'x':
        pose.orient.rotate_xb(math.radians(d))
    elif axis == 'y':
        pose.orient.rotate_yb(math.radians(d))
    elif axis == 'z':
        pose.orient.rotate_zb(math.radians(d))

    else:
        p = settings.getSett('threePoints')
        normal = frame.computeNormal(p[0],p[1],p[2])

        
        z_axis = np.array([0, 0, 1])  # The default Z-axis
        axis_of_rotation = np.cross(z_axis, normal)
        axis_of_rotation = axis_of_rotation / np.linalg.norm(axis_of_rotation)  # Normalize

        # Step 5: Calculate the angle between the Z-axis and the normal vector
        dot_product = np.dot(z_axis, normal)
        angle = np.arccos(dot_product)  # This gives the angle in radians

        # Step 6: Manually create a quaternion from the axis and angle
        half_angle = angle / 2.0
        sin_half_angle = np.sin(half_angle)

        # Quaternion components: [cos(θ/2), sin(θ/2) * axis_x, sin(θ/2) * axis_y, sin(θ/2) * axis_z]
        qw = np.cos(half_angle)
        qx, qy, qz = axis_of_rotation * sin_half_angle

        # Create the quaternion
        rotation_quaternion = math3d.Quaternion(qw, qx, qy, qz)

        # Step 7: Apply the quaternion to the current pose orientation
        # Assuming 'pose.orient' is an instance of math3d.Orientation

        # Convert quaternion to orientation using set_quaternion
        new_orientation = math3d.Orientation()
        new_orientation.set_quaternion(rotation_quaternion)

        # Step 8: Apply the new orientation to pose.orient
        pose.orient = new_orientation  #



        #euler_angles = pose.orient.to_euler("xyz")
        #new_orientation = math3d.Orientation.new_from_euler([euler_angles[0], euler_angles[1], 0])

        #pose.orient = new_orientation

    bugp(f"pose {pose}")
    bot.set_pose(pose)


#linear tool move on x axis distance, acceleration, velocity
def moveX(bot, d, a, v, t = 'cut'):
    global tx, estimatedTime
    global bumpX
    d = d/1000.00 # /100 to translate to mm for urx
    if t == 'cut':
        #print("\r\n\r\n")
        adjustForce(bot)
        addLine(d, 0)
        
        #addLine(0, 0, d, 0)

    bugp(f"tx : {tx} -> {tx + d}")
    tx += d + bumpX
    tx = round(tx,6)

    bugp(f"***trying to move: {d} in X dimension")
    d += bumpX
    bumpX = 0
    if not settings.getSett('debugging'):
        if not estimateTime:
            time.sleep(0.1)
            bot.translate(changePlane((-1 * d,0,0)), acc=a, vel=v, wait=False)

    if estimateTime:
        estimatedTime += .1
    addToScratchTimer(getLinearMoveTime(bot, [0,0,0], [-1*d,0,0], a, v))
    wait(bot)


def moveY(bot, d, a, v,  t = 'cut'):
    global ty, estimatedTime
    global bumpY
    d = d/1000.00 # /100 to translate to mm for urx

    if t == 'cut':
        #print("\r\n\r\n")
        adjustForce(bot)
        addLine(0, d)
        #addLine(0,0,0,d)

    bugp(f"ty : {ty} -> {ty + d}")
    ty += d + bumpY
    ty = round(ty,6)
    bugp(f"***trying to move: {d} in Y dimension")
    d += bumpY
    bumpY = 0
    if not settings.getSett('debugging'):
        if not estimateTime:
            time.sleep(0.1)
            bot.translate(changePlane((0,d,0)), acc=a, vel=v, wait=False)

    if estimateTime:
        estimatedTime += .1

    addToScratchTimer(getLinearMoveTime(bot, [0,0,0], [0,d,0], a, v))
    wait(bot)

def moveXY(bot, x,y,a,v,t = 'position'):
    global tx,ty, estimatedTime
    global bumpX, bumpY
    x = x/1000.00 # /100 to translate to mm for urx
    y = y/1000.00 # /100 to translate to mm for urx

    if t == 'cut':
        addLine(x,0)
        addLine(0,y)
        #addLine(0,0,0,d)

    ty += y + bumpY
    tx += x + bumpX
    tx = round(tx,6)
    ty = round(ty,6)
    #currentPosition = bot.getl()
    bugp(f"***trying to move: {x} , {y} in X & Y dimensions")
    x += bumpX
    y += bumpY
    bumpX = 0
    bumpY = 0
    if not settings.getSett('debugging'):
        if not estimateTime:
            time.sleep(0.1)
            target = changePlane((-1 * x,y,0))
            bot.translate(target, acc=a, vel=v, wait=False)
    
    if estimateTime:
        estimatedTime += .1   
        #waitForTranslation(bot, currentPosition, target)
    addToScratchTimer(getLinearMoveTime(bot, [0,0,0], [x,y,0], a, v))
    wait(bot)


def moveXYZ(bot, x,y, zDirection,a,v,t = 'position'):
    global tx,ty,tz, estimatedTime
    global iszup
    global bumpX, bumpY
    x = x/1000.00 # /100 to translate to mm for urx
    y = y/1000.00 # /100 to translate to mm for urx
    z = zDirection * (travelZHeight/1000.00)

    if z < 0:
        iszup = False
    else:
        iszup = True

    if t == 'cut':
        addLine(x,0)
        addLine(0,y)
        #addLine(0,0,0,d)

    ty += y + bumpY
    tx += x + bumpX
    tz += z
    tx = round(tx,6)
    ty = round(ty,6)
    tz = round(tz,6)
    #currentPosition = bot.getl()
    bugp(f"***trying to move: {x} , {y} , {z} in X, Y, Z dimensions")
    x += bumpX
    y += bumpY
    bumpX = 0
    bumpY = 0
    if not settings.getSett('debugging'):
        if not estimateTime:
            time.sleep(0.1)
            target = changePlane((-1 * x,y,z))
            bot.translate(target, acc=a, vel=v, wait=False)
    
    if estimateTime:
        estimatedTime += .1   
        #waitForTranslation(bot, currentPosition, target)
    addToScratchTimer(getLinearMoveTime(bot, [0,0,0], [x,y,z], a, v))
    wait(bot)
 

def moveArc(bot,x,y,a,v,t='position'):
    print("\r\nMOVE ARC\r\n\r\n\r\n")
    global tx,ty, estimatedTime
    global bumpX, bumpY
    x = x/1000.00 # /100 to translate to mm for urx
    y = y/1000.00 # /100 to translate to mm for urx

    ty += y + bumpY
    tx += x + bumpX
    tx = round(tx,6)
    ty = round(ty,6)
    #currentPosition = bot.getl()
    bugp(f"***trying to move: {x} , {y} in X & Y dimensions in an ARC")
    x += bumpX
    y += bumpY
    bumpX = 0
    bumpY = 0

    if not settings.getSett('debugging'):
        if not estimateTime:
            time.sleep(0.1)
            target = changePlane((-1 * x,y,0))

            currentPose = bot.getl()
            targetPose = currentPose[:]
            halfPose = currentPose[:]
            targetPose[0] += target[0]
            targetPose[1] += target[1]
            targetPose[2] += target[2] + (2/1000.00)
            halfPose[0] += target[0]/2
            halfPose[1] += target[1]/2
            halfPose[2] += 50 / 1000.00
            
            via = []
            via = [halfPose[0],halfPose[1],halfPose[2],halfPose[3],halfPose[4],halfPose[5]]
            target = [targetPose[0],targetPose[1],targetPose[2],targetPose[3],targetPose[4],targetPose[5]]
            
            via = [round(val, 6) for val in via]
            target = [round(val, 6) for val in target]

            print(f"HALF {type(via)} {via}")
            print(f"target {type(target)} {target}")

            #bot.movel(halfPose,.1,.1)
            #time.sleep(5)
            
            #move1 = bot._format_move('movel',halfPose,.1,.1,radius=.01,prefix='p')
            #move2 = bot._format_move('movel',targetPose,.1,.1, prefix='p')
            #print(f"MOVE 1 : {move1}")
            #print(f"MOVE 2 : {move2}")
            #bot.send_program(move1)
            #bot.send_program(move2)
            bot.send_program(f"movec(p{halfPose},p{targetPose}, a={.1}, v={.1}, r=0)")

           

            #bot.movec(via,target,.1,.1,False)
            #bot.movec(halfPose,targetPose,.1,.1,False)
            #bot.movel(via,.1,.1,False)
            #time.sleep(3)
            #bot.movel(target,.1,.1,False)

            
            #bot.send_program(f"movel({halfPose},.1,.1,r=0.5)")

            #time.sleep(5)
            #bot.send_program(f"movel({targetPose},.1,.1)")

            #bot.send_program(f"movec({via},{target},{0.1},{0.1},{.1},{0})")
            #bot.send_program(f"movec({halfPose},{targetPose},{0.1},{0.1},{.05},{0})")
            
            addToScratchTimer(getLinearMoveTime(bot, [0,0,0], [x,y,0], .1, .1))
            
            wait(bot)


                
            
            #bot.translate(target, acc=a, vel=v, wait=False)
    
    if estimateTime:
        estimatedTime += .1   
        #waitForTranslation(bot, currentPosition, target)
    #addToScratchTimer(getLinearMoveTime(bot, [0,0,0], [x,y,0], a, v))
    #wait(bot)   

def moveXYArc(bot,x,y,a,v,t='position'):
    global tx,ty, estimatedTime
    global bumpX, bumpY
    x = x/1000.00 # /100 to translate to mm for urx
    y = y/1000.00 # /100 to translate to mm for urx

    ty += y + bumpY
    tx += x + bumpX
    tx = round(tx,6)
    ty = round(ty,6)
    #currentPosition = bot.getl()
    bugp(f"***trying to move: {x} , {y} in X & Y dimensions in an ARC")
    x += bumpX
    y += bumpY
    bumpX = 0
    bumpY = 0

    if not settings.getSett('debugging'):
        if not estimateTime:
            time.sleep(0.1)
            target = changePlane((-1 * x,y,0))

            currentPose = bot.getl()
            targetPose = currentPose[:]
            halfPose = currentPose[:]
            targetPose[0] += target[0]
            targetPose[1] += target[1]
            halfPose[0] += target[0]/2
            halfPose[1] += target[1]/2
            halfPose[2] += travelZHeight / 1000.00
            
            bot.movel(halfPose,a,v,False)
            addToScratchTimer(getLinearMoveTime(bot, [0,0,0], [x/2,y/2,0], a, v))
            wait(bot)
        
            bot.movel(targetPose,a,v,False)
            addToScratchTimer(getLinearMoveTime(bot, [0,0,0], [x/2,y/2,0], a, v))
            wait(bot)

                
            
            #bot.translate(target, acc=a, vel=v, wait=False)
    
    if estimateTime:
        estimatedTime += .1   
        #waitForTranslation(bot, currentPosition, target)
    #addToScratchTimer(getLinearMoveTime(bot, [0,0,0], [x,y,0], a, v))
    #wait(bot)



def moveZ(bot, d, a, v):
    global tz, estimatedTime
    d = d/1000.00 # /100 to translate to mm for urx
    tz += d
    tz = round(tz,6)
    bugp(f"***trying to move: {d} in Z dimension")
    if not settings.getSett('debugging'):
        if not estimateTime:
            time.sleep(0.1)
            bot.translate(changePlane((0,0,d)), acc=a, vel=v, wait=False)

    if estimateTime:
        estimatedTime += .1
    addToScratchTimer(getLinearMoveTime(bot, [0,0,0], [0,0,d], a, v))

    wait(bot)

def moveToCutHeight(bot):
    #TODO move to cut height
    bugp("TODO move to cut height")

#def liftFromCut(bot):
#    print('raising from cut height')
#    moveZ(bot, sb.zPrepH, .5, .5)

def motorOn(bot): 
    bugp("MOTOR ON")
    isMotorOn = True
    #bot.set_digital_out(0,True)
    #send_gcode(bot, "M3 S" + str(mb.getSett('motorSpeed')))
    return True

def motorOff(bot):
    isMotorOn = False
    bugp("MOTOR OFF")
    #bot.set_digital_out(0,False)
    #send_gcode(bot, "M5")
    return False


def getLinearMoveTime(bot, startP, endP, a, v):
    #distance traveled
    #startP = [v*1000 for v in startP]
    #endP = [v*1000 for v in endP]
    distance = math.sqrt((endP[0] - startP[0])**2 + (endP[1] - startP[1])**2 + (endP[2] - startP[2])**2)
    #time and distance of acceleration period
    t_acc = v/a
    d_acc = .5* a * t_acc**2

    #if distance does not allwo for max velocity to be reached just use acc period
    #else add rest of time
    if 2 * d_acc >= distance:
        t_acc_adjusted = math.sqrt(distance / a)
        total_time = 2 * t_acc_adjusted
    else:
        d_const = distance - 2 * d_acc
        t_const = d_const / v
        total_time = 2 * t_acc + t_const

    #print(f"totalTime {total_time}")
    return total_time * settings.getSett('timeMultiplier')

def getPoseMovementTime(bot, ePose, a, v):
    #calculate longest joint move
    sPose = bot.getj()
    joint_distances = [abs(e - s) for s, e in zip(sPose, ePose)]
    max_distance = max(joint_distances) 

    #time and distance of acceleration period
    t_acc = v/a
    d_acc = .5* a * t_acc**2

    #if distance does not allwo for max velocity to be reached just use acc period
    #else add rest of time
    if 2 * d_acc >= max_distance:
        t_acc_adjusted = math.sqrt(max_distance / a)
        total_time = 2 * t_acc_adjusted
    else:
        d_const = max_distance - 2 * d_acc
        t_const = d_const / v
        total_time = 2 * t_acc + t_const

    return total_time


def addToScratchTimer(t):
    global scratchTimer
    scratchTimer += (t * 1.5) 
    '''
    if not settings.getSett('debugging'):
        scratchTimer += (t * 1.5) 
    else:
        scratchTimer += (t/4)
    '''

def addLine(dx, dy):
    global cutlines
    #5,-2.5, 5, -2.5

    startx = round(tx,6)# - startingPose[0]
    starty = round(ty,6)# - startingPose[1]
    gox = round(startx + dx,6)
    goy = round(starty + dy,6)

    #print(f"\n\nADD LINE -- {startx}, {starty}, {gox}, {goy}\n\n")

    cutlines.append([startx,starty,gox,goy])

def getLines():
    c =  [[float(v*1000) for v in r] for r in cutlines]
    #print(f"CUTLINES: {c}")
    return c

def clearLines():
    global cutlines
    cutlines.clear()


def setNewStartingPosition(bot, moves, outfile):
    bugp("SET NEW POSE")
    bugp(settings.getSett('debugging'))

    if(settings.getSett('status') == 'ready' and not settings.getSett('debugging')):
        bugp("FREEDRIVE")
        bot.set_freedrive(True, timeout=30)
        bugp('gototsleep')
        time.sleep(30)
        bugp('done sleeping')
        l = bot.getl()
        j = bot.getj()
        label = "startingPose"

        moves[label] = {
            'joints': j,
            'transformations': l
        }
        bugp(f"MOVESSSS ::::: {moves}")

        bugp(json.dumps(moves))
    
        for k,m in moves.items():
            bugp(f"{k} {m}")
        
        
        with open(outfile, 'w+') as f:
            f.write("position label, joints, transformations\n")
            json.dump(moves, f)
        
        return True
        
    else:
        return False




def getAlignerTranslatedPose(bot,pose):
    try:
        xo = settings.getSett('alignoffx')
        yo = settings.getSett('alignoffy')
        zo = settings.getSett('zStartOffset')

        adx = settings.getSett('adjustx')
        ady = settings.getSett('adjusty')

        #bw = settings.getSett('bitw')

        #print(f"POSE: OLD {pose}")
        # Modify the Z-coordinate of the position
        pose['transformations'][2] += 0.001 * zo   # Convert n mm to meters (UR uses meters)

        ##CENTER OF BIT ALIGNED OVER CORNER OF TICKET!
        #pose['transformations'][0] += ( (0.001 * xo) - (adx/1000) + (bw/2000) )
        #pose['transformations'][1] -= ( (0.001 * yo) - (ady/1000) - (bw/2000) )

        pose['transformations'][0] +=  (0.001 * xo) + (adx/1000)
        pose['transformations'][1] +=  (0.001 * yo) + (ady/1000)


        #print(f"POSE: new {pose}")

        return pose

    except Exception as e:
        bugp("FALIED TO Z OFF")
        bugp(e)
        traceback.format_exc()


def adjustStartingPose(bot, moves):
    global startingPose
    print(f"op {originalStartingPose['transformations']}")
    print(f"sp {moves['startingPose']['transformations']}")
    
    moves['startingPose'] = getAlignerTranslatedPose(bot, copy.deepcopy(originalStartingPose))
    startingPose = moves['startingPose']

    print(f"op {originalStartingPose['transformations']}")
    print(f"sp {moves['startingPose']['transformations']}")
    return moves['startingPose']



def changePlane(p):
    #ps = settings.getSett('threePoints')
    
    #matrix = frame.create_rotation_matrix_for_plane(ps[0],ps[1],ps[2])
    #point = frame.apply_rotation_matrix(matrix, p)
    
    #print(f"TRANSFORMED POINT FROM: {[round(x *1000,2) for x in p]} ----> {np.round(point * 1000,2)}")
    
    return p
    #return point

def oldadjustForce(bot, targetForce = False):
    global scratchTimer
    
    if not estimateTime:
                    
        if settings.getSett('checkForce') and not settings.getSett('debugging'):
            #if not targetForce:
            targetForce = settings.getSett('forceScratch')

            #force = getDebouncedForce(bot)
            force = getSensorForce(bot)
            
          
            #make sure that force value is supplied
            while not force:
                force = getSensorForce(bot)
                #force = getDebouncedForce(bot)
                


            #y=−0.0242x2+2.2012x−11.1997
            difference =  targetForce - force 
            
            bugp(f"target: {targetForce} FORCE: {force}")
            bugp(f"SPREAD ALLOWANCE: {settings.getSett('forceWiggleRoom')}    DIFFERENCE : {difference}")
            
            if abs( difference) < settings.getSett('forceWiggleRoom') :
                return True
        
            #if gravity is acting upon tcp more than table then push down and try again
            elif isGravity(bot):
                moveZ(bot, -.5, 2, 2)
                #print("-------GRAVITY-------")
                adjustForce(bot, targetForce)

            else:
                adj = settings.getSett('adjustmentMulti')
                  
                if difference > 0:
                    #print(f"FORCE: {force} -----")
                    bugp("-----------------------------------------")
                    
                    moveZ(bot, -1*adj* (abs(difference))/10, 2, 2)
                    
                else:
                    #print(f"FORCE: {force} +++++")
                    bugp("+++++++++++++++++++++++++++++++++++++++++")
                    
                    moveZ(bot, adj*(abs(difference))/10, 2 ,2)
                    
                adjustForce(bot, targetForce )
            time.sleep(0.1)
    else:
        scratchTimer += 1

#recursivly adjust z height until force target is met twice in a row
def adjustForce(bot, targetForce = False):
    global scratchTimer
    
    #skip if performing time estimate
    if not estimateTime:
        
        #skip if debugging or not checking force setting  
        if settings.getSett('checkForce') and not settings.getSett('debugging'):
            
            targetForce = settings.getSett('forceScratch')
            force = False
            while not force:
                force = getDebouncedSensorForce(bot)

            difference =  targetForce - force 
            
            bugp(f"target: {targetForce} FORCE: {force}")
            bugp(f"SPREAD ALLOWANCE: {settings.getSett('forceWiggleRoom')}    DIFFERENCE : {difference}")
            
            if abs( difference) < settings.getSett('forceWiggleRoom') :
                return True
        
            #if gravity is acting upon tcp more than table then push down and try again
            elif isGravity(bot):
                moveZ(bot, -.5, 2, 2)
                #print("-------GRAVITY-------")
                adjustForce(bot, targetForce)

            #move z position based on force reading with respect to forceData table and target force
            else:
                adj = settings.getSett('adjustmentMulti')
                  
                if difference > 0:
                    bugp("-----------------------------------------")
                else:
                    bugp("+++++++++++++++++++++++++++++++++++++++++")
                    
                dis = getTargetDistance(force, targetForce)
                moveZ(bot, -1*adj* dis, 2, 2)
               
                adjustForce(bot, targetForce )

            time.sleep(0.1)
    else:
        scratchTimer += 1

def getTargetDistance(force, target):
    with open('poseData/forceData.csv', 'r') as f:
        reader = csv.reader(f)
        data = list(reader)

    at = 0
    to = 0
    
    for i in range(0,len(data)-1):
        if float(data[i][0]) <= force < float(data[i+1][0]):
            at = float(data[i][1])

    for i in range(0,len(data)-1):
        if float(data[i][0]) <= target < float(data[i+1][0]):
            to = float(data[i][1])

    travel = to - at

    bugp(f"adjusting Z : {at} - {to} = {travel}")
    return travel

debounce = 50000
tightness = 5
def getDebouncedForce(bot):
    #readings = [bot.get_force() for _ in range(debounce)]
    readings = [bot.get_analog_in(2) for _ in range(debounce)]
    avg = sum(readings) / len(readings)
    filtered = [x for x in readings if abs(x-avg) <= tightness]

    return sum(filtered) / len(filtered) if filtered else False


def HighResDelay(amt):
    t = 0
    start = time.perf_counter()
    while time.perf_counter() - start < amt:
        pass

sendebounce = 1000
sentightness = 2
sendelay = .00001
def getDebouncedSensorForce(bot):
    secmon = bot.secmon
    readings = []
    for r in range(0,sendebounce):
        readings.append((secmon._dict['ToolData']['analogInput3'] - secmon._dict['ToolData']['analogInput2']) * 1000)
        HighResDelay(sendelay)
            
    avg = sum(readings) / len(readings)
    filtered = [x for x in readings if abs(x-avg) <= sentightness]

    return sum(filtered) / len(filtered) if filtered else False

sensorSamples = 1000
def getSensorForce(bot):
    secmon = bot.secmon
    #readings = [secmon._dict['ToolData']['analogInput2'] for _ in range(sensorSamples)]
    readings = [(secmon._dict['ToolData']['analogInput2'] - secmon._dict['ToolData']['analogInput3']) * 1000 for _ in range(sensorSamples)]
    avg = sum(readings) / len(readings)
    #filtered = [x for x in readings if abs(x-avg) <= tightness]

    return avg
    


def isGravity(bot, gravity_vector=np.array([0, 0, -9.81]), angle_threshold=90):
    if not settings.getSett('debugging'):
        forces = []
        for r in range(0,5000):
            forces.append(bot.get_tcp_force())

        # Compute the average of the force vectors
        average_force = np.mean([np.array(force[:3]) for force in forces], axis=0)
        if np.linalg.norm(average_force) == 0:
            return False  # No force, not aligned with anything

        # Normalize vectors
        average_force_normalized = average_force / np.linalg.norm(average_force)
        gravity_vector_normalized = gravity_vector / np.linalg.norm(gravity_vector)

        # Calculate the angle between the vectors
        dot_product = np.dot(average_force_normalized, gravity_vector_normalized)
        angle = np.degrees(np.arccos(np.clip(dot_product, -1.0, 1.0)))

        bugp(f"target: {angle_threshold}  angle: {angle}")
        # Check if the angle is within the threshold
        #return angle <= angle_threshold or angle >= 180 - angle_threshold
        return angle <= angle_threshold
        #return angle <= angle_threshold
    else:
        return True

def getForceAngle( bot, gravity_vector=np.array([0, 0, -9.81]) ):
    forces = []
    for r in range(0,5000):
        forces.append(bot.get_tcp_force())

    # Compute the average of the force vectors
    average_force = np.mean([np.array(force[:3]) for force in forces], axis=0)
    if np.linalg.norm(average_force) == 0:
        return False  # No force, not aligned with anything

    average_force_normalized = average_force / np.linalg.norm(average_force)
    gravity_vector_normalized = gravity_vector / np.linalg.norm(gravity_vector)

    # Calculate the angle between the vectors
    dot_product = np.dot(average_force_normalized, gravity_vector_normalized)
    angle = np.degrees(np.arccos(np.clip(dot_product, -1.0, 1.0)))

    #print(f"angle: {angle}")

    return angle


#determine relative distance from startingPose, rather than calculated (ie tx,ty)
def getRelativePosition(bot):
    if not settings.getSett('debugging'):
        sp = startingPose['transformations']
        cp = bot.getl()
        x = round( -(cp[0] - sp[0]) , 6)
        y = round( (cp[1] - sp[1]) , 6)

        return x,y

    else:
        return False

