'''copyright 2021 Joe Born
all rights reserved '''
#import cs112_s21_week4_linter
from cmu_112_graphics import *
from vnn_TF import *
import random, string, math, time
import PIL, copy
from PIL import Image 
import decimal

#TODO: grid screws up when canvas stretched
#file = 'C:/GitHub/VectNN/JB_4.bmp'

def appStarted(app):
    app.rows = 28 # a row and col for each pixel 
    app.cols = 28 # a row and col for each pixel 
    app.selCol = 0
    app.selRow = 0
    app.margin = 100
    app.botMargin = 300
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
    variables(app)
    findEnds(app) #TODO 
    getMidPoints(app)
    getTrace(app)
    trainNN(app)

def makePrediction(app):    
    writeSample(app)
    prediction = predictSample(app).tolist()
    app.prediction = prediction
    app.predNum = prediction.index(max(prediction))
    app.confidence = int(max(prediction)*100)
    app.predictionMade = True

def variables(app):
    app.pixW = (app.width - 2*app.margin)//app.cols
    app.pixH = (app.height - app.margin -app.botMargin)//app.rows
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
def pointInGrid(app,x,y):
    return ((app.margin <= x <= app.width - app.margin) and \
        (app.margin <= y <=app.height -app.botMargin))

def sizeChanged(app):
    variables(app)

def mousePressed(app, event):
    if pointInGrid(app,event.x,event.y):
        app.selCol, app.selRow = getGridCoords(app,event.x,event.y)
        if app.markerActive:
            index = getIndex(app.selCol,app.selRow)
            app.pixels[index]= 250 # sets pixel to an arbitrary "light" value
        if app.eraserActive:
            index = getIndex(app.selCol,app.selRow)
            app.pixels[index]= 2 # sets pixel to an arbitrary "light" value
    elif .18*app.width<event.x<.27*app.width and .028*app.height<event.y<.071*app.height:
        makePrediction(app)
    elif .55*app.width<event.x<.76*app.width and .73*app.height<event.y<.78*app.height:
        drawingButtonPressed(app, event.x,event.y)
    elif .15*app.width<event.x<.25*app.width and .75*app.height<event.y<.88*app.height:
        fileButtonPressed(app,event.x,event.y)
    elif .37*app.width<event.x<.9*app.width and .88*app.height<event.y<.96*app.height:
        visualizationButtonPressed(app,event.x,event.y)


def drawingButtonPressed(app,x,y):
    if .55*app.width<x<.60*app.width and .73*app.height<y<.78*app.height:
        appStarted(app)
    if .63*app.width<x<.67*app.width and .73*app.height<y<.78*app.height:
        app.eraserActive = not app.eraserActive
        app.markerActive = False
    if .71*app.width<x<.75*app.width and .73*app.height<y<.78*app.height:
        app.markerActive = not app.markerActive
        app.eraserActive = False

def fileButtonPressed(app,x,y):
    if .15*app.width<x<.25*app.width and .76*app.height<y<.80*app.height:
        saveFile(app)
    if .15*app.width<x<.25*app.width and .83*app.height<y<.87*app.height:
        openFile(app)

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

def mouseDragged(app, event):
    if app.markerActive:
        x,y = getGridCoords(app,event.x,event.y)
        index = getIndex(x,y)
        app.pixels[index]= 250 # sets pixel to an arbitrary "light" value
    if app.eraserActive:
        x,y = getGridCoords(app,event.x,event.y)
        index = getIndex(x,y)
        app.pixels[index]= 2 # sets pixel to an arbitrary "dark" value

def getGridCoords(app,x,y): #view to model
    if not pointInGrid(app,x,y):
        return (-1,-1)
    col = int((x-app.margin)/app.pixW)
    row = int((y-app.margin)/app.pixH)
    return col, row
    
def getCellUpperLeft(app,row, col):#model to view
    x1 = app.margin + col*app.pixW
    y1 = app.margin + row*app.pixH
    return(x1,y1)

def drawSelection(app, canvas):
    (x1,y1) = getCellUpperLeft(app,app.selRow, app.selCol)
    canvas.create_rectangle(x1,y1,x1+app.pixW,y1+app.pixH, width= 3, fill = None)

def keyPressed(app, event):
    if event.key.lower() == 'space':
        app.contigLinesVisible = not app.contigLinesVisible
    if event.key.lower() == 'o':
        app.oneContigVis = not app.oneContigVis        

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
#list stores pixels by rows, starting with top
def getIndex(x,y, width=28):
    i = (y)*width + (x)#TODO y-1, x-1 fixed an out of index error in the parser, but seriously screws things up
    return i

def getStartPoint(app): #returns starting point to trace
    minDist = 10**10
    if app.ends != []:
        for (col,row) in app.ends:
            #print("tempAppEnds: ", app.ends)
            dist = math.sqrt(row**2 + col**2)
            if dist < minDist:
                minDist = dist
                (startX, startY) = (col,row)
        app.ends.remove((startX,startY))
        return (startX, startY)
    #if no end, start with the bend closest to 0,0
    elif app.bends != []:
        for (col, row) in app.bends:
            dist = math.sqrt(row**2 + col**2)
            if dist < minDist:
                minDist = dist
                (startX, startY) = (col,row)
        app.bends.remove((startX,startY))#TODO mistake- this removes each end in order (or should anyway)
        return (startX, startY)
    else: return (None, None)

def getTrace(app):
    app.trace = []
    #start with the end closest to 0,0
    (startX, startY) = getStartPoint(app)
    app.trace.append((startX, startY))
    #connect to farthest contiguous point
    midsList, outlineList = getMidPoints(app)# TODO eliminate all the calls to gMP, put midslist etc in app...
    while len(midsList) > 1:
        traceIndex = app.trace.index((startX,startY))
        #print ("ML prior: ", midsList)
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
                    #print("endX,endY", x,y)
        if maxDistance >= 1: app.trace.append((endX,endY))
        if (startX,startY) in midsList: midsList.remove((startX,startY))
        index = 0
        #maxDist is dist between this x and the "prior" X.  Whereas lastDist
        #is the distance between the most recent two trace points
        lastDist = math.sqrt((startX-endX)**2+(startY-endY)**2)
        while index < (len(midsList)): #removes intermediate points from ML
            (x,y) = midsList[index]
            if areContiguous(app,(startX, startY),(x,y)) and \
                areContiguous(app, (endX,endY), (x,y)):
                dist = math.sqrt((startX - x)**2 +(startY - y)**2)
                if dist <= lastDist:
                    midsList.pop(index)
                    if (x,y) in app.ends: app.ends.remove((x,y))
                    if (x,y) in app.bends: app.bends.remove((x,y))
                else: index += 1
            elif min(startX,endX) <= x <= max(startX,endX) and \
            min(startY,endY) <= y <= max(startY,endY) and isConnected(app,(endX,endY),(x,y)):
                    if (x,y) == (11,11): print("x,y,endX,endY: ", x,y,endX,endY)
                    midsList.pop(index)    
            else: index += 1
        if (startX,startY) != (endX,endY): # it found a new connection point
            (startX,startY) = (endX,endY)
        else: #failing that, make sure all ends/bends are connected
            (startX,startY)= getStartPoint(app)
            if (startX,startY) == (None,None): break #if ends/bends gone,we're done
            #TODO: sometimes leaves ends unconnected, see notes on 4/336.png
            else:
                app.trace.append("gap") 
                app.trace.append((startX, startY))
        if (endX,endY) in midsList: midsList.remove((endX,endY))
        #print("app.trace", app.trace)
        #print("ML after: ",midsList)
        #input("press any key")
    closeTheLoop(app)

#closing the loop on closed chars
#TODO: need a test to determine if char otherwise closed, see 3/7.png
def closeTheLoop(app):
    if "gap" not in app.trace:
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

def distance(coord1,coord2):
    (x1,y1) = coord1
    (x2,y2) = coord2 
    return math.sqrt((x2-x1)**2+(y2-y1)**2)


    # delete all midpoints "passed"
    #"passed" means closer to the from mid point and contiguous to both
    #from chosen point choose farthest contiguous point (ignoring all skipped points)
    #done when no midpoints are left (either because they were chosen or skipped)


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
    canvas.create_rectangle(app.width//5-bW, app.height*.78-bH, app.width//5+bW, app.height*.78+bH )
    canvas.create_text(app.width//5,app.height*.78, text = "save file")
    canvas.create_rectangle(app.width//5-bW, app.height*.85-bH, app.width//5+bW, app.height*.85+bH)
    canvas.create_text(app.width//5,app.height*.85, text = "open file")

def drawDisplayControls(app,canvas):
    bH = 30 #button half height
    cW = app.width//4 #nominal console column width
    rH = app.height*.03 #nominal console row height
    tCX = app.width//2 + 115 # cen location of viz tools title text
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
    cW = app.width//4 #nominal console column width
    rH = app.height*.03 #nominal console row height
    tCX = app.width//2 + 115 # cen location of viz tools title text
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

def drawMidPoints(app, canvas):
    if app.midPointsOn:
        midsList, outlineList = getMidPoints(app)
        for coords in midsList:
            ((x,y))=coords
            x=app.margin+app.pixW//4+x*app.pixW
            y=app.margin+app.pixH//4+y*app.pixH
            canvas.create_rectangle(x,y,x+app.pixW//2,y+app.pixH//2, fill="gray")

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
    canvas.create_text(100,700, text =f'sel Coord(row,col) : {app.selRow} , {app.selCol}')

def drawOutline(app, canvas):
    canvas.create_text(30,app.height*.975, text=f'Threshold: {app.threshold}    {app.file}', font='Times 11', anchor = 'w')
    midsList, outlineList = getMidPoints(app)
    for coords in outlineList:
        ((x,y))=coords
        x=app.margin+x*app.pixW
        y=app.margin+y*app.pixH
        canvas.create_rectangle(x,y,x+app.pixW,y+app.pixH, fill ="lightgray")

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
                (xs,ys) = getCellUpperLeft(app,app.selRow, app.selCol)
                (xs,ys) = (xs+10,ys+10)
                if app.contPath == "all": 
                    canvas.create_line(x1,y1,x2,y2, fill = "red", width =2)
                elif (x1 == xs) and (y1 == ys): #contPath = "one" 
                    canvas.create_line(x1,y1,x2,y2, fill = "red", width =2)
                
def drawEnds(app, canvas):
    if app.endsBendsOn:
        for (col,row) in app.ends: # TODO fix this to match row, col convention
            x = app.offset + col*app.pixW
            y = app.offset + row*app.pixH
            r = 15
            canvas.create_oval(x-r,y-r,x+r,y+r, width = 4, outline = "green", fill = None)

def drawBends(app, canvas): # TODO fix this to match row, col convention
    if app.endsBendsOn:
        for (col,row) in app.bends:
            x = app.offset + col*app.pixW
            y = app.offset + row*app.pixH
            r = 15
            canvas.create_oval(x-r,y-r,x+r,y+r, width = 4, outline = "blue", fill = None)


def drawTrace(app, canvas):
    if app.traceOn  and app.trace[0] != (None,None):
        (startX,startY) = app.trace[0]
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
    findEnds(app) #TODO hard to imagine this should be here
    getTrace(app) #TODO put these in the right places
    findEnds(app)


def drawCharacter(app, canvas):
    drawOutline(app, canvas)
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
    drawCharacter(app,canvas)
    drawPrediction(app,canvas)
    

def main():
    #cs112_s21_week4_linter.lint()
    runApp(width=762, height=962)
    

if __name__ == '__main__':
    main()




















