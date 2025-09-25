import threading
import programs
import settings
import asyncio
import websockets
import json

pauseEvent = threading.Event()
stop_event = threading.Event()
task_thread = None
socket_thread = None


def isPaused():
    if(settings.getSett('status') == 'paused') :
        return True
    else:
        return False

def pauseThread():
    pauseEvent.clear()
    settings.setSett('status','paused')
    print("THREAD PAUSED---")

def stopThread():
    stop_event.clear()
    settings.setSett('status','ready')
    print('PROGRAM / THREAD STOPPED')

def unpauseThread():
    pauseEvent.set()
    settings.setSett('status', 'in progress')

def checkPause():
    pauseEvent.wait()

def checkStop():
    return stop_event.is_set()
    

def startProgram(program, scratchArea):
    global task_thread
    global socket_thread

    if task_thread and task_thread.is_alive():
        print("Stopping existing thread...")
        stop_event.set()  # Signal the thread to stop
        task_thread.join()  # Wait for the thread to finish
        if socket_thread and socket_thread.is_alive():
            print("Stopping existing ws thread...")
            socket_thread.join()  # Wait for the thread to finish

    if(program == 'all'):
        task_thread = threading.Thread(target=programs.scratchAllInOrder, args = (scratchArea,))
        
    elif(program == 'random'):
        task_thread = threading.Thread(target=programs.doAllRandom, args = (scratchArea,))
        
    elif(program == 'scratch by group'):
        task_thread = threading.Thread(target=programs.scratchByGroup, args = (scratchArea,))

    elif(program == 'scratch by group interruptable'):
        task_thread = threading.Thread(target=programs.scratchByGroupInterruptable, args = (scratchArea,))
        

    task_thread.daemon = True  # Make the thread exit when the main program exits
    task_thread.start()
   
    startWebSocketThread()

    settings.setSett('status','in progress')
    pauseEvent.set()


def togglePause(status = 'none'):
    if status == 'none':
        status = settings.getSett('status')
    if status == 'in progress':
        settings.setSett('status','paused')
        pauseThread()
    elif status == 'paused':
        settings.setSett('status','in progress')
        unpauseThread()


#+++++++++++++++++++++++++       WEBSOCKET
#sends lines to GUI if any new ones are created
oldlines = []
async def websocket_handler(websocket, path):
    global oldlines
    while True:# not checkPause():
        lines = programs.getLines()
        scratched = programs.getScratchedInfo() 
        payload = {'lines': lines,'scratched' :  scratched}
        if len(lines) > 0:
            await websocket.send(json.dumps(payload))

        await asyncio.sleep(2)
        


def run_websocket_server():
    print("|+++++++++++++++++++++++++++++++++++")
    print("|+++++++++++++++++++++++++++++++++++")
    print("|+++++++++++++++++++++++++++++++++++")
    print('..starting ws server')
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    ws_server = websockets.serve(websocket_handler, '0.0.0.0', 8765)
    loop.run_until_complete(ws_server)
    loop.run_forever()


def startWebSocketThread():

    ws_thread = threading.Thread(target=run_websocket_server)
    ws_thread.daemon = True
    ws_thread.start()
    return ws_thread