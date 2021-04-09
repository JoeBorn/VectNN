'''copyright 2021 Joe Born
all rights reserved '''
#import cs112_s21_week4_linter
from cmu_112_graphics import *
import random, string, math, time
import PIL, copy
from PIL import Image 
import decimal
import csv
import glob


#img.show()
def appStarted(app):
    app.contigLinesVisible = True
    app.oneContigVis = False
    app.rows = 28 # a row and col for each pixel 
    app.cols = 28 # a row and col for each pixel 
    app.selCol = 0
    app.selRow = 0
    app.margin = 100
    app.offset = app.margin + 10 # from 0,0 to the center of a cell
    app.ends = []
    app.bends = []
    variables(app)
    openFile(app)
    #findEnds(app) #TODO this sure shouldn't be here, but where?
    #getMidPoints(app)
    #getTrace(app)

def openFile(app):
    for i in range(2,10):
        path = f'C:/mnist/mnist_all_files/testing/{i}/'
        for filename in glob.glob(os.path.join(path, '*.png')):
            with open(os.path.join(os.getcwd(), filename), 'r') as f: # open in readonly mode
                app.img = Image.open(filename)
                #print(filename)
                findEnds(app)
                getTrace(app)
                
            with open('mnist_1_testing.csv', newline='',mode='a') as csvfile: # https://realpython.com/python-csv/#:~:text=Reading%20from%20a%20CSV%20file,which%20does%20the%20heavy%20lifting.
                traceWriter = csv.writer(csvfile, delimiter=',') # delimiter here means what it writes to delimit 
                traceWriter.writerow(traceConverter(i,app))
    print(f"done! no {i}")

def traceConverter(i,app):
    result = [i]
    for item in app.trace:
        if item != "gap":
            (x,y) = item
            result.append(x)
            result.append(y)
    return result


def variables(app):
    app.pixWH = (app.width - 2*app.margin)//app.cols
    app.threshold = 120 # lightness threshold to determine edges of chars
    #0 is black, 255 is white, on pngs, letters are light on black background

def roundHalfUp(d):
    # Round to nearest with ties going away from zero.
    rounding = decimal.ROUND_HALF_UP
    # See other rounding options here:
    # https://docs.python.org/3/library/decimal.html#rounding-modes
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))

#grid details derived from: https://www.cs.cmu.edu/~112/notes/notes-animations-part2.html
def pointInGrid(app,x,y):
    return ((app.margin <= x <= app.width - app.margin) and \
        (app.margin <= y <=app.height -app.margin))

def mousePressed(app, event):
    app.selCol, app.selRow = getGridCoords(app,event.x,event.y)

def getGridCoords(app,x,y): #view to model
    if not pointInGrid(app,x,y):
        return (-1,-1)
    col = int((x-app.margin)/app.pixWH)
    row = int((y-app.margin)/app.pixWH)
    return col, row
    
def getCellUpperLeft(app,row, col):#model to view
    x1 = app.margin + col*app.pixWH
    y1 = app.margin + row*app.pixWH
    return(x1,y1)

def drawSelection(app, canvas):
    (x1,y1) = getCellUpperLeft(app,app.selRow, app.selCol)
    canvas.create_rectangle(x1,y1,x1+app.pixWH,y1+app.pixWH, width= 3, fill = None)

def keyPressed(app, event):
    if event.key.lower() == 'space':
        app.contigLinesVisible = not app.contigLinesVisible
def keyPressed(app, event):
    if event.key.lower() == 'o':
        app.oneContigVis = not app.oneContigVis        

def getMidPoints(app): #finds the midpoints, taking horizontal slices
    pixels = list(app.img.getdata()) # returns one long flattened list: row1, row2, etc
    (width, height) = app.img.size #28,28 TODO: is this a global?
    leadEdge = 0
    vertThreshold = 5 # length of vertical segment to break up with multi points
    midsImageList = list() #a list that collects the midpoint pixels into a format PIL can create a PNG, etc
    midsList = list() # a list of the coordinate tuples of the midpoints
    outlineList = list() # list of leading and trailing edges, should form an outline
    for i in range(width*height):
        midsImageList.append(255) # 255 is white
    for x in range(width):
        for y in range(height):
            if pixels[getIndex(x,y)] > app.threshold and leadEdge == 0: 
                leadEdge = y # leading edge found
            if pixels[getIndex(x,y)] <= app.threshold and leadEdge != 0: #trailing edge found
                #TODO remove single pixel "turds"
                trailEdge = y-1 #TODO: Check, but I think because <= app.threshold
                if abs(leadEdge-trailEdge) > vertThreshold:
                    midpoint = leadEdge + 1
                    #del midsImageList[getIndex(x,midpoint)] #TODO: is this still needed?
                    #clean up if not
                    #midsImageList.insert(getIndex(x,midpoint), 0)
                    midsList.append((x,midpoint))
                    midpoint = trailEdge -1
                    #del midsImageList[getIndex(x,midpoint)]
                    #midsImageList.insert(getIndex(x,midpoint), 0)
                    midsList.append((x,midpoint))
                else:
                    midpoint = round((leadEdge + trailEdge)/2)
                    midsList.append((x,midpoint))# 
                for y in range (leadEdge,y):
                    outlineList.append((x,y))# because <=THRESHOLD trigger
                #print("x,y,m: ",x,y,midpoint, end = "__")
                leadEdge = 0      
    return midsImageList, midsList,outlineList

#gets index out of a flattened list given x and y coords of the image
#list stores pixels by rows, starting with top
def getIndex(x,y, width=28):
    i = (y-1)*width + x-1
    return i

def getEndsBends(app):
    minDist = 10**10
    if app.ends != []:
        for (col,row) in app.ends:
            #print("tempAppEnds: ", app.ends)
            dist = math.sqrt(row**2 + col**2)
            if dist < minDist:
                minDist = dist
                (startCol, startRow) = (col,row)
        app.ends.remove((startCol,startRow))
        return (startCol, startRow)
    #if no end, start with the bend closest to 0,0
    elif app.bends != []:
        for (col, row) in app.bends:
            dist = math.sqrt(row**2 + col**2)
            if dist < minDist:
                minDist = dist
                (startCol, startRow) = (col,row)
        app.bends.remove((startCol,startRow))# mistake- this removes each end in order (or should anyway)
        return (startCol, startRow)
    else: return (None, None)

def getTrace(app):
    app.trace = []
    #start with the end closest to 0,0
    (startCol, startRow) = getEndsBends(app)
    app.trace.append((startCol, startRow))
    #connect to farthest contiguous point
    midsImageList, midsList, outlineList = getMidPoints(app)# TODO eliminate all the calls to gMP, put midslist etc in app...
    while len(midsList) > 1:
        traceIndex = app.trace.index((startCol,startRow))
        #print ("ML prior: ", midsList)
        maxDistance = 0
        for index in range(len(midsList)):
            if (startCol,startRow) == (None,None): break #TODO Fix
            if areContiguous(app,(startCol, startRow),midsList[index]):
                (x,y) = midsList[index] #TODO: pick one, it's either row, col or x,y
                if traceIndex == 0 or app.trace[traceIndex-1] == 'gap':
                    dist = math.sqrt((startCol - x)**2 +(startRow - y)**2)
                else:
                    (priorX,priorY)= app.trace[traceIndex - 1]
                    dist = math.sqrt((priorX - x)**2 +(priorY - y)**2)
                if dist > maxDistance:
                    maxDistance = dist
                    (endX, endY) = (x,y)
                    #print("endX,endY", x,y)
        if maxDistance >= 1: app.trace.append((endX,endY))
        if (startCol,startRow) in midsList: midsList.remove((startCol,startRow))
        index = 0
        while index < (len(midsList)): #removes intermediate points from ML
            if (startCol,startRow) == (None,None): break #TODO Fix
            if areContiguous(app,(startCol, startRow),midsList[index]) and \
                areContiguous(app, (endX,endY), midsList[index]):
                (x,y) = midsList[index]
                if traceIndex == 0 or app.trace[traceIndex -1] == "gap":
                    dist = math.sqrt((startCol - x)**2 +(startRow - y)**2)
                else:
                    (priorX,priorY)= app.trace[traceIndex - 1]
                    dist = math.sqrt((priorX - x)**2 +(priorY - y)**2)
                #print ("x,y,dist: ", x,y,dist, end = " ")
                if dist <= maxDistance:
                    midsList.pop(index)
                    if (x,y) in app.ends: app.ends.remove((x,y))
                    if (x,y) in app.bends: app.bends.remove((x,y))
                else: index += 1
            else: index += 1
        if (startCol,startRow) != (endX,endY): # it found a new connection point
            (startCol,startRow) = (endX,endY)
        else: #failing that, make sure all ends/bends are connected
            (startCol,startRow)= getEndsBends(app)
            if (startCol,startRow) == (None,None): break #if ends/bends gone,we're done
            #TODO: sometimes, leaves ends unconnected, see notes on 4/336.png
            else:
                app.trace.append("gap") 
                app.trace.append((startCol, startRow))
        if (endX,endY) in midsList: midsList.remove((endX,endY))
        #print("app.trace", app.trace)
        #print("ML after: ",midsList)
        #input("press any key")
    if areContiguous(app,app.trace[0],app.trace[-1]):
        app.trace.append(app.trace[0]) #closing the loop on closed chars
    #print (app.trace) 

    # delete all midpoints "passed"
    #"passed" means closer to the from mid point and contiguous to both
    #from chosen point choose farthest contiguous point (ignoring all skipped points)
    #done when no midpoints are left (either because they were chosen or skipped)


#takes original "image" list and two midpoints(tuple with two ints(row and column coords)) 
# and returns if they are contiguous
#presumes that columns aren't more than one apart
def areContiguous(app,mid1,mid2): 
    app.pixels = list(app.img.getdata()) 
    (x1,y1) = (mid1[0], mid1[1])
    (x2,y2) = (mid2[0], mid2[1])
    largestX = max(x1,x2)
    smallestX = min(x1,x2)     
    if abs(x1-x2) > 1 and abs(y1-y2) > 1: 
        m = (y2-y1)/(x2-x1) # m is the slope
        b = y1+.5 -m*(x1+.5) # b is the y intercept
        for row in range(min(y1,y2),max(y1,y2)+1):
            xStart = (row-b)/m
            xEnd = (row +1-b)/m
            xMin = max(smallestX,int(min(xStart,xEnd)))
            xMax = min(largestX,roundHalfUp(max(xStart,xEnd)))# frankly I'm not sure why
            # int works here, I would have thought math.ceil, but it works 
            # and has to do with simple counting
            xMid = (xMin + xMax)//2
            #requiring the char pixel in xMid is the more restrictive case, but 
            #seems to work ok.
            if app.pixels[getIndex(xMid,row)] < app.threshold:
                return False
    if not isConnected(app, mid1,mid2):
        return False 
    return True

def isConnected(app,mid1,mid2):  
    (x1,y1) = (mid1[0], mid1[1])
    (x2,y2) = (mid2[0], mid2[1])
    if abs(x1-x2)==1 and abs(y1-y2)==1: #by definition so to speak
        return True
    elif x1 == x2:
        for row in range(min(y1,y2),max(y1,y2)+1):
            if app.pixels[getIndex(x1,row)] < app.threshold: #gap found
                return False
        return True
    elif y1 == y2:
        for col in range(min(x1,x2),max(x1,x2)+1):
            if app.pixels[getIndex(col, y1)] < app.threshold: #gap found
                return False
        return True
    else:
        #print("rec coords: ", x1,y1,x2,y2)
        if x2 > x1: dx = 1
        elif x1 > x2: dx = -1
        else: dx = 0
        if y2 > y1:dy = 1
        elif y1 > y2:dy = -1
        else: dy = 0
        if app.pixels[getIndex(x2,y2-dy)] > app.threshold and isConnected(app,(x1,y1),(x2,y2-dy)):
            return True
        elif app.pixels[getIndex(x2-dx,y2)] > app.threshold and isConnected(app,(x1,y1),(x2-dx,y2)):
            return True
        else:
            return False    

def contiguousPairs(app,midsList):
    contMidStart = list()
    contMidEnd = list()
    maxConnections = 100 #TODO: think about this.effectively eliminated for now 
    #max no of pairs to "connect to" allowed  
    #(doubled by prior "smaller" coords with their own connection allocation)
    for coord1 in range (len(midsList)):
        connections = 0
        for coord2 in range(len(midsList)):
            if connections <= maxConnections and coord1 != coord2 and \
                areContiguous(app,midsList[coord1], midsList[coord2]):
                contMidStart.append(midsList[coord1])
                contMidEnd.append(midsList[coord2])
                connections += 1
    return (contMidStart, contMidEnd)
'''
print("\n contiguousPairs: +++++++++++++++++")
(contMidStart, contMidEnd) = contiguousPairs(midsList, img)
for i in range(len(contMidStart)):
    print(contMidStart[i], contMidEnd[i])
'''
def drawMidPoints(app, canvas):
    canvas.create_rectangle(100,100, 380,380)
    midsImageList, midsList, outlineList = getMidPoints(app)
    for coords in midsList:
        ((x,y))=coords
        x=105+x*20
        y=105+y*20
        canvas.create_rectangle(x,y,x+10,y+10, fill="gray")

def drawGrid(app, canvas):
    rEdge = app.width - app.margin + 1
    bEdge = app.height - app.margin + 1
    for x in range(app.margin,rEdge, app.pixWH):
        canvas.create_line(x,app.margin,x,bEdge)
    for y in range(app.margin,bEdge, app.pixWH):
        canvas.create_line(app.margin,y,rEdge,y)
    for x in range(app.margin,rEdge, app.pixWH*5):
        canvas.create_line(x,app.margin,x,bEdge, width = 2)
    for y in range(app.margin,rEdge, app.pixWH*5):
        canvas.create_line(app.margin,y,bEdge,y, width = 2)
    canvas.create_text(100,700, text =f'sel Coord(row,col) : {app.selRow} , {app.selCol}')

def drawOutline(app, canvas):
    canvas.create_text(100,50, text=f'Threshold: {app.threshold}    {file}', font='Courier 11 bold', anchor = 'w')
    midsImageList, midsList, outlineList = getMidPoints(app)
    for coords in outlineList:
        ((x,y))=coords
        x=100+x*20
        y=100+y*20
        canvas.create_rectangle(x,y,x+20,y+20, fill ="lightgray")

def drawContiguousConnections(app, canvas):
    midsImageList, midsList, outlineList = getMidPoints(app)
    if app.contigLinesVisible == True: #TODO: something wrong here 
        (contMidStart, contMidEnd) = contiguousPairs(app,midsList)
        for i in range(len(contMidStart)):
            (x1,y1) = contMidStart[i]
            (x1,y1) = app.offset + x1*20, app.offset + y1*20 
            (x2,y2) = contMidEnd[i]
            (x2,y2) = app.offset + x2*20, app.offset + y2*20
            if app.oneContigVis == True:
                (xs,ys) = getCellUpperLeft(app,app.selRow, app.selCol)
                (xs,ys) = (xs+10,ys+10)
                if app.selRow == 0 and app.selCol == 0: 
                    canvas.create_line(x1,y1,x2,y2, fill = "red", width =2)
                elif (x1 == xs) and (y1 == ys): 
                    canvas.create_line(x1,y1,x2,y2, fill = "red", width =2)
                
def drawEnds(app, canvas):
    for (col,row) in app.ends: # TODO fix this to match row, col convention
        x = app.offset + col*20
        y = app.offset + row*20
        r = 15
        canvas.create_oval(x-r,y-r,x+r,y+r, width = 4, outline = "green", fill = None)

def drawBends(app, canvas): # TODO fix this to match row, col convention
    for (col,row) in app.bends:
        x = app.offset + col*20
        y = app.offset + row*20
        r = 15
        canvas.create_oval(x-r,y-r,x+r,y+r, width = 4, outline = "blue", fill = None)

def findEnds(app):
    ''' go through all the midpoints & apply two part test: 1 end has all 
    connected points in "one direction", ie up down, left, right etc &
    2. those connected points must be connected to one another '''
    midsImageList, midsList, outlineList = getMidPoints(app)
    (contMidStart, contMidEnd) = contiguousPairs(app,midsList) #copied from drawContiguousConnections
    app.ends = []
    app.bends = []
    i = 1 #TODO missing the last midpoint? first, it's missing something
    allRorL = True # all contMidEnds are on one side of contMidStart
    allUorD = True # all contMidEnds are above or all are below contMidStart
    allConnected = True
    while i < len(contMidStart):
        if contMidStart[i] != contMidStart[i-1] or i == len(contMidStart)-1:
            if (allRorL or allUorD):
                if not allConnected:
                    app.bends.append(contMidStart[i-1])
                else: # if it has only one pair, it's an end
                    app.ends.append(contMidStart[i-1]) 
            i += 1
            allRorL = True # reset checks
            allUorD = True
            allConnected = True 
        else: #if it's an additional mid connection then perform the checks.
            (x1,y1) = contMidStart[i] 
            (x2,y2) = contMidEnd[i-1]
            (x3,y3) = contMidEnd[i]
            if (x2-x1)*(x3-x1) <= 0: 
                allRorL = False #they aren't all to one side
            if (y2-y1)*(y3-y1) <= 0:
                allUorD = False #they aren't all above (or below)
            if not areContiguous(app,(x2,y2),(x3,y3)):
                allConnected = False #the connections aren't connected to each other
                # ie it's not an end, just a side of a curve, a "bend"
            i += 1
        
    #print ("app.ends: ", app.ends)

def drawTrace(app, canvas):
    for i in range(1,len(app.trace)):
        if app.trace[i-1] != "gap" and app.trace[i] !="gap":
            (x1,y1) = app.trace[i-1]
            (x1,y1) = app.offset + x1*20, app.offset + y1*20 
            (x2,y2) = app.trace[i]
            (x2,y2) = app.offset + x2*20, app.offset + y2*20
            canvas.create_line(x1,y1,x2,y2, fill ="orange", width = 3)


def timerFired(app):
    variables(app)
    findEnds(app)

'''
def redrawAll(app, canvas):
    drawGrid(app,canvas)
    drawOutline(app, canvas)
    drawMidPoints(app, canvas)
    drawEnds(app, canvas)
    drawBends(app, canvas)
    drawSelection(app, canvas)
    drawTrace(app, canvas)
    drawContiguousConnections(app, canvas)
'''    
 

def main():
    #cs112_s21_week4_linter.lint()
    runApp(width=760, height=760)
    

if __name__ == '__main__':
    main()




















