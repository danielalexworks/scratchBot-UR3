import csv
import settings
import programs
import json


lines = []
currentTicket = {}
scratchAreas = []
#read scratch data from csv
#translate into urx mm
def gatherScratchData(filename):
    global currentTicket, scratchAreas
    l = []
    with open('scratchData/' + filename, 'r') as f:
        reader = csv.reader(f)
        #general ticket info
        labels = next(reader) 
        info = next(reader)
        for i in range(0,len(labels)):
            if labels[i] != '' and info[i] != '':
                currentTicket[labels[i].replace(" ","_")] = info[i]
        #skip scratch box labels
        next(reader)
        for r in reader:
            r[1] = float(r[1]) #/ 100
            #r[0] = -1 * float(r[0])  #/ 100
            r[0] = float(r[0])  #/ 100
            #r[2] = float(r[2]) / 100

            #r[3] = float(r[3]) / 100

            l.append([int(i) if idx not in [4,5] else i for idx, i in enumerate(r)])

    settings.bugp(currentTicket)
    settings.updateGeneralTicketInfo(currentTicket)
    scratchAreas = l
    #print(scratchAreas)
    return l


def getTicketInfo():
    #print("++++++++++++++++++++++")
    data = {}
    t = gatherScratchData(settings.getSett('scratchData'))
    data['boxes'] = t
    n = settings.getSett('ticket_name')
    w = settings.getSett('ticket_width')
    h = settings.getSett('ticket_height')
    data['ticket_info'] = {'ticket_name':n, 'ticket_width':w, 'ticket_height':h}
    #print("----")
    #print("RETURNED TICKET INFO")
    return json.dumps(data)




