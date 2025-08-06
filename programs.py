import moneyBadger_GUI as mb
import time

remaining =[]
programComplete = False

programs = ['random', 'numbers before prizes', 'all']

#scracth every area, choosen at random
def doAllRandom(areas):
    global remaining
    global programComplete
    programComplete = False
    print('*****************************************')
    print("***** STARTING PROGRAM : ALL RANDOM *****")
    print('*****************************************')
    mb.setProgramStatus('in progress')
    mb.updateSettings({'filterIds':''})

    #make a list of all scratch areas
    remaining = list(range(0,len(areas)))

    #choose a random area,
    #scratch it
    #remove it from remaining, until remaining is empty
    #sleep may need to be adjusted, seems like a good number, though
    while len(remaining):   
        if mb.endNow:
            remaining = 0
        else:     
            num = random.choice(remaining)
            print("========== Cutting # ::: " + str(num) + " ::: ==========")
            mb.scratchIt(areas[num])
            mb.wait()
            remaining.remove(num)
            #time.sleep(mb.getScratchTimer()/10 + 4)
            time.sleep(10)
            mb.setFirstScratch(False)

    mb.tryHome()
    mb.setProgramStatus('ready')
    programComplete = True

def scratchAllInOrder(areas):
    global remaining
    global programComplete
    programComplete = False
    print('*******************************************')
    print("***** STARTING PROGRAM : ALL IN ORDER *****")
    print('*******************************************')
    mb.setProgramStatus('in progress')
    mb.updateSettings({'filterIds':''})

    #make a list of all scratch areas
    remaining = list(range(0,len(areas)))

    #choose a random area,
    #scratch it
    #remove it from remaining, until remaining is empty
    #sleep may need to be adjusted, seems like a good number, though
    for num in range(0,len(areas)):
        if mb.endNow:
            break
        else:
            print("========== Cutting # ::: " + str(num) + " ::: ==========")
            mb.scratchIt(areas[num])
            mb.wait()
            time.sleep(mb.getScratchTimer()/10 + 4)
            #time.sleep(10)
            mb.setFirstScratch(False)
            remaining.remove(num)

    mb.tryHome()
    mb.setProgramStatus('ready')
    programComplete = True

def scratchNumbersBeforePrizes(areas):
    global remaining
    global programComplete
    programComplete = False
    print("*********************************************")
    print("***** STARTING PROGRAM : NUMS B4 PRIZES *****")
    print('*********************************************')
    mb.setProgramStatus('in progress')
    mb.updateSettings({'filterIds':''})
    winningIds = []
    #make a list of all scratch areas
    remaining = list(range(1,len(areas)+1))
    
    #sort areas by group (type)
    #areas = sorted(areas, key=lambda i: i[5])
    #get list of groups and sort them
    groups = sorted(list(set(i[5] for i in areas)))

    #iterate through groups and scratch boxes
    # pause if finish group and there is a p in the group id
    # filter scratches by filter list if an f in group id
    for group in groups: 
        print('+++++++++++++++++++++++++++++++++++++++++||')
        print("++++++++++++++++++++++++" + group)
        print('+++++++++++++++++++++++++++++++++++++++++||')
        mb.checkPause()

        if mb.endNow:
            break
        else:
            for area in areas:
                if mb.endNow:
                    break
                else:
                    if area[5] == group:
                        
                        if 'f' in group:
                            if str(area[8]) in mb.getSett('filterIds').split(','):
                                mb.scratchIt(area)
                                mb.wait()
                                if not mb.getSett('debugging'):
                                    time.sleep(mb.getScratchTimer()/10 + 4)
                                mb.setFirstScratch(False)
                                remaining.remove(area[8])
                                
                        else:
                            mb.scratchIt(area)
                            mb.wait()
                            if not mb.getSett('debugging'):
                                    time.sleep(mb.getScratchTimer()/10 + 4)
                            mb.setFirstScratch(False)
                            remaining.remove(area[8])
                        #wait_for_enter()


        if not mb.endNow:
            if('p' in group):
                #print("+++++++++++++++++++++++++++++++++ p in group")
                mb.togglePause()

    mb.tryHome()
    time.sleep(5) #give time for front end to update
    mb.setProgramStatus('ready')
    programComplete = True

def wait_for_enter():
    input('Enter to Continue')