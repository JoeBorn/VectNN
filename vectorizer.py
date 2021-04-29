'''copyright 2021 Joe Born
all rights reserved '''
#import cs112_s21_week4_linter
from cmu_112_graphics import *
from vnn_TF import *
from vnn_fileParser import *
import math
from PIL import Image 
import decimal
import csv
import glob

def appStarted(app):
    app.picHeight = 28 # a y and x for each pixel 
    app.picWidth = 28 # a y and x for each pixel 
    app.selX = 0
    app.selY = 0
    app.margin = 100
    app.botMargin = 300
    app.mouseMovedDelay = 10
    app.offset = app.margin + 10 # from 0,0 to the center of a cell
    app.file = 'C:/mnist/mnist_all_files/training/8/17.png'  
    app.img = Image.open(app.file)
    app.pixels = list(app.img.getdata())
    app.drawingMode = None
    app.midPointsOn = True
    app.endsBendsOn = True
    app.traceOn = True
    app.contPath = "one"
    app.markerActive = False
    app.eraserActive = False
    app.predictionMade = False
    app.imageDisplay = "original"
    app._root.resizable(False, False)
    app.network = "VNN"
    variables(app)
    findEnds(app) #TODO 
    getMidPoints(app)
    getTrace(app)

    #createStandardCSVFile(app)
    #trainNN(app)
    #makeStandardPrediction(app)
    #createStandardCSVFile(app)


def traceConverter(app, i=0):
    hasGap = False
    result = [i] + [0]*26
    if app.trace[0] == app.trace[-1]: result[1] = 28 #closed feature
    for i in range(min(len(app.trace), 12)): #truncates at 25 (w/o gap)
        if app.trace[i] != "gap":
            if hasGap == False:
                (x,y) = app.trace[i]
                result[2*i+2] =x
                result[2*i+3] =y 
            else: #new segment will start at index 25, proving a fixed point to NN
                (x,y) = app.trace[i]
                result.append(x)
                result.append(y)
        else: 
            hasGap = True
            if app.trace[i-1] == app.trace[0]:
                result[1] = 28 # add "closed" feature to array
    return result[:36]

#84% validation accuracy with 100 epochs
def traceThetaConverter(app, i=0):
    dist1 = distance(app.trace[0],(0,0))
    angle1 = getSortOfAngle((-1,0),(0,0),app.trace[0])
    dist2 = distance(app.trace[1],app.trace[0])
    angle2 = getSortOfAngle((0,0),app.trace[0],app.trace[1])
    result = [i] + [0]+ [dist1]+[angle1]+[dist2]+[angle2]+[0]*19
    if app.trace[0] == app.trace[-1]: result[1] = 28 #closed feature 
    hasGap = False
    i = 2
    while i <min(len(app.trace), 12): #truncates at 12 (w/o gap)
        if app.trace[i] != "gap":
            if app.trace[i-1] != "gap" and app.trace[i-2] != "gap":
                angle = getSortOfAngle(app.trace[i-2],app.trace[i-1],app.trace[i])
                dist = distance(app.trace[i-1],app.trace[i])
                if hasGap == False:
                    result[2*i] = dist
                    result[2*i+1] = angle
                else: #new segment will start at index 25, proving a fixed point to NN
                    result.append(dist)
                    result.append(angle)
            i += 1
        else: 
            hasGap = True
            startingPoint = True
            if app.trace[i-1] == app.trace[0]:
                result[1] = 28 # add "closed" feature to array
            if i+2<len(app.trace) and app.trace[i+1] != "gap" and app.trace[i+2] != "gap":
                dist1 = distance(app.trace[i+1],(0,0))
                angle1 = getSortOfAngle((-1,0),(0,0),app.trace[i+1])
                dist2 = distance(app.trace[i+1],app.trace[i+2])
                angle2 = getSortOfAngle((0,0),app.trace[i+1],app.trace[i+2])
                result.extend([dist1,angle1,dist2,angle2])
            i +=3 
    return result[:36]


# returns an "angle" value 0 and 10*Pi between two head to tail vectors 
def getSortOfAngle(coord1,coord2,coord3):
    x1,y1 = coord1
    x2,y2 = coord2
    x3,y3 = coord3
    sign = -1
    if isLeft(coord1,coord2,coord3): sign = 1
    angle = math.pi+sign*(math.acos(((x2-x1)*(x3-x2)+(y2-y1)*(y3-y2))
    /(math.sqrt((x2-x1)**2+(y2-y1)**2)
    *math.sqrt((x3-x2)**2+(y3-y2)**2))))
    return angle*5

#https://stackoverflow.com/questions/1560492/how-to-tell-whether-a-point-is-to-the-right-or-left-side-of-a-line
def isLeft(coord1,coord2,coord3):
    x1,y1 = coord1
    x2,y2 = coord2
    x3,y3 = coord3
    return ((x2 - x1)*(y3 - y1) - (y2 - y1)*(x3 - x1)) > 0

def makePrediction(app):    
    writeSample(app)
    prediction = predictSample(app).tolist()
    app.prediction = prediction
    app.predNum = prediction.index(max(prediction))
    app.confidence = int(max(prediction)*100)
    app.predictionMade = True

def makeStandardPrediction(app):    
    writeStandardSample(app)
    prediction = predictStandard(app).tolist()
    print("standard prediction")
    print(prediction)
    print(prediction.index(max(prediction)))
    print("confidence: ",int(max(prediction)*100))    
    app.confidence = int(max(prediction)*100)
    app.predictionMade = True
    app.prediction = prediction
    app.predNum = prediction.index(max(prediction))
    app.confidence = int(max(prediction)*100)
    app.predictionMade = True  
    
def variables(app):
    app.pixW = (app.width - 2*app.margin)//app.picWidth
    app.pixH = (app.height - app.margin -app.botMargin)//app.picHeight
    app.threshold = 120 # lightness threshold to determine edges of chars
    #0 is black, 255 is white, on pngs, letters are light on black background

#https://www.cs.cmu.edu/~112/notes/notes-variables-and-functions.html#RecommendedFunctions.
def roundHalfUp(d):
    # Round to nearest with ties going away from zero.
    rounding = decimal.ROUND_HALF_UP
    # See other rounding options here:
    # https://docs.python.org/3/library/decimal.html#rounding-modes
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))

def openFile(app):
    #https://stackoverflow.com/questions/3579568/choosing-a-file-in-python-with-simple-dialog
    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    app.file = filedialog.askopenfilename() # show an "Open" dialog box and return the path to the selected file
    app.img = Image.open(app.file)
    app.pixels = list(app.img.getdata())
    findEnds(app) #TODO 
    getMidPoints(app)
    getTrace(app)
    app.predictionMade = False

def saveFile(app):
    #https://pythonbasics.org/tkinter-filedialog/
    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    app.newFile = filedialog.asksaveasfilename() # show an "Open" dialog box and return the path to the selected file
    savedImg =Image.new("L",(28,28))
    savedImg.putdata(app.pixels)
    savedImg.save(app.newFile)

#grid details derived from: https://www.cs.cmu.edu/~112/notes/notes-animations-part2.html
#outer pixels are not part of the mnist dbase, so they are excluded here too
def pointInGrid(app,x,y):
    return ((app.margin + 2*app.pixW <= x <= app.width - app.margin - 2*app.pixW) and \
        (app.margin + 2*app.pixH <= y <=app.height -app.botMargin - 2*app.pixH))

def sizeChanged(app):
    variables(app)

def mousePressed(app, event):  
    if pointInGrid(app,event.x,event.y):
        app.selX, app.selY = getGridCoords(app,event.x,event.y)
        if app.markerActive:
            index = getIndex(app.selX,app.selY)
            app.pixels[index]= 250 # sets pixel to an arbitrary "dark" value
        if app.eraserActive:
            index = getIndex(app.selX,app.selY)
            app.pixels[index]= 2 # sets pixel to an arbitrary "light" value
    elif .18*app.width<event.x<.27*app.width and .028*app.height<event.y<.071*app.height:
        makeStandardPrediction(app)
    elif .55*app.width<event.x<.76*app.width and .73*app.height<event.y<.78*app.height:
        drawingButtonPressed(app, event.x,event.y)
    elif .05*app.width<event.x<.15*app.width and .75*app.height<event.y<.88*app.height:
        fileButtonPressed(app,event.x,event.y)
    elif .19*app.width<event.x<.9*app.width and .88*app.height<event.y<.96*app.height:
        visualizationButtonPressed(app,event.x,event.y)

def drawingButtonPressed(app,x,y):
    #clear button
    if .55*app.width<x<.60*app.width and .73*app.height<y<.78*app.height:
        app.pixels = [2 for i in range(784)]
        app.trace = []
        app.ends, app.bends = [], []
    #erase button
    if .63*app.width<x<.67*app.width and .73*app.height<y<.78*app.height:
        app.eraserActive = not app.eraserActive
        app.markerActive = False
    #marker button
    if .71*app.width<x<.75*app.width and .73*app.height<y<.78*app.height:
        app.markerActive = not app.markerActive
        app.eraserActive = False

def fileButtonPressed(app,x,y):
    if .05*app.width<x<.15*app.width and .76*app.height<y<.80*app.height:
        try: saveFile(app)
        except: return
    if .05*app.width<x<.15*app.width and .83*app.height<y<.87*app.height:
        try: openFile(app)
        except: return

def visualizationButtonPressed(app,x,y):
    r = 11
    if (.39*app.width-x)**2 +(.89*app.height-y)**2 < r**2:
        app.midPointsOn = True
    elif (.39*app.width-x)**2 +(.92*app.height-y)**2 < r**2:
        app.midPointsOn = False
    elif (.56*app.width-x)**2 +(.89*app.height-y)**2 < r**2:
        app.endsBendsOn = True
    elif (.56*app.width-x)**2 +(.92*app.height-y)**2 < r**2:
        app.endsBendsOn = False
    elif (.72*app.width-x)**2 +(.89*app.height-y)**2 < r**2:
        app.traceOn = True
    elif (.72*app.width-x)**2 +(.92*app.height-y)**2 < r**2:
        app.traceOn = False
    elif (.89*app.width-x)**2 +(.89*app.height-y)**2 < r**2:
        app.contPath = "all"
    elif (.89*app.width-x)**2 +(.92*app.height-y)**2 < r**2:
        app.contPath = "one"
    elif (.89*app.width-x)**2 +(.95*app.height-y)**2 < r**2:
        app.contPath = "off"
    elif (.21*app.width-x)**2 +(.89*app.height-y)**2 < r**2:
        app.imageDisplay = "outline"
    elif (.21*app.width-x)**2 +(.92*app.height-y)**2 < r**2:
        app.imageDisplay = "original"    

def mouseDragged(app, event):
    if app.markerActive:
        x,y = getGridCoords(app,event.x-5,event.y-5)
        index = getIndex(x,y)
        app.pixels[index]= 250 # sets pixel to an arbitrary "light" value
        x,y = getGridCoords(app,event.x+5,event.y+5)
        index = getIndex(x,y)
        app.pixels[index]= 250 
    if app.eraserActive:
        x,y = getGridCoords(app,event.x-5,event.y-5)
        index = getIndex(x,y)
        app.pixels[index]= 2 # sets pixel to an arbitrary "dark" value
        x,y = getGridCoords(app,event.x+5,event.y+5)
        index = getIndex(x,y)
        app.pixels[index]= 2

def getGridCoords(app,x,y): #view to model
    if not pointInGrid(app,x,y):
        return (-1,-1)
    x = int((x-app.margin)/app.pixW)
    y = int((y-app.margin)/app.pixH)
    return x, y
    
def getCellUpperLeft(app,y, x):#model to view
    x1 = app.margin + x*app.pixW
    y1 = app.margin + y*app.pixH
    return(x1,y1)

def drawSelection(app, canvas):
    (x1,y1) = getCellUpperLeft(app,app.selY, app.selX)
    canvas.create_rectangle(x1,y1,x1+app.pixW,y1+app.pixH, width= 3, fill = None)       

def getMidPoints(app): #finds the midpoints, taking horizontal slices
    #pixels = list(app.img.getdata()) # returns one long flattened list: row1, row2, etc
    (width, height) = app.img.size #28,28 #TODO: we may be in drawing mode
    leadEdge = 0
    vertThreshold = 5 # length of vertical segment to break up with multi points
    midsList = list() # a list of the coordinate tuples of the midpoints
    outlineList = list() # list of leading and trailing edges, should form an outline
    for x in range(width):
        for y in range(height):
            if app.pixels[getIndex(x,y)] > app.threshold and leadEdge == 0: 
                leadEdge = y # leading edge found
            if app.pixels[getIndex(x,y)] <= app.threshold and leadEdge != 0: #trailing edge found
                #TODO remove single pixel "turds"
                trailEdge = y-1 #TODO: Check, but I think because <= app.threshold
                if abs(leadEdge-trailEdge) > vertThreshold:
                    midpoint = leadEdge + 1
                    midsList.append((x,midpoint))
                    midpoint = trailEdge -1
                    midsList.append((x,midpoint))
                else:
                    midpoint = round((leadEdge + trailEdge)/2)
                    midsList.append((x,midpoint))# 
                for y in range (leadEdge,y):
                    outlineList.append((x,y))# because <=THRESHOLD trigger
                #print("x,y,m: ",x,y,midpoint, end = "__")
                leadEdge = 0      
    return midsList,outlineList

#gets index out of a flattened list given x and y coords of the image
#list stores pixels by picHeight, starting with top
def getIndex(x,y, width=28):
    index = (y)*width + (x)
    return index

def getCoord(index, width= 28):
    y = index // width
    x = index % width
    return x,y 

def getStartPoint(app): #returns starting point to trace
    minDist = 10**10
    if app.ends != []:
        for (x,y) in app.ends:
            #print("tempAppEnds: ", app.ends)
            dist = math.sqrt(y**2 + x**2)
            if dist < minDist:
                minDist = dist
                (startX, startY) = (x,y)
        app.ends.remove((startX,startY))
        return (startX, startY)
    #if no end, start with the bend closest to 0,0
    elif app.bends != []:
        for (x, y) in app.bends:
            dist = math.sqrt(y**2 + x**2)
            if dist < minDist:
                minDist = dist
                (startX, startY) = (x,y)
        app.bends.remove((startX,startY))#TODO mistake- this removes each end in order (or should anyway)
        return (startX, startY)
    else: return (None, None)

#This function produces the trace list that attempts to trace the character
def getTrace(app):
    app.trace = []
    outOfOrder = False
    (startX, startY) = getStartPoint(app)#start with the end closest to 0,0
    if (startX,startY) == (None,None):return
    app.trace.append((startX, startY))
    #connect to farthest contiguous point
    midsList, outlineList = getMidPoints(app)
    if len(midsList) < 2: return
    while len(midsList) > 1:
        traceIndex = app.trace.index((startX,startY))
        maxDistance = 0
        for index in range(len(midsList)):
            if areContiguous(app,(startX, startY),midsList[index]):
                (x,y) = midsList[index] 
                if traceIndex == 0 or app.trace[traceIndex-1] == 'gap':
                    dist = math.sqrt((startX - x)**2 +(startY - y)**2)
                else:
                    (priorX,priorY)= app.trace[traceIndex - 1]
                    dist = math.sqrt((priorX - x)**2 +(priorY - y)**2)
                if dist > maxDistance:
                    maxDistance = dist
                    (endX, endY) = (x,y)
        if maxDistance >= 1: 
            app.trace.append((endX,endY))
            if (startX,startY) != (endX,endY): # it found a new connection point
                (startX,startY) = (endX,endY)
        else: #failing that, make sure all ends/bends are connected
            (startX,startY)= getStartPoint(app)
            if (startX,startY) == (None,None): break #if ends/bends gone,we're done
            #TODO: sometimes leaves ends unconnected, see notes on 4/336.png
            else:
                #trace should have start point in upper left
                if distance(app.trace[0],(0,0)) > distance((endX,endY),(0,0)):
                    app.trace.reverse() 
                app.trace.append("gap")
                if distance(app.trace[0],(0,0)) > distance((startX,startY),(0,0)):
                    outOfOrder = True
                app.trace.append((startX, startY))
        midsList = removeIntermediatePoints(app,midsList)
    if len(app.trace) > 1:
        closeTheLoop(app)
        reorderIfNeeded(app, outOfOrder)

def removeIntermediatePoints(app,midsList):
    #maxDist is dist between this x and the "prior" X.  Whereas lastDist
    #is the distance between the most recent two trace points
    if len(app.trace) <2: return
    if app.trace[-2] == "gap" or app.trace[-1] == "gap": return midsList
    startX,startY = app.trace[-2]
    endX,endY = app.trace[-1]
    distToPrior = distance(app.trace[-1],app.trace[-2])
    index = 0
    if (startX,startY) in midsList: midsList.remove((startX,startY))
    if (endX,endY) in midsList: midsList.remove((endX,endY))
    while index < (len(midsList)): #removes intermediate points from ML
        (x,y) = midsList[index]
        if areContiguous(app,(app.trace[-1]),(x,y)) and \
            areContiguous(app, (app.trace[-2]), (x,y)):
            dist = distance(app.trace[-2],(x,y))
            if dist <= distToPrior:
                midsList.pop(index)
                if (x,y) in app.ends: app.ends.remove((x,y))
                if (x,y) in app.bends: app.bends.remove((x,y))
            else: index += 1
        elif min(startX,endX) <= x <= max(startX,endX) and \
        min(startY,endY) <= y <= max(startY,endY) and isConnected(app,(endX,endY),(x,y)):
                midsList.pop(index)    
        else: index += 1
    return midsList

#closing the loop on closed chars
#TODO: need a test to determine if char otherwise closed, see 3/7.png
def closeTheLoop(app):
    if "gap" not in app.trace and len(app.trace) >1:
        startX, startY = app.trace[0]
        endX, endY = app.trace[-1]
        threshold = 1.6
        if areContiguous(app,app.trace[0],app.trace[-1]):
            app.trace.append(app.trace[0]) 
            #TODO: maybe this is ok, but see training/0/283 it doesn't find the connecting end "soon enough"
        else: # if start and end aren't contiguous, is there a point connecting them?
            midsList, outlineList = getMidPoints(app)
            minDist = 1000
            for i in range(len(midsList)):
                if(areContiguous(app,app.trace[0],midsList[i])) and areContiguous(app,app.trace[-1],midsList[i]):
                    dist = distance((startX,startY),(midsList[i])) + distance((endX,endY),(midsList[i]))
                    if dist < minDist:
                        minDist = dist
                        (xConnection,yConnection) = midsList[i]
            if minDist < distance((startX,startY),(endX,endY))*threshold:
                app.trace.append((xConnection,yConnection))
                app.trace.append(app.trace[0])

#if start point improperly placed, reverse list
def reorderIfNeeded(app, outOfOrder):
    if not outOfOrder:
        if distance(app.trace[-1],(0,0)) < distance(app.trace[0],(0,0)):
            app.trace.reverse()
    '''
    else: #since oOO, have to find upper left point
        minDist = distance(app.trace[0],(0,0))
        for i in range(1,len(app.trace)):
            if app.trace[i] == "gap":
                dist = distance(app.trace[i+1],(0,0))
                if dist < minDist:
                    minDist = dist
                    minI = i+1
        app.trace = app.trace[minI:] + app.trace[:minI]
    '''

def distance(coord1,coord2):
    #try: 
    (x1,y1) = coord1
    #except: print(coord1)
    (x2,y2) = coord2 
    return math.sqrt((x2-x1)**2+(y2-y1)**2)

#takes original "image" list and two midpoints and returns if they are contiguous
# ie if they are candidates to be connected directly by the trace.
def areContiguous(app,mid1,mid2):  
    (x1,y1) = (mid1[0], mid1[1])
    (x2,y2) = (mid2[0], mid2[1])
    if x1 == None or y1 == None or x2 == None or y2 == None: return False
    largestX = max(x1,x2)
    smallestX = min(x1,x2)
    #below checks for mids connected by "L" sections that should not be bridged 
    if abs(x1-x2)>1 and abs(y1-y2) > 1: 
        m = (y2-y1)/(x2-x1) # m is the slope
        b = y1+.5-m*(x1+.5) # b is the y intercept
        yMin, yMax = min(y1,y2),max(y1,y2)
        for y in range(yMin,yMax+1):
            xStart = (y-b)/m
            xEnd = (y+1-b)/m
            xMin = max(smallestX,int(min(xStart,xEnd)))
            xMax = min(largestX,roundHalfUp(max(xStart,xEnd)))
            xMid = (xMin + xMax)//2
            if app.pixels[getIndex(xMid,y)] < app.threshold:
                return False
    if not isConnected(app, mid1,mid2):
        return False 
    return True

def isConnected(app,mid1,mid2): #makes sure no gap between midpoints
    (x1,y1) = (mid1[0], mid1[1])
    (x2,y2) = (mid2[0], mid2[1])
    if abs(x1-x2)==1 and abs(y1-y2)==1: #by definition so to speak
        return True
    elif x1 == x2:
        for y in range(min(y1,y2),max(y1,y2)+1):
            if app.pixels[getIndex(x1,y)] < app.threshold: #gap found
                return False
        return True
    elif y1 == y2:
        for x in range(min(x1,x2),max(x1,x2)+1):
            if app.pixels[getIndex(x, y1)] < app.threshold: #gap found
                return False
        return True
    else:
        if x2 > x1: dx = 1
        elif x1 > x2: dx = -1
        else: dx = 0
        if y2 > y1: dy = 1
        elif y1 > y2: dy = -1
        else: dy = 0
        if getIndex(x2-dx,y2) > 783: print(getIndex(x2-dx,y2),x2,dx,y2)
        if app.pixels[getIndex(x2,y2-dy)] > app.threshold and isConnected(app,(x1,y1),(x2,y2-dy)):
            return True
        elif app.pixels[getIndex(x2-dx,y2)] > app.threshold and isConnected(app,(x1,y1),(x2-dx,y2)):
            return True
        else:
            return False

#this function produces pairs of contigous midpoints, ultimately used
# in getTrace
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
(contMidStart, contMidEnd) = contiguousPairs(midsList, app.img)
for i in range(len(contMidStart)):
    print(contMidStart[i], contMidEnd[i])
'''

#Apply two part test to all midpoints: 1 end has all 
#connected points in "one direction", ie up down, left, right etc &
#2. those connected points must be connected to one another
def findEnds(app):
    midsList, outlineList = getMidPoints(app)
    (contMidStart, contMidEnd) = contiguousPairs(app,midsList)
    app.ends = []
    app.bends = []
    i = 1 
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
        
def drawButtons(app, canvas):
    bW = 40 #button half width
    bH = 25 #button half height
    dCX,dCY = app.width//2 + 115, app.height*.705 # drawing tools console center
    canvas.create_text(dCX,dCY, text = "Drawing Tools")
    #clear drawing button
    canvas.create_rectangle(dCX -2*bW, dCY +bH, dCX -bW, dCY+ 3*bH)
    canvas.create_text(dCX-3*bW//2,dCY +2*bH, text = "Clear")
    #eraser button
    eraserColor = "white"
    if app.eraserActive: eraserColor = "light gray"
    canvas.create_rectangle(dCX -bW//2, dCY +bH, dCX +bW//2, dCY+ 3*bH, fill = eraserColor)
    canvas.create_rectangle(dCX-10, dCY+bH+20, dCX+10, dCY+bH+42, fill = "black" )
    canvas.create_rectangle(dCX-10, dCY+bH+8, dCX+10, dCY+bH+18, fill = "pink" )
    #marker button
    markerColor= "white"
    if app.markerActive: markerColor = "light gray"
    canvas.create_rectangle(dCX +bW, dCY +bH, dCX +2*bW, dCY+ 3*bH, fill = markerColor )
    canvas.create_rectangle(dCX+bW+10 , dCY+bH+20, dCX+2*bW-10, dCY+bH+42, fill = "black" )
    canvas.create_polygon(dCX+bW+10 , dCY+bH+18, dCX+2*bW-10,dCY+bH+18,dCX+3*bW//2,dCY+bH+6,fill = "gray", width = 1 )
    #file related buttons
    canvas.create_rectangle(app.width*.1-bW, app.height*.78-bH, app.width*.1+bW, app.height*.78+bH )
    canvas.create_text(app.width*.1,app.height*.78, text = "save file")
    canvas.create_rectangle(app.width*.1-bW, app.height*.85-bH, app.width*.1+bW, app.height*.85+bH)
    canvas.create_text(app.width*.1,app.height*.85, text = "open file")

def drawDisplayControls(app,canvas):
    bH = 30 #button half height
    cW = app.width*.25 #nominal console column width
    rH = app.height*.03 #nominal console y height
    tCX = app.width*.65 # cen location of viz tools title text
    tCY = app.height*.83 # cen location of viz tools title text
    r = 11 #radio button radius
    r2 = 6 #inner radio button radius
    canvas.create_text(tCX,tCY, text = "Visualization Tools")
    canvas.create_text(tCX-cW,tCY+rH, text = "Midpoints")
    canvas.create_oval(tCX-cW-10-r,tCY+rH+bH-r,tCX-cW-10+r,tCY+rH+bH+r)
    if app.midPointsOn: 
        canvas.create_oval(tCX-cW-10-r2,tCY+rH+bH-r2,tCX-cW-10+r2,tCY+rH+bH+r2, fill= "black")
    canvas.create_text(tCX-cW+30,tCY+rH+bH, text = "On")
    canvas.create_oval(tCX-cW-10-r,tCY+rH+2*bH-r,tCX-cW-10+r,tCY+rH+2*bH+r)
    if not app.midPointsOn:
        canvas.create_oval(tCX-cW-10-r2,tCY+rH+2*bH-r2,tCX-cW-10+r2,tCY+rH+2*bH+r2,fill="black")
    canvas.create_text(tCX-cW+30,tCY+rH+2*bH, text = "Off")
    canvas.create_text(tCX-cW//3,tCY+rH, text = "Ends/Bends")
    canvas.create_oval(tCX-cW//3-10-r,tCY+rH+bH-r,tCX-cW//3-10+r,tCY+rH+bH+r)
    if app.endsBendsOn:
        canvas.create_oval(tCX-cW//3-10-r2,tCY+rH+bH-r2,tCX-cW//3-10+r2,tCY+rH+bH+r2,fill="black" )
    canvas.create_text(tCX-cW//3+30,tCY+rH+bH, text = "On")
    canvas.create_oval(tCX-cW//3-10-r,tCY+rH+2*bH-r,tCX-cW//3-10+r,tCY+rH+2*bH+r)
    if not app.endsBendsOn:
        canvas.create_oval(tCX-cW//3-10-r2,tCY+rH+2*bH-r2,tCX-cW//3-10+r2,tCY+rH+2*bH+r2,fill ="black")
    canvas.create_text(tCX-cW//3+30,tCY+rH+2*bH, text = "Off")

def drawDisplayControls2(app, canvas):
    bH = 30 #button half height
    cW = app.width*.25 #nominal console column width
    rH = app.height*.03 #nominal console y height
    tCX = app.width*.65 # cen location of viz tools title text
    tCY = app.height*.83 # cen location of viz tools title text
    r = 11 #radio button radius
    r2 = 6 #inner radio button radius
    canvas.create_text(tCX+cW//3,tCY+rH, text = "Trace")
    canvas.create_oval(tCX+cW//3-10-r,tCY+rH+bH-r,tCX+cW//3-10+r,tCY+rH+bH+r)
    if app.traceOn:
        canvas.create_oval(tCX+cW//3-10-r2,tCY+rH+bH-r2,tCX+cW//3-10+r2,tCY+rH+bH+r2,fill ="black")
    canvas.create_text(tCX+cW//3+30,tCY+rH+bH, text = "On")
    canvas.create_oval(tCX+cW//3-10-r,tCY+rH+2*bH-r,tCX+cW//3-10+r,tCY+rH+2*bH+r)
    if not app.traceOn:
        canvas.create_oval(tCX+cW//3-10-r2,tCY+rH+2*bH-r2,tCX+cW//3-10+r2,tCY+rH+2*bH+r2,fill ="black")
    canvas.create_text(tCX+cW//3+30,tCY+rH+2*bH, text = "Off")
    canvas.create_text(tCX+cW,tCY+rH, text = "Contiguous Paths")
    canvas.create_oval(tCX+cW-10-r,tCY+rH+bH-r,tCX+cW-10+r,tCY+rH+bH+r)
    if app.contPath == "all":
        canvas.create_oval(tCX+cW-10-r2,tCY+rH+bH-r2,tCX+cW-10+r2,tCY+rH+bH+r2,fill ="black")
    canvas.create_text(tCX+cW+30,tCY+rH+bH, text = "All")
    canvas.create_oval(tCX+cW-10-r,tCY+rH+2*bH-r,tCX+cW-10+r,tCY+rH+2*bH+r)
    if app.contPath == "one":
        canvas.create_oval(tCX+cW-10-r2,tCY+rH+2*bH-r2,tCX+cW-10+r2,tCY+rH+2*bH+r2,fill="black")
    canvas.create_text(tCX+cW+30,tCY+rH+2*bH, text = "One")
    canvas.create_oval(tCX+cW-10-r,tCY+rH+3*bH-r,tCX+cW-10+r,tCY+rH+3*bH+r)
    if app.contPath == "off":
        canvas.create_oval(tCX+cW-10-r2,tCY+rH+3*bH-r2,tCX+cW-10+r2,tCY+rH+3*bH+r2, fill="black")
    canvas.create_text(tCX+cW+30,tCY+rH+3*bH, text = "Off")

def drawDisplayControls3(app, canvas):
    bH = 30 #button half height
    cW = app.width*.25 #nominal console column width
    rH = app.height*.03 #nominal console y height
    tCX = app.width*.65 # cen location of viz tools title text
    tCY = app.height*.83 # cen location of viz tools title text
    r = 11 #radio button radius
    r2 = 6 #inner radio button radius
    canvas.create_text(tCX-1.7*cW,tCY+rH, text = "Image")
    canvas.create_oval(tCX-1.7*cW-10-r,tCY+rH+bH-r,tCX-1.7*cW-10+r,tCY+rH+bH+r)
    if app.imageDisplay == "outline": 
        canvas.create_oval(tCX-1.7*cW-10-r2,tCY+rH+bH-r2,tCX-1.7*cW-10+r2,tCY+rH+bH+r2, fill= "black")
    canvas.create_text(tCX-1.7*cW+30,tCY+rH+bH, text = "Outline")
    canvas.create_oval(tCX-1.7*cW-10-r,tCY+rH+2*bH-r,tCX-1.7*cW-10+r,tCY+rH+2*bH+r)
    if app.imageDisplay == "original":
        canvas.create_oval(tCX-1.7*cW-10-r2,tCY+rH+2*bH-r2,tCX-1.7*cW-10+r2,tCY+rH+2*bH+r2,fill="black")
    canvas.create_text(tCX-1.7*cW+30,tCY+rH+2*bH, text = "Original")

def drawNetworkControls(app, canvas):
    r = 11 #radio button radius
    r2 = 6 #inner radio button radius
    canvas.create_text(15,8, text = "Network Type:", anchor = "w")
    canvas.create_oval(30-r,32-r,30+r,32+r)
    if app.network == "Regular": 
        canvas.create_oval(30-r2,32-r2,30+r2,32+r2, fill= "black")
    canvas.create_text(50,32, text = "Standard NN", anchor = "w")
    canvas.create_oval(30-r,60-r,30+r,60+r)
    if app.network == "VNN":
        canvas.create_oval(30-r2,60-r2,30+r2,60+r2, fill="black")
    canvas.create_text(50,60, text = "Vector NN", anchor = "w")

def drawMidPoints(app, canvas):
    #from: https://www.cs.cmu.edu/~112/notes/notes-graphics.html#customColors
    pistachio = rgbString(147, 197, 114)
    if app.midPointsOn:
        midsList, outlineList = getMidPoints(app)
        for coords in midsList:
            ((x,y))=coords
            x=app.margin+app.pixW//4+x*app.pixW
            y=app.margin+app.pixH//4+y*app.pixH
            canvas.create_rectangle(x,y,x+app.pixW//2,y+app.pixH//2, fill=pistachio)

def drawGrid(app, canvas):
    rEdge = app.width - app.margin + 1
    bEdge = app.height - app.botMargin + 1
    for x in range(app.margin,rEdge, app.pixW):
        canvas.create_line(x,app.margin,x,bEdge)
    for y in range(app.margin,bEdge, app.pixH):
        canvas.create_line(app.margin,y,rEdge,y)
    for x in range(app.margin,rEdge, app.pixW*5):
        canvas.create_line(x,app.margin,x,bEdge, width = 2)
    for y in range(app.margin,rEdge, app.pixH*5):
        canvas.create_line(app.margin,y,bEdge,y, width = 2)
    canvas.create_text(100,700, text =f'Selected Coord(x,y): {app.selX}, {app.selY}')

def drawImage(app, canvas):
    canvas.create_text(30,app.height*.975, text=f'Threshold: {app.threshold}    {app.file}', font='Times 11', anchor = 'w')
    if app.imageDisplay == "outline":
        midsList, outlineList = getMidPoints(app)
        for coords in outlineList:
            ((x,y))=coords
            x=app.margin+x*app.pixW
            y=app.margin+y*app.pixH
            color = rgbString(app.threshold,app.threshold,min(app.threshold+10,255))
            canvas.create_rectangle(x,y,x+app.pixW,y+app.pixH, fill=color)
    else: #app.imageDisplay is "original"
        for index in range(len(app.pixels)):
            x,y = getCoord(index)
            pixelLum = 255- app.pixels[index] #Reverses the gray image from original negative 
            color = rgbString(pixelLum,pixelLum,min(pixelLum+10,255))
            x=app.margin+x*app.pixW
            y=app.margin+y*app.pixH
            canvas.create_rectangle(x,y,x+app.pixW,y+app.pixH, fill=color)
        drawGrid(app,canvas)

#https://www.cs.cmu.edu/~112/notes/notes-graphics.html#customColors
def rgbString(r, g, b):
    # Don't worry about the :02x part, but for the curious,
    # it says to use hex (base 16) with two digits.
    return f'#{r:02x}{g:02x}{b:02x}'

def drawContiguousConnections(app, canvas):
    if app.contPath != "off":
        midsList, outlineList = getMidPoints(app)
        if True: #app.contigLinesVisible == True: #TODO: something wrong here 
            (contMidStart, contMidEnd) = contiguousPairs(app,midsList)
            for i in range(len(contMidStart)):
                (x1,y1) = contMidStart[i]
                (x1,y1) = app.offset + x1*20, app.offset + y1*20 
                (x2,y2) = contMidEnd[i]
                (x2,y2) = app.offset + x2*20, app.offset + y2*20
                (xs,ys) = getCellUpperLeft(app,app.selY, app.selX)
                (xs,ys) = (xs+10,ys+10)
                if app.contPath == "all": 
                    canvas.create_line(x1,y1,x2,y2, fill = "red", width =2)
                elif (x1 == xs) and (y1 == ys): #contPath = "one" 
                    canvas.create_line(x1,y1,x2,y2, fill = "red", width =2)
                
def drawEnds(app, canvas):
    if app.endsBendsOn:
        for (x,y) in app.ends: 
            x = app.offset + x*app.pixW
            y = app.offset + y*app.pixH
            r = 15
            canvas.create_oval(x-r,y-r,x+r,y+r, width = 4, outline = "green", fill = None)

def drawBends(app, canvas): 
    if app.endsBendsOn:
        for (x,y) in app.bends:
            x = app.offset + x*app.pixW
            y = app.offset + y*app.pixH
            r = 15
            canvas.create_oval(x-r,y-r,x+r,y+r, width = 4, outline = "blue", fill = None)

def drawTrace(app, canvas):
    if app.traceOn  and app.trace != []:
        (startX,startY) = app.trace[0]
        if startX == None or startY == None: return #new drawing, no trace yet
        startX,startY =app.offset + startX*app.pixW, app.offset + startY*app.pixH
        canvas.create_oval(startX-5,startY-5,startX+5,startY+5, fill="red")
        for i in range(1,len(app.trace)):
            if app.trace[i-1] != "gap" and app.trace[i] !="gap":
                (x1,y1) = app.trace[i-1]
                (x1,y1) = app.offset + x1*app.pixW, app.offset + y1*app.pixH 
                (x2,y2) = app.trace[i]
                (x2,y2) = app.offset + x2*app.pixW, app.offset + y2*app.pixH
                canvas.create_line(x1,y1,x2,y2, fill ="orange", width = 3)

def drawPrediction(app, canvas):
    canvas.create_rectangle(app.width*.18,app.height*.071,app.width*.27,app.height*.028)
    canvas.create_text(app.width*.225,app.height*.05, text= "Predict")
    canvas.create_text(app.width*.35, app.height*.01,text= "Prediction:", anchor = "w")
    if app.predictionMade:
        canvas.create_text(app.width*.4,app.height*.05, text=f"{app.predNum} ({app.confidence} % conf.)", font ="times 18 bold")
        canvas.create_rectangle(app.width*.55,app.height*.071,app.width*.81,app.height*.028)
        for i in range(len(app.prediction)):
            canvas.create_rectangle(app.width*.56 +i*20,app.height*.07,app.width*.56 +i*20+10, app.height*.07-app.prediction[i]*40, fill="red")
            canvas.create_text(app.width*.56+i*20 +5, app.height*.08,text= f"{i}")

def timerFired(app):
    variables(app)
    ML, OL = getMidPoints(app)
    if len(ML) > 1: # don't start drawing until there's something to draw
        findEnds(app) #TODO hard to imagine this should be here
        getTrace(app) #TODO put these in the right places
        #findEnds(app)

def drawCharacter(app, canvas):
    drawImage(app, canvas)
    drawMidPoints(app, canvas)
    drawEnds(app, canvas)
    drawBends(app, canvas)
    drawSelection(app, canvas)
    drawTrace(app, canvas)
    drawContiguousConnections(app, canvas)

def redrawAll(app, canvas):
    drawGrid(app,canvas)
    drawButtons(app,canvas)
    drawDisplayControls(app,canvas)
    drawDisplayControls2(app,canvas)
    drawDisplayControls3(app,canvas)
    drawCharacter(app,canvas)
    drawPrediction(app,canvas)
    drawNetworkControls(app,canvas)
    
def main():
    #cs112_s21_week4_linter.lint()
    runApp(width=762, height=962)
    
if __name__ == '__main__':
    main()




















