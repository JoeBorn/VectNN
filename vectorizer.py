'''copyright 2021 Joe Born
all rights reserved '''
#import cs112_s21_week4_linter
from cmu_112_graphics import *
import random, string, math, time
import PIL
from PIL import Image 


#TODO: figure out how to deal with THRESHOLD instead of as global
THRESHOLD = 120 # lightness threshold to determine edges of chars
# 0 is black, 255 is white, letters are light on black background
img = Image.open('C:/Users/joebo_000/Downloads/VNN/mnist_all_files/training/6/13.png')
#img.show()
def appStarted(app):
    app.contigLinesVisible = True 
    findEnds(app)
    app.pixel0 =100
    app.pixWH = 20
    app.selCol = 0
    app.selRow = 0

def mousePressed(app, event):
    app.selCol, app.selRow = getGridCoords(app,event.x,event.y)
    
def getGridCoords(app,x,y):
    col = (x-app.pixel0)//app.pixWH
    row = (y-app.pixel0)//app.pixWH
    return col, row

def keyPressed(app, event):
    if event.key.lower() == 'space':
        app.contigLinesVisible = not app.contigLinesVisible


def getMidPoints(image): #finds the midpoints, taking horizontal slices
    pixels = list(image.getdata()) # returns one long flattened list: row1, row2, etc
    (width, height) = img.size #28,28 TODO: is this a global?
    leadEdge = 0
    vertThreshold = 7 # length of vertical segment to break up with multi points
    midsImageList = list() #a list that collects the midpoint pixels into a format PIL can create a PNG, etc
    midsList = list() # a list of the coordinate tuples of the midpoints
    outlineList = list() # list of leading and trailing edges, should form an outline
    for i in range(width*height):
        midsImageList.append(255) # 255 is white
    for x in range(width):
        for y in range(height):
            if pixels[getIndex(x,y)] > THRESHOLD and leadEdge == 0: 
                leadEdge = y # leading edge found
            if pixels[getIndex(x,y)] <= THRESHOLD and leadEdge != 0: #trailing edge found
                #TODO remove single pixel "turds"
                trailEdge = y-1 #TODO: Check, but I think because <=THRESHOLD
                if abs(leadEdge-trailEdge) > vertThreshold:
                    midpoint = leadEdge + 1
                    del midsImageList[getIndex(x,midpoint)] #TODO: is this still needed?
                    #clean up if not
                    midsImageList.insert(getIndex(x,midpoint), 0)
                    midsList.append((x,midpoint))
                    midpoint = trailEdge -1
                    del midsImageList[getIndex(x,midpoint)]
                    midsImageList.insert(getIndex(x,midpoint), 0)
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
    i = y*width + x
    return i

midsImageList, midsList, outlineList = getMidPoints(img)

mids_image = Image.new("L",(28,28)) 
mids_image.putdata(midsImageList)

#print(midsList)
#mids_image.save('C:/Users/joebo_000/Downloads/VNN/4_9_mids.png')
#mids_image.show()

#returns a list of (segLength) length vector angles 
# + starting and ending point coordinates, and number of segments
#TODO: resolve conflict between one end and start with potentially 
#multiple segments

def getSnake(mids_image,image, segLength=1):
    #start at beginning of midsList 
    # (smallest x (smallest y within that if more than one x))
    #check x+1 and x+2
    #if no left, the mark as start and go right
    # if left, keep going until no more left (recursion base case)
    #if no right, mark end and return segment

    return snake,startPoint,endPoint,segments

#takes original "image" list and two midpoints(tuple with two ints(row and column coords)) 
# and returns if they are contiguous
#presumes that columns aren't more than one apart
def areContiguous(image,mid1,mid2): 
    pixels = list(image.getdata()) 
    (x1,y1) = (mid1[0], mid1[1])
    (x2,y2) = (mid2[0], mid2[1])
    if not isConnected(image, mid1,mid2):
        return False      
    if abs(x1-x2) > 1 and abs(y1-y2) > 1: 
        m = (y2-y1)/(x2-x1) # m is the slope
        b = y1+.5 -m*(x1+.5) # b is the y intercept
        priorRowSegPixels = [i for i in range(min(x1,x2),max(x1,x2)+1)]
        #print("PRSP: ", priorRowSegPixels)
        for row in range(min(y1,y2),max(y1,y2)+1):
            xStart = (row-b)/m
            xEnd = (row +1-b)/m
            largestX = max(x1,x2)
            smallestX = min(x1,x2)
            xMin = max(smallestX,int(min(xStart,xEnd)))
            xMax = min(largestX,int(max(xStart,xEnd)))# frankly I'm not sure why
            # int works here, I would have thought math.ceil, but it works 
            # and has to do with simple counting
            segPixelFound = False #every row must find a char pixel
            curRowSegPixels =[] # lists allow for testing contiguity of char pixels between rows
            # ie. there must be a path to walk over a gap
            #print("xs", xStart,"xe",xEnd)
            for col in range (smallestX,largestX+1):
                if pixels[getIndex(col,row)] > THRESHOLD:
                    curRowSegPixels.append(col)
                    if col >= xMin and col <= xMax: #and col in priorRowSegPixels: #char pixel found
                        segPixelFound = True
                    #print("col: ",col,"cRSP: ", curRowSegPixels, xMin,xMax)
            priorRowSegPixels = curRowSegPixels
            if segPixelFound == False:
                #print("fails diag test", col, row, priorRowSegPixels, curRowSegPixels)
                return False
    return True

def isConnected(image,mid1,mid2): 
    pixels = list(image.getdata()) 
    (x1,y1) = (mid1[0], mid1[1])
    (x2,y2) = (mid2[0], mid2[1])
    if abs(x1-x2)==1 and abs(y1-y2)==1: #by definition so to speak
        return True
    elif x1 == x2:
        for row in range(min(y1,y2),max(y1,y2)+1):
            if pixels[getIndex(x1,row)] < THRESHOLD: #gap found
                #print("false1")
                return False
        return True
    elif y1 == y2:
        for col in range(min(x1,x2),max(x1,x2)+1):
            if pixels[getIndex(col, y1)] < THRESHOLD: #gap found
                #print("false2")
                return False
        return True
    else:
        #print("rec coords: ", x1,y1,x2,y2)
        if x2 > x1: xinc = 1
        elif x1 > x2: xinc = -1
        else: xinc = 0
        if y2 > y1:yinc = 1
        elif y1 > y2:yinc = -1
        else: yinc = 0
        if pixels[getIndex(x2,y2-yinc)] > THRESHOLD and isConnected(image,(x1,y1),(x2,y2-yinc)):
            return True
        elif pixels[getIndex(x2-xinc,y2)] > THRESHOLD and isConnected(image,(x1,y1),(x2-xinc,y2)):
            return True
        else:
            #print("false3")
            return False    

#print("isConnected1", isConnected(img,(7,18),(10,12)))
#print("isConnected2", isConnected(img,(12,18),(19,11)))


def contiguousPairs(midsList, img):
    contMidStart = list()
    contMidEnd = list()
    maxConnections = 100 #TODO: think about this.effectively eliminated for now 
    #max no of pairs to "connect to" allowed  
    #(doubled by prior "smaller" coords with their own connection allocation)
    for coord1 in range (len(midsList)):
        connections = 0
        for coord2 in range(len(midsList)):
            if connections <= maxConnections and coord1 != coord2 and \
                areContiguous(img,midsList[coord1], midsList[coord2]):
                #distanceSq = (midsList[coord1][0]-midsList[coord2][0])**2 + \
                #(midsList[coord1][1]-midsList[coord2][1])**2
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
    for coords in midsList:
        ((x,y))=coords
        x=105+x*20
        y=105+y*20
        canvas.create_rectangle(x,y,x+10,y+10, fill="gray")

def drawGrid(app, canvas):
    pixel28 = 100 + 28*20
    #canvas.create_rectangle(100,100, 380,380)
    for x in range(app.pixel0,pixel28, app.pixWH):
        canvas.create_line(x,app.pixel0,x,pixel28)
    for y in range(app.pixel0,pixel28, app.pixWH):
        canvas.create_line(app.pixel0,y,pixel28,y)
    for x in range(app.pixel0,pixel28, app.pixWH*5):
        canvas.create_line(x,app.pixel0,x,pixel28, width = 2)
    for y in range(app.pixel0,pixel28, app.pixWH*5):
        canvas.create_line(app.pixel0,y,pixel28,y, width = 2)
    canvas.create_text(100,700, text =f'sel Coord(row,col) : {app.selRow} , {app.selCol}')

def drawOutline(app, canvas):
    canvas.create_text(100,50, text=f'Threshold: {THRESHOLD}', font='Arial 11')
    for coords in outlineList:
        ((x,y))=coords
        x=100+x*20
        y=100+y*20
        canvas.create_rectangle(x,y,x+20,y+20, fill ="lightgray")

def drawContiguousConnections(app, canvas):
    if app.contigLinesVisible == True:
        offset = 110# from 0,0 to center of pertinent pixel
        (contMidStart, contMidEnd) = contiguousPairs(midsList, img)
        for i in range(len(contMidStart)):
            (x1,y1) = contMidStart[i]
            (x1,y1) = offset + x1*20, offset + y1*20 
            (x2,y2) = contMidEnd[i]
            (x2,y2) = offset + x2*20, offset + y2*20
            canvas.create_line(x1,y1,x2,y2, fill = "red", width =2)

def drawEnds(app, canvas):
    offset = 110 #TODO fix local var used multiple places
    for (x,y) in app.ends:
        x = offset + x*20
        y = offset + y*20
        r = 13
        canvas.create_oval(x-r,y-r,x+r,y+r, width = 2, outline = "green", fill = None)

def findEnds(app):
    ''' go through all the midpoints & apply two part test: 1 end has all 
    connected points in "one direction", ie up down, left, right etc &
    2. those connected points must be connected to one another '''
    (contMidStart, contMidEnd) = contiguousPairs(midsList, img) #copied from drawContiguousConnections
    app.ends = []
    i = 1 #TODO missing the last midpoint? first, it's missing something
    allRorL = True # all contMidEnds are on one side of contMidStart
    allUorD = True # all contMidEnds are above or all are below contMidStart
    while i < len(contMidStart):
        if contMidStart[i] != contMidStart[i-1] or i == len(contMidStart)-1:
            if allRorL or allUorD: # if it has only one pair, it's an end
                app.ends.append(contMidStart[i-1]) 
            i += 1
            allRorL = True # reset checks
            allUorD = True 
        else: #if it's a repeat then perform the checks.
            (x1,y1) = contMidStart[i] 
            (x2,y2) = contMidEnd[i-1]
            (x3,y3) = contMidEnd[i]
            if (x2-x1)*(x3-x1) <= 0:
                allRorL = False
            if (y2-y1)*(y3-y1) <= 0:
                allUorD = False
            i += 1
        
    #print ("app.ends: ", app.ends)


def testAreContiguous():
    print("Testing areContiguous()...", end="")
    #assert(areContiguous(img,(9,17),(10,10)) == False)
    assert(areContiguous(img,(8,21),(9,17)) == False)
    print("Passed!")


def redrawAll(app, canvas):
    #drawCharacter(app, canvas)
    drawGrid(app,canvas)
    drawOutline(app, canvas)
    drawMidPoints(app, canvas)
    drawContiguousConnections(app, canvas)
    drawEnds(app, canvas)
    #drawSnake(app, canvas)
    #testAreContiguous()

def main():
    #cs112_s21_week4_linter.lint()
    runApp(width=1000, height=800)
    

if __name__ == '__main__':
    main()




















