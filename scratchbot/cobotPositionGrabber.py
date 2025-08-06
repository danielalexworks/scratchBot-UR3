import urx
import time
import os
import traceback
import numpy as np
import frame
import json
import keyboard
import sys
import pprint
import csv
a=.1
v=.1
ip = "192.168.137.100"
ip = "169.254.193.201"
outfile= 'poseData/cobotPos.csv'
framefile = 'poseData/frameData.json'
forceData = 'poseData/forceData.csv'

def printHelp():
    print("---VALID COMMANDS---")
    
    commands = [
        ["c:","clear saved positions"],
        ["f :","enable free drive for 120 seconds"],
        ["s :","save position"],
        ["n :","get normal from 3 points (follow prompts)"],
        ["r :","test force mode"],
        ["g :","get force mode"],
        ["d :","display continuous force readings"],
        ["e :","execute force graph routine"],
        ["h :","print this message"],

        ["q :","close program"]

    ]
    col_width = max(len(row[0]) for row in commands) + 3

    for row in commands:
        print(f"{row[0]:<{col_width}} {row[1]}")

    
def wait(do_wait = False):
    if do_wait:
        print("Click enter to continue")
        input()


def initializeCobot():
        cnt = 0
        while cnt < 5:
            try:
                print('...trying to start bot...')
                rob = urx.Robot(ip, True)    
                #rob.set_tcp((0, 0, 0.1 , 0, 0, 0))
                #lil marker
                #rob.set_tcp((0, 62/1000, 99.3/1000 , 0.349, 0, 0))
                #pencil
                #rob.set_tcp((0, 110/1000, 104/1000 , 0, 0, 0))
                #rigidcoin
                #rob.set_tcp((0, 0, 151/1000 , 0, 0, 0))
                #longcoin
                #rob.set_tcp((0, 55/1000, 394/1000 , 0, 0, 0))
                #probe
                #newcoin
                rob.set_tcp((0, 0, 171/1000 , 0, 0, 0))
                #rob.set_tcp((66/1000, 0, 118/1000 , 0, 0,0.174))
                #rob.set_tcp((0, 66/1000, 118/1000 , 0.174,0, 0 ))

                print('tcp set')
                #rob.set_payload(.11, (0, 0, 61/1000))
                #rob.set_payload(.31, (0, 0, 170/1000))
                rob.set_payload(.21, (0, 0, 60/1000))
                print('payload set')
                time.sleep(0.2)
                print(" .---.  .----. .----.  .----.  .---.    .-..-. .-..-. .---. .-.  .--.  .-.   .-. .---. .----..----. ")
                print("/  ___}/  {}  \\| {}  }/  {}  \\{_   _}   | ||  `| || |{_   _}| | / {} \\ | |   | |{_   / | {_  | {}  \\")
                print("\\     }\\      /| {}  }\\      /  | |     | || |\\  || |  | |  | |/  /\\  \\| `--.| | /    }| {__ |     /")
                print(" `---'  `----' `----'  `----'   `-'     `-'`-' `-'`-'  `-'  `-'`-'  `-'`----'`-' `---' `----'`----' ")

                rob.send_program("set_tool_voltage(12)")
                return rob

            except Exception as e:
                print(e)
                traceback.format_exc()
                cnt += 1

        if cnt == 5 :
            print('failed to connect')
            os._exit(1)
   

def alignTicket():
    print('')

def getNormal():
    points = []

    for i in range(0,3):
        if i == 0:
            input(f"move probe to top right corner. Adjust position until tip touches but light doesn't turn on. Then press enter")
        elif i == 1:
            input(f"move probe along x axis in + direction. Adjust position until tip touches but light doesn't turn on. Then press enter")
        else:
            input(f"move probe along y axis in + direction. Adjust position until tip touches but light doesn't turn on. Then press enter")
        p = rob.getl()
        points.append((p[0],p[1],p[2]))

    print(points)
    normal = frame.computeNormal(points[0],points[1],points[2])

    o = {}
    o['points'] = points
    o['normal'] = normal.tolist()
    with open(framefile, 'w') as f:
            json.dump(o, f, indent=4)

    return normal

debounce = 50000
tightness = 5
def testForce():
    forceMarkers = []
    
    print("\n\n=======================================================")
    print("set TCP where no force being applied and press s")
    #get readings and take average
    # after 1/10 readings complete, discard outliers based on tightness
    cnt = 0
    l = 0
    while True:
        '''
        f = 0
        cnt = 0
        for i in range(0,debounce):
            c = rob.get_force()
            if i > debounce / 10:
                if abs( (f / i) - c ) < tightness:
                    f += c
                    cnt += 1
            else:
                f += c
                cnt += 1


        f = f/cnt
        t = f"FORCE : {f}"
        s = " " * l
        print(f"\r{s}\r{t}", end = "")
        sys.stdout.flush()
        l = len(t)
        '''
        
        
        

        print(f" isSmoothgravity: {isNotGravity(rob)}")
        input()

        readings = [rob.get_analog_in(2) - rob.get_analog_in(3) for _ in range(debounce)]
        avg = sum(readings) / len(readings)
        filtered = [x for x in readings if abs(x-avg) <= tightness]

        print(f"FORCE: {sum(filtered) / len(filtered) if filtered else None}")

        time.sleep(.1)

        if keyboard.is_pressed("q"):
            break
        elif keyboard.is_pressed("s"):
            forceMarkers.append(f)
            print("\nFORCE SAVED: {f}")
            if len(forceMarkers) == 1:
                print("set TCP where optimal force being applied and press s")
            else:
                print("set TCP where too much force being applied and press s")

    with open('poseData/forceSettings.json', 'w+') as file:
            json.dump(forceMarkers, file, indent=4)

    print('\rforce settigns saved')


def getForce():
    readings = [rob.get_tcp_force() for _ in range(debounce)]
    avg = sum(readings) / len(readings)
    #filtered = [x for x in readings if abs(x-avg) <= tightness]

    print(f"tcp force: {avg}")

    secmon = rob.secmon
    pprint.pprint(secmon._dict['ToolData']['analogInput2'])
    pprint.pprint(secmon._dict['ToolData']['analogInput3'])
    #readings = [rob.send_program("textmsg(get_analog_in(2))") for _ in range(debounce)]
    #avg = sum(readings) / len(readings)
    #filtered = [x for x in readings if abs(x-avg) <= tightness]

    #print(f"sensor force: {avg}")

def displayForce():
    readings = [rob.get_tcp_force() for _ in range(debounce)]
    avg = sum(readings) / len(readings)
    #filtered = [x for x in readings if abs(x-avg) <= tightness]

    print(f"tcp force: {avg}")

    
    #secmon = rob.secmon
    while(True):
        print(f"\r{getDebouncedSensorForce()}", end="", flush=True)
        #print(f"\r{ round( (secmon._dict['ToolData']['analogInput2'] - secmon._dict['ToolData']['analogInput3']) * 1000,2 )}", end="", flush=True)
        
        if keyboard.is_pressed('q'):
            break


def getOldForce():
    readings = [rob.get_tcp_force() for _ in range(debounce)]
    avg = sum(readings) / len(readings)
    #filtered = [x for x in readings if abs(x-avg) <= tightness]

    print(f"tcp force: {avg}")

    secmon = rob.secmon
    pprint.pprint(secmon._dict['ToolData']['analogInput2'])
    #readings = [rob.send_program("textmsg(get_analog_in(2))") for _ in range(debounce)]
    #avg = sum(readings) / len(readings)
    #filtered = [x for x in readings if abs(x-avg) <= tightness]

    #print(f"sensor force: {avg}")



debounce = 500
tightness = 2
def getDebouncedSensorForce():
    secmon = rob.secmon
    readings = []
    for r in range(0,debounce):
        try:
            readings.append((secmon._dict['ToolData']['analogInput3'] - secmon._dict['ToolData']['analogInput2']) * 1000)
            time.sleep(0.0001)
        except:
            cobot.shutdown()
    #readings = [(secmon._dict['ToolData']['analogInput2'] - secmon._dict['ToolData']['analogInput3']) * 1000 for _ in range(debounce)]
    avg = sum(readings) / len(readings)
    filtered = [x for x in readings if abs(x-avg) <= tightness]


    return sum(filtered) / len(filtered) if filtered else False


def getDebouncedTCPForce():

    readings = [rob.get_tcp_force() for _ in range(debounce)]
    avg = sum(readings) / len(readings)
    filtered = [x for x in readings if abs(x-avg) <= tightness]

    return sum(filtered) / len(filtered) if filtered else False



def isNotGravity(bot, gravity_vector=np.array([0, 0, -9.81]), angle_threshold=20):
    
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

    # Check if the angle is within the threshold
    return angle <= angle_threshold or angle >= 180 - angle_threshold



def normalTest():
    p1 = (0,0,0)
    p2 = (0,1,1)
    p3 = (1,1,2)
    tp = (2,2,1)
    #normal = frame.computeNormal(p1,p2,p3)
    #print(f"NORMAL {normal}")
    #R, tv = frame.getTranslationVector((0,0,0),(1,0,1),(2,3,3))
    #print(f"TRANSLATION VECTOR {tv}")
    origin = (0,0,0)
    #matrix = frame.create_frame(normal,origin)
    #print(f"MATRIX {matrix}")
    matrix = frame.create_rotation_matrix_for_plane(p1,p2,p3)
    print(f"MATRIX {matrix}")
    point = frame.apply_rotation_matrix(matrix, tp)

    print(f"{origin} to {point}")
    
    #point = frame.transform_to_base_frame(matrix, (2,2,1))
    #print(f"{origin} to {point}")
    #point = frame.transform_point((2,2,1), R, tv)
    #print(f"{origin} to {point}")


def forceGraph():
    maxForce = input("Enter max force value (~30) : ")
    if maxForce == 'q':
        shutdownCobot()
    maxForce = int(maxForce)
    inc = input("Enter Movement Increments in mm (0.2) : ")
    inc = float(inc)

    readings = []

    input("Move TCP so that it is touching the table in the scratch position and pree Enter.")

    print("Beginning Force Graph Routine. Please Wait.")
    print('READING FORCE')
    force = getDebouncedSensorForce()
    while( force < maxForce):
        print(f"FORCE: {force}")
        if keyboard.is_pressed('q'):
            break
        readings.append(force)
        print(f"LOWERING : {inc}mm")
        moveZ(inc)
        time.sleep(1)
        print('READING FORCE...')
        force = getDebouncedSensorForce()

    print(f"\r\n\r\n{readings}\r\n\r\n")
    #print("paste the above into poseData/forceData.csv. Put each on own line. and add , inc amount after each force value")
    
    with open(forceData, 'w', newline='') as f:
        writer = csv.writer(f)
        for i,num in enumerate(readings):
            writer.writerow([num, round((i*inc)+inc,2)])
    

def getTargetDistance(target):
    with open('poseData/forceData.csv', 'r') as f:
        reader = csv.reader(f)
        data = list(reader)

    force = getDebouncedSensorForce()
    print(f"force: {force}")

    at = 0
    to = 0
    
    for i in range(0,len(data)-1):
        if float(data[i][0]) <= force < float(data[i+1][0]):
            at = float(data[i][1])

    for i in range(0,len(data)-1):
        if float(data[i][0]) <= target < float(data[i+1][0]):
            to = float(data[i][1])

    travel = to - at
    print(f"{at} - {to} = {travel}")
    moveZ(travel)

def moveZ(d):
    global tz, estimatedTime
    d = -1* (d/1000.00) # /100 to translate to mm for urx
    rob.translate((0,0,d), acc=.5, vel=.5, wait=False)

    
def shutdownCobot():
    rob.send_program("set_tool_voltage(0)")
    print('meh')
    os._exit(1)

#(0,0,0) (1,0,1), (2,3,3) surface
#go to  (2, 2, 1), from 0,0,0
# = (0.789, 0.263, -0.789)
####################################################
#                                                  #
#                 PROGRAM START                    #
#                                                  #
####################################################

try:
    rob = initializeCobot()
    printHelp()
    normalTest()

    while True:
        
        k = input("input command code: ")
        
        if k == 'f':
            print("**free drive enabled for 120 seconds**")
            rob.set_freedrive(True, timeout=120)
            for i in range(19,0):
                print(i)
                time.sleep(1)
        elif k == 'c':
            with open(outfile, 'w+') as f:
                f.write("position label, joints, transformations\n")

            print("**positions cleared from " + outfile)

        elif k == 's':
            print('**OUTPUTTING POSITION**')
            l = rob.getl()
            j = rob.getj()

            label = input('position label: ')

            with open(outfile, 'a+') as f:
                f.write(f"\"{label}\",\"{j}\",\"{l}\"\n")

            print(f"{label} written to {outfile}")
            print(f"TRANSFORMATIONS: {l}")
            print(f"JOINTS         : {j}")

        elif k == 'a':
            alignTicket()
        elif k == 'd':
            displayForce()
        elif k == 'q':
            #cobot.shutdown(rob)
            shutdownCobot()

        elif k == 'e':
            forceGraph()

        elif k == 'h':
            printHelp()

        elif k == 'n':
            normal = getNormal()
            print(f"NORMAL : {normal}")

        elif k == 'r':
            testForce()
        elif k == 'g':
            getForce()
        elif k =='t':
            getTargetDistance(30)
        else:
            print("invalid command - try h for help")

        time.sleep(.2)
except Exception as e:
    print(e)
    shutdownCobot()