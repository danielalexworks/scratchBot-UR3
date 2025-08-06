import urx
import time
import os

a=.1
v=.1
try:
    rob = urx.Robot("192.168.137.100")
    rob.set_tcp((0, 0, 0.1, 0, 0, 0))
    rob.set_payload(2, (0, 0, 0.1))
    time.sleep(0.2)  #leave some time to robot to process the setup commands

    rob.movej((1, 2, 3, 4, 5, 6), a, v)
    print('========================= MOVE L')
    rob.movel((x, y, z, rx, ry, rz), a, v)
    print( "Current tool pose is: ",  rob.getl())
    rob.movel((0.1, 0, 0, 0, 0, 0), a, v, relative=True)  # move relative to current pose
    print('========================= MOVE TOOL')
    rob.translate((0.1, 0, 0), a, v)  #move tool and keep orientation
    rob.stopl()

    os._exit(1)
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
    os._exit(1)