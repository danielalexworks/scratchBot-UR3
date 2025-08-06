import moneyBadger_GUI as mb
import time
import threadManager
import serial


#start up cnc
def initialize_cnc():
    debugging = mb.getSett('debugging')
    print('d ' + str(debugging))
    if debugging == False:
        cnc = serial.Serial(mb.getSett('port'), 115200, timeout=1)
        print('initializing...')
        # Wait for the CNC controller to be ready
        time.sleep(2)  
        cnc.write(b"\r\n\r\n")  # Send a newline to wake up GRBL
        time.sleep(2) 
        cnc.flushInput()  # Flush any initial data in the serial buffer
        print('complete')

        return cnc
    else:
        return False

#send gcode command to machine
def send_gcode(cnc, command):
    threadManager.checkPause()
    debugging = mb.getSett('debugging')
    
    
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

    #else:
    #print(command)
    #print('--------------' + command)


def motorOn(cnc): 
    send_gcode(cnc, "M3 S" + str(mb.getSett('motorSpeed')))
    return True

def motorOff(cnc):
    send_gcode(cnc, "M5")
    return False

#formulate gcode for X movement
def MoveX(cnc, x, tx, tz, scratchTimer, t = 'move'):

    scratchTimer += abs(x)
   
    #check direction of movement
    #set zcheck resolution accordingly
    if x < 0:
        mres = -1 * mb.getSett('movementResolution')
        neg = True
    else:
        mres = mb.getSett('movementResolution')
        neg = False


    #forumlate gcode in increments of resolution
    #or what's left over
    #adjust speed accordingly
    #adjust Z offset after each increment
    #skip and move all at once if positioning or going home
    if t != 'gohome' and t != 'positioning':
        
        while (neg and x < 0) or (not neg and x > 0):
            zshift = mb.adjustZ()
            #tryPauseProgram()
            if abs(x) > abs(mres):
                cmd = "G21G91X" + str(mres)
                tx += mres
            else:
                cmd = "G21G91X" + str(x)
                tx += x

            if zshift:
                cmd += "Z" + str(zshift)
                tz += zshift
                mb.tz = tz
                mb.tx = tx
                scratchTimer += abs(zshift)


            if t == 'cut':
                cmd += "F" + str(mb.getSett('travelSpeedCut'))
            else:
                cmd += "F" + str(mb.getSett('travelSpeed'))

            
            send_gcode(cnc,cmd)
            x -= mres
    else:
        cmd = "G21G91X" + str(x) + "F" + str(mb.getSett('travelSpeed'))
        tx += x
        send_gcode(cnc,cmd)

    return tx, tz, scratchTimer
        
#see above
def MoveY(cnc, y, ty, tz, scratchTimer, t = 'move'):
    scratchTimer += abs(y)

    if y < 0:
        mres = -1 * mb.getSett('movementResolution')
        neg = True
    else:
        mres = mb.getSett('movementResolution')
        neg = False

    if t != 'gohome' and t != 'positioning':
        while (neg and y < 0) or (not neg and y > 0):
            zshift = mb.adjustZ()
            #tryPauseProgram()
            time.sleep(1)
            mb.bugp("y: " + str(y))
            if abs(y) > abs(mres):
                cmd = "G21G91Y" + str(mres)
                ty += mres
            else:
                cmd = "G21G91Y" + str(y)
                ty += y

            if zshift:
                cmd += "Z" + str(zshift)
                tz += zshift
                mb.tz = tz
                mb.ty = ty
                scratchTimer += abs(zshift)

            if t == 'cut':
                cmd += "F" + str(mb.getSett('travelSpeedCut'))
            else:
                cmd += "F" + str(mb.getSett('travelSpeed'))    

            send_gcode(cnc,cmd)
            y -= mres
    else:
        cmd = "G21G91Y" + str(y) + "F" + str(mb.getSett('travelSpeed'))
        ty += y
        send_gcode(cnc,cmd)

    return ty, tz, scratchTimer

def MoveZ(cnc, z, tz, scratchTimer, t = 'move'):

    #tryPauseProgram()

    #print("tz: " + str(tz))
    z = round(z,2)
    scratchTimer += abs(z)

    cmd = "G21G91Z" + str(z) + "F"
    if t == 'cut':
        cmd += str(100)
    else:
        cmd += str(600)

    send_gcode(cnc,cmd)
    tz = round(z + tz,2);
    if(tz != 0):
        isZHome = False
    else:
        isZHome = True
    #print("tz: " + str(tz))

    return tz,scratchTimer, isZHome

