import threading
import programs
import moneyBadger_GUI as mb

pauseEvent = threading.Event()

def isPaused():
    if(mb.getSett('status') == 'paused') :
        return True
    else:
        return False

def pauseThread():
    
    pauseEvent.clear()
    mb.setSett('status','paused')
    print("THREAD PAUSED---")

def unpauseThread():
    
    pauseEvent.set()
    mb.setSett('status', 'in progress')

def checkPause():
    pauseEvent.wait()
    

def startProgram(program, scratchArea):
    
    if(program == 'all'):
        task_thread = threading.Thread(target=programs.scratchAllInOrder, args = (scratchArea,))
        #programs.scratchAllInOrder(scratchArea)
    elif(program == 'random'):
        task_thread = threading.Thread(target=programs.doAllRandom, args = (scratchArea,))
        #programs.doAllRandom(scratchArea)
    elif(program == 'numbers before prizes'):
        task_thread = threading.Thread(target=programs.scratchNumbersBeforePrizes, args = (scratchArea,))
        #programs.scratchNumbersBeforePrizes(scratchArea)

    task_thread.daemon = True  # Make the thread exit when the main program exits
    task_thread.start()
    mb.setSett('status','in progress')
    pauseEvent.set()