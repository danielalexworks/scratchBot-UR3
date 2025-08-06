import math
import csv

#import z offsets for unlevel bed
with open('scratchData/offsets.csv', newline='') as f:
    zoffs = list(csv.reader(f))
print(zoffs)


def getZoff(tx,ty, xoff, yoff, tz):
    #100 x 280
    global zoffs
    
    x = tx - xoff
    y = ty - yoff

    #if above the ticket
    #if ty < yoff and tx < xoff and tz != 0:
    if int(tz) != 0:
        #print("txty: "+ str(x) + ',' + str(y))
        #print("[][]: " + str(abs(math.floor((tx-xoff)/10))) + ',' + str(abs(math.floor((ty-yoff)/10))))

        # how far traveled - distance to ticket = how far on ticket 
        # how far on ticket / 10 = [x][]
        #print(zoffs[abs(math.floor((tx-xoff)/10))][abs(math.floor((ty-yoff)/10))])
        xloc = abs(math.floor((tx-xoff)/10))
        yloc = abs(math.floor((ty-yoff)/10))
        if len(zoffs) > xloc:
            if len(zoffs[xloc]) > yloc:
                return zoffs[xloc][yloc]
            else:
                return 0
        else: 
            return 0
    else:
        #print("----txty: "+ str(x) + ',' + str(y))
        #return 0
        return tz

