import urx
import time
import os
import traceback

a=.1
v=.1
freedriveTimeOut = 2
rob = urx.Robot("192.168.137.100")
do_wait = True

def wait():
    if do_wait:
        print("Click enter to continue")
        input()


try:
    #rob = urx.Robot("192.168.137.100")
    rob.set_tcp((0, 0, 0.1 , 0, 0, 0))
    rob.set_payload(.1, (0, 0, 0.1))
    time.sleep(0.2)  #leave some time to robot to process the setup commands
    #print("---FREEDRIVE FOR "+ str(freedriveTimeOut) + " seconds")
    '''
    rob.set_freedrive(True, timeout=freedriveTimeOut)
    time.sleep(0.1)
    t = 0
    while t < freedriveTimeOut:
        print(t)
        t += 1
        time.sleep(1)


    rob.set_freedrive(False)
    '''
    j = rob.getj()
    print("JOINTS")
    print(j)
    
    t = rob.get_pose()
    print("TRANSFORMATIONS")
    print(t)
    time.sleep(0.1)
    print('move')
    wait()
    try:
        #move up
        #rob.translate((0,0,-.01), acc=a, vel=v, wait=True)
        #rotate last joint
        wait()
        j[5] += 1
        print(j)
        #rob.stopj()
        #time.sleep(2)
        rob.movej(j, acc=8, vel=3.14, wait=True)
        time.sleep(5)
    except urx.RobotException as e:
        print('robo ex: ' + str(e))
        traceback.format_exc()
    except Exception as e:
        print('poop')
        print(e)
        traceback.format_exc()

    #rob.stopl()
    #rob.stopj()
    #rob.movel((0.1, 0, 0, 0, 0, 0), a, v, relative=True)
    print('gonna')
    #rob.stop()
    print('stop')
    rob.close()
    print('close')
    os._exit(1)
    



    #rob.movej((1, 2, 3, 4, 5, 6), a, v)
    #print('========================= MOVE L')
    #rob.movel((x, y, z, rx, ry, rz), a, v)
    #print( "Current tool pose is: ",  rob.getl())
    #rob.movel((0.1, 0, 0, 0, 0, 0), a, v, relative=True)  # move relative to current pose
    #print('========================= MOVE TOOL')
    #rob.translate((0.1, 0, 0), a, v)  #move tool and keep orientation
    #rob.stopl()

    '''
    rob.movel((x, y, z, rx, ry, rz), wait=False)
    while True :
        sleep(0.1)  #sleep first since the robot may not have processed the command yet
        if rob.is_program_running():
            break

    rob.movel((x, y, z, rx, ry, rz), wait=False)
    while rob.getForce() < 50:
        sleep(0.01)
        if not rob.is_program_running():
            break
    rob.stopl()
    '''

except Exception as e:
    print(e)
    traceback.format_exc()
    
    os._exit(1)

finally:
  
    
    os._exit(1)