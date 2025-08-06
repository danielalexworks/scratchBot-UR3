import urx
import time
import traceback
import cobot

a=.5
v=.5

infile= 'poseData/cobotPos.csv'

####################################################
#                                                  #
#                 PROGRAM START                    #
#                                                  #
####################################################

rob = cobot.initializeCobot()
moves = cobot.getMovesFromFile(rob,infile)
if cobot.getPose(rob, moves) != 'startingPos':
	cobot.moveTo(rob,moves, 'startingPos', 'joints', a,v)
	time.sleep(5)

#move in box
#cobot.moveX(rob, .01, .1, .1)
#cobot.moveY(rob, .01, .1, .1)
#cobot.moveX(rob, -.01, .1, .1)
#cobot.moveY(rob, -.01, .1, .1)

cobot.moveTo(rob,moves, 'home', 'joints', a,v)
time.sleep(5)

'''
cobot.moveTo(rob,moves, 'startingPos', 'joints', a,v)
time.sleep(10)
cobot.moveTo(rob,moves, 'home', 'joints', a,v)
time.sleep(10)
print(moves)
'''

cobot.shutdown(rob)
