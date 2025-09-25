
import programs
import os
import json

###########################################
#----SETTINGS-----------------------------#
###########################################
## TCP IN COBOT.PY

settingsfile = 'poseData/settings.json'
framefile = 'poseData/frameData.json'
surfaceNormal = [ 0.41031536, -0.64787792, -0.64179085]
pointOnSurface = (0.46656472313293174, -0.07892937674554397, 0.5052424095303475)
#threePoints = [(0.43176485002645376, -0.05524767452877159, 0.5034003288465712), (0.43176331363178594, -0.09726129032332252, 0.5104038792414554), (0.3786170491294491, -0.09723763219630037, 0.48962863812256735)]
threePoints = [(0.35430051837908827, -0.048593740498686755, 0.5257915031036533), (0.42162930213768113, 0.0334994664597813, 0.5488237323888393), (0.35254577135111115, 0.027612748616971574, 0.46746051923457904)]

settings = {}
debugging = 0

ip = "192.168.137.100"

defaultProgram = "scratch by group"
defaultProgram = 'all'
#NEED TO SET FOR EACH TICKET TYPE
#ticket csv
scratchDataOptions = []
currentScratch = 1

#multiple calculated movetime by this number. 1+. the higher, the more chance move will be finished before next one begins
timeMultiplier = 1.1

#difference between leveling plate and bottom of bit
zStartOffset = 29.5

#distance of corner of ticket to start point
#TODO may need offz
offy = -280 #-56 -58 840
offx = -100   #-60 -73 315

#aligner distance from tool center to aligner point
ady = 48.50
adx = 26.2 

#distance of aligner point to startingPoint
alignoffx = 52
alignoffy = 87

#distance of corner of arm base to corner of start point marked on table
#armoffx = 100
#armoffy = 12

#NEED TO SET FOR CHANGES IN CUTTING MACHINE
#width of cutting bit in mm
bitw = 8 # TODO set to bit width
#TOOL center point
#TCP = '(0, 0, 0.1 , 0, 0, 0)'
#overlap of cut passes TODO dial in (may not required)
passOffset = 0

#how far to stop above scrathz before motor startst
moveHeight = -2 #TODO set prep height

#ADJUSTABLE FOR PERFORMANCE
#distance between z height adjustments for inconsistnet bed height LIKELY not required with cobot
movementResolution = 8
#TODO speed
motorSpeed = 300
travelSpeed = 200
travelSpeedCut = 100

###################################################################
###################################################################
ticket_width = 0
ticket_height = 0
ticket_name = 'blank'
ticket_cost = 0

#misc
zadj = 0
#used to estimate time scratch takes to complete
scratchTimer = 0
direction = 1


programStatus = 'ready'
endNow = False
buttons = []

#holder for imported scratch data
scratchArea = []
#_________________#
#    SETTINGS     #
#_________________#

def bugp(s):
    if getSett("bugp"):
        print(s)

def getSettingsData():
    loadSettings()
    return settings

def getTicketFileNames():
    f = os.listdir('scratchData')
    return f

def getTicketNames():
    tickets = []
    files = os.listdir('scratchData')

    for f in files:
        with open('scratchData/' + f, 'r') as data:
            reader = csv.reader(data)
            next(reader) 
            info = next(reader)
            tickets.append(info[0])
    return f

def saveSettings():
    with open(settingsfile, 'w') as f:
        json.dump(settings, f, indent=4)

    

def loadSettings():
    global settings

    with open(settingsfile, 'r') as f:
        settings = json.load(f)
    

def initializeSettings():
    global settings
    global scratchDataOptions
    global currentScratch

    scratchDataOptions = getTicketFileNames()
    currentScratch = scratchDataOptions[currentScratch]

    '''
    settings['debugging'] = {'value':debugging, 'type':'bool'}
    settings['scratchData'] = {'value':currentScratch, 'type':'select',
        'options':scratchDataOptions}
    
    settings['offx'] = {'value':offx, 'type':'float'}
    settings['offy'] = {'value':offy, 'type':'float'}
    settings['alignoffx'] = {'value':alignoffx, 'type':'float'}
    settings['alignoffy'] = {'value':alignoffy, 'type':'float'}
    settings['zStartOffset'] = {'value':zStartOffset, 'type':'float'}
    settings['adx'] = {'value':adx, 'type':'float'}
    settings['ady'] = {'value':ady, 'type':'float'}
    #settings['TCP'] = {'value':TCP, 'type':'string'}
    settings['bitw'] = {'value':bitw, 'type':'float'}
    settings['passOffset'] = {'value':passOffset, 'type':'float'}
    settings['moveHeight'] = {'value':moveHeight, 'type':'float'}
    settings['movementResolution'] = {'value':movementResolution, 'type':'float'}
    settings['motorSpeed'] = {'value':motorSpeed, 'type':'int'}
    settings['travelSpeed'] = {'value':travelSpeed, 'type':'int'}
    settings['travelSpeedCut'] = {'value':travelSpeedCut, 'type':'int'}
    settings['scratchOrder'] = {'value':defaultProgram, 'type':'select', 
        'options':programs.programs}
    settings['ip'] = {'value':ip, 'type':'string'}
    settings['status'] = {'value':programStatus, 'type':'status'}
    settings['filterIds'] = {'value':'', 'type':'string'}
    settings['poses'] = {'value':[], 'type':'buttons'}
    settings['ticket_name'] = {'value':ticket_name, 'type':'info'}
    settings['ticket_cost'] = {'value':ticket_cost, 'type':'info'}
    settings['ticket_width'] = {'value':ticket_width, 'type':'info'}
    settings['ticket_height'] = {'value':ticket_height, 'type':'info'}
    settings['timeMultiplier'] = {'value':timeMultiplier, 'type':'info'}
    settings['surfaceNormal'] = {'value':surfaceNormal, 'type':'info'}
    settings['pointOnSurface'] = {'value':pointOnSurface, 'type':'info'}
    settings['threePoints'] = {'value':threePoints, 'type':'info'}
    saveSettings()
    '''
    print(f"\n\n start:\n{settings}")
    loadSettings()
    getFrameData()

    setSett('status','ready')

    saveSettings()
    
def getFrameData():
    global settings
    with open(framefile, 'r') as f:
        frame = json.load(f)

    setSett('threePoints',frame['points'])
    setSett('surfaceNormal', frame['normal'])


def updateSettings(d):
    print("\r\n\r\n\r\n",d)
    for k,v in d.items():
        setSett(k,v)

    saveSettings()
    print(settings)

def getSett(d):
    return settings[d]['value'];

def getPayload():
    p = settings["payload"]

    return {'weight':p['weight'], 'x':p['x'], 'y':p['y'], 'z':p['z']}

     

def getTCP():
    
    tcp = settings["TCP"]
    t = {}
    t['x'] = tcp['x']
    t['z'] = tcp['z']
    t['y'] = tcp['y']
    t['rx'] = tcp['rx']
    t['rz'] = tcp['rz']
    t['ry'] = tcp['ry']

    return t


def setSett(d, v):
    global settings
    if settings[d]['type'] == "float":
        v = float(v)
    elif settings[d]['type'] == "int":
        v = int(v)
    settings[d]['value'] = v


def setPossiblePoses(p):
    bugp(f"registered  POSES {p}")
    setSett('poses', p)
    saveSettings()

#TODO DO NOT NEED
def setProgramStatus(s):
    setSett('status',s)

def updateGeneralTicketInfo(d):
    for k,v in d.items():
        setSett(k,v)

    saveSettings()
