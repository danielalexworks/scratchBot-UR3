import scratchBot as sb
import time
import settings
import threadManager
import ticket
import cobot
import random
import cameraTracker as cam



remaining =[]
programComplete = False
endNow = False
firstScratch = True
nextGroup = False

programs = ['random', 'scratch by group', 'all', 'scratch by group interruptable']
 
def startCurrentProgram():
    scratchArea = ticket.gatherScratchData(settings.getSett('scratchData'))
    threadManager.startProgram(settings.getSett('scratchOrder'), scratchArea)

#scracth every area, choosen at random
def doAllRandom(areas):
    global remaining
    global programComplete, firstScratch
    programComplete = False
    firstScratch = True
    cobot.clearLines()
    sb.setStartingPose()
    settings.setSett('filterIds', '')

    cam.goToBack(True)

    print('*****************************************')
    print("***** STARTING PROGRAM : ALL RANDOM *****")
    print('*****************************************')
    cam.goToTicketTop(True)
    time.sleep(2)

    settings.updateSettings({'filterIds':'','status':'in progress'})

    #make a list of all scratch areas
    remaining = list(range(0,len(areas)))
    

    sb.moveTo('startingPose')
    
    sb.zUp()

    #choose a random area,
    #scratch it
    #remove it from remaining, until remaining is empty
    #sleep may need to be adjusted, seems like a good number, though
    while len(remaining):   
        threadManager.checkPause()
        if threadManager.checkStop():
            break
        if endNow:
            remaining = 0
        else:     
            num = random.choice(remaining)
            sb.bugp("========== Cutting # ::: " + str(num) + " ::: ==========")
            sb.scratchIt(areas[num])
            #sb.wait()
            remaining.remove(num)
            #time.sleep(sb.getScratchTimer()/10 + 4)
            #time.sleep(10)
            firstScratch = False

    finshProgram()

def scratchAllInOrder(areas):
    global remaining
    global programComplete, firstScratch
    programComplete = False
    firstScratch = True
    cobot.clearLines()
    sb.setStartingPose()
    settings.setSett('filterIds', '')

    cam.goToBack(True)

    print('*******************************************')
    print("***** STARTING PROGRAM : ALL IN ORDER *****")
    print('*******************************************')
    cam.goToTicketTop(True)
    time.sleep(2)
    settings.updateSettings({'filterIds':'','status':'in progress'})

    #make a list of all scratch areas
    remaining = list(range(0,len(areas)))

    sb.moveTo('startingPose')
    

    #choose a random area,
    #scratch it
    #remove it from remaining, until remaining is empty
    #sleep may need to be adjusted, seems like a good number, though
    for num in range(0,len(areas)):
        threadManager.checkPause()
        if threadManager.checkStop():
            break
        if endNow:
            break
        else:
            sb.bugp("========== Cutting # ::: " + str(num) + " ::: ==========")
            sb.scratchIt(areas[num])
            #sb.wait()
            #time.sleep(cobot.getScratchTimer()/10 + 4)
            firstScratch = False
            remaining.remove(num)
    
    finshProgram()

def scratchByGroup(areas):
    global remaining, nextGroup
    global programComplete, firstScratch
    programComplete = False
    firstScratch = True
    cobot.clearLines()
    sb.setStartingPose()
    settings.setSett('filterIds', '')
    cam.goToBack(True)

    print("*********************************************")
    print("***** STARTING PROGRAM : NUMS B4 PRIZES *****")
    print('*********************************************')
    cam.goToTicketTop(True)
    time.sleep(2)
    settings.updateSettings({'filterIds':'','status':'in progress'})

    winningIds = []
    #make a list of all scratch areas
    remaining = list(range(1,len(areas)+1))
    
    #sort areas by group (type)
    #areas = sorted(areas, key=lambda i: i[5])
    #get list of groups and sort them
    groups = sorted(list(set(i[5] for i in areas)))

    sb.moveTo('startingPose')
    sb.zUp()

    #iterate through groups and scratch boxes
    # pause if finish group and there is a p in the group id
    # filter scratches by filter list if an f in group id
    
    for group in groups: 
        print('+++++++++++++++++++++++++++++++++++++++++||')
        print("++++++++++++++++++++++++" + group)
        print('+++++++++++++++++++++++++++++++++++++++++||')
        threadManager.checkPause()
        if threadManager.checkStop():
            break

        if endNow:
            break
        else:
            for area in areas:
                #advance group button in UI
                if nextGroup:
                    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++NEXTGROUP")
                    nextGroup = False
                    break

                threadManager.checkPause()
                if threadManager.checkStop():
                    break
                if endNow:
                    break
                else:
                    if area[5] == group:
                        
                        if 'f' in group:
                            if str(area[8]) in settings.getSett('filterIds').split(','):
                                sb.scratchIt(area)
                                firstScratch = False
                                remaining.remove(area[8])
                                
                        else:
                            sb.scratchIt(area)
                            firstScratch = False
                            remaining.remove(area[8])
                        #wait_for_enter()

        
        if not endNow:
            if('p' in group):
                if not cobot.estimateTime:
                    sb.togglePause("in progress")

    
    finshProgram()


def scratchByGroupInterruptable(areas):
    global remaining, nextGroup
    global programComplete, firstScratch
    programComplete = False
    firstScratch = True
    cobot.clearLines()
    sb.setStartingPose()
    settings.setSett('filterIds', '')
    cam.goToBack(True)

    print("***********************************************************")
    print("***** STARTING PROGRAM : NUMS B4 PRIZES  INTERRUPTABLE*****")
    print('***********************************************************')
    cam.goToTicketTop(True)
    time.sleep(2)
    settings.updateSettings({'filterIds':'','status':'in progress'})

    winningIds = []
    #make a list of all scratch areas
    remaining = list(range(1,len(areas)+1))
    
    #sort areas by group (type)
    #areas = sorted(areas, key=lambda i: i[5])
    #get list of groups and sort them
    groups = sorted(list(set(i[5] for i in areas)))

    sb.moveTo('startingPose')
    sb.zUp()

    #iterate through groups and scratch boxes
    # pause if finish group and there is a p in the group id
    # filter scratches by filter list if an f in group id
    
    for group in groups: 
        print('+++++++++++++++++++++++++++++++++++++++++||')
        print("++++++++++++++++++++++++" + group)
        print('+++++++++++++++++++++++++++++++++++++++++||')
        threadManager.checkPause()
        if threadManager.checkStop():
            break

        if endNow:
            break
        else:
            for area in areas:
                #advance group button in UI
                if nextGroup:
                    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++NEXTGROUP")
                    nextGroup = False
                    break

                threadManager.checkPause()
                if threadManager.checkStop():
                    break
                if endNow:
                    break
                else:
                    if area[5] == group:
                        
                        if 'f' in group:
                            if str(area[8]) in settings.getSett('filterIds').split(','):
                                sb.scratchIt(area)
                                firstScratch = False
                                remaining.remove(area[8])
                                
                        else:
                            sb.scratchIt(area)
                            firstScratch = False
                            remaining.remove(area[8])
                            #wait_for_enter()

                            ###NEW STUFF###
                            #check for filterIds present
                            #scratch all of them then remove from filters
                            if len(settings.getSett('filterIds')) :
                                sb.bugp(f"-0-0-0-0-0 FILTER ID 0-0-0-0-0- {settings.getSett('filterIds')}")
                                scratchThese = settings.getSett('filterIds').split(',')                                
                                for s in scratchThese:
                                    s = int(s)
                                    sb.bugp(f"{type(s)} - {s} in scratchThese")
                                    if s in remaining:
                                        sb.bugp(s)
                                        result = next((row for row in areas if row[8] == s), None)
                                        sb.bugp(result)
                                        sb.scratchIt(result)
                                        
                                        if not settings.getSett('debugging'):
                                            time.sleep(mb.getScratchTimer()/10 + 4)
                                        firstScratch = False
                                        remaining.remove(s)

                                settings.setSett('filterIds', '')
                                sb.bugp(f"FILTER IDS {settings.getSett('filterIds')}")



        
        if not endNow:
            if('p' in group):
                if not cobot.estimateTime:
                    sb.togglePause("in progress")

    
    finshProgram()

def finshProgram():
    print('d')
    time.sleep(2)
    cam.goToBack(False)
    settings.updateSettings({'status':'ready'})
    programComplete = True
    sb.moveTo("home")
    cobot.iszup = False
    cobot.estimateTime = False
    print(f"ESTIMATED TIME: {int(cobot.estimatedTime/10)} minutes")

def advanceToNextGroup():
    global nextGroup
    nextGroup = True


def getScratchedInfo():
    #print('scratch info')
    if settings.getSett('status') in ['in progress', 'paused']:
        return remaining;
    elif programComplete:
        return 'ready'
    else:
       return 'ready'


def wait_for_enter():
    input('Enter to Continue')

def endProgram():
    global endNow
    endNow = True


def getLines():
    return cobot.getLines()