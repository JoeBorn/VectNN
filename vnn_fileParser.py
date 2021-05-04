'''
This file creates the CSV files either directly from the image pixels for the standard NN
or from the trace and other features for the VNN.

ThetaCSV is an experimental preparation of the data whos accuracy rate has not yet achieved 
that of the VNN, so it has not yet been deployed

if the CSV files have been provided, it is not necessary to run this file unless changes 
are made to the trace and related algorithms.

'''



import csv
from cmu_112_graphics import *
import glob
from PIL import Image
from vectorizer import *


def createStandardCSVFile(app):
    with open('mnist_standard_testing.csv', newline='',mode='a') as csvfile: # https://realpython.com/python-csv/#:~:text=Reading%20from%20a%20CSV%20file,which%20does%20the%20heavy%20lifting.
                traceWriter = csv.writer(csvfile, delimiter=',') # delimiter here means what it writes to delimit 
                traceWriter.writerow([i for i in range(785)]) #headers
    for i in range(10):
        #path = f'C:/mnist/mnist_all_files/testing/{i}/'
        path = f'C:/mnist/mnist_all_files/testing/{i}/'
        for filename in glob.glob(os.path.join(path, '*.png')):
            with open(os.path.join(os.getcwd(), filename), 'r') as f: # open in readonly mode
                app.img = Image.open(filename)
                app.pixels = list(app.img.getdata())
                try:
                    with open('mnist_standard_testing.csv', newline='',mode='a') as csvfile: # https://realpython.com/python-csv/#:~:text=Reading%20from%20a%20CSV%20file,which%20does%20the%20heavy%20lifting.
                        traceWriter = csv.writer(csvfile, delimiter=',') # delimiter here means what it writes to delimit 
                        traceWriter.writerow([i]+app.pixels)
                except: 
                    print(filename)          
    print(f"done! no {i}")

    #creates the training and testing csv files, used manually only when there's a change in trace, etc.
def createVNNCSVFile(app):
    with open('mnist_VNN_testing.csv', newline='',mode='a') as csvfile: # https://realpython.com/python-csv/#:~:text=Reading%20from%20a%20CSV%20file,which%20does%20the%20heavy%20lifting.
                traceWriter = csv.writer(csvfile, delimiter=',') # delimiter here means what it writes to delimit 
                traceWriter.writerow([i for i in range(36)]) #headers
    for i in range(10):
        #path = f'C:/mnist/mnist_all_files/training/{i}/'
        path = f'C:/mnist/mnist_all_files/testing/{i}/'
        for filename in glob.glob(os.path.join(path, '*.png')):
            with open(os.path.join(os.getcwd(), filename), 'r') as f: # open in readonly mode
                app.img = Image.open(filename)
                app.pixels = list(app.img.getdata())
                try:
                    getMidPoints(app)
                    findEnds(app)
                    getTrace(app)
                    with open('mnist_VNN_testing.csv', newline='',mode='a') as csvfile: # https://realpython.com/python-csv/#:~:text=Reading%20from%20a%20CSV%20file,which%20does%20the%20heavy%20lifting.
                        traceWriter = csv.writer(csvfile, delimiter=',') # delimiter here means what it writes to delimit 
                        traceWriter.writerow(traceConverter(app,i))
                except: 
                    print(filename)          
    print(f"done! no {i}")

def createThetaCSVFile(app):
    with open('mnist_theta_only_training.csv', newline='',mode='a') as csvfile: # https://realpython.com/python-csv/#:~:text=Reading%20from%20a%20CSV%20file,which%20does%20the%20heavy%20lifting.
                traceWriter = csv.writer(csvfile, delimiter=',') # delimiter here means what it writes to delimit 
                traceWriter.writerow([i for i in range(36)]) #headers
    for i in range(10):
        #path = f'C:/mnist/mnist_all_files/testing/{i}/'
        path = f'C:/mnist/mnist_all_files/training/{i}/'
        for filename in glob.glob(os.path.join(path, '*.png')):
            with open(os.path.join(os.getcwd(), filename), 'r') as f: # open in readonly mode
                app.img = Image.open(filename)
                app.pixels = list(app.img.getdata())
                try:
                    getMidPoints(app)
                    findEnds(app)
                    getTrace(app)
                    with open('mnist_theta_only_training.csv', newline='',mode='a') as csvfile: # https://realpython.com/python-csv/#:~:text=Reading%20from%20a%20CSV%20file,which%20does%20the%20heavy%20lifting.
                        traceWriter = csv.writer(csvfile, delimiter=',') # delimiter here means what it writes to delimit 
                        traceWriter.writerow(traceThetaConverter(app,i))
                except: 
                    print(filename)          
    print(f"done! no {i}")


#84% validation accuracy with 100 epochs with theta and magnitude
def traceThetaConverter(app, i=0):
    result = [i] + [0]*12
    if app.trace[0] == app.trace[-1]: result[1] = 28 #closed feature 
    hasGap = False
    i = 2
    while i <min(len(app.trace), 12): #truncates at 12 (w/o gap)
        if app.trace[i] != "gap":
            if app.trace[i-1] != "gap" and app.trace[i-2] != "gap":
                angle = getSortOfAngle(app.trace[i-2],app.trace[i-1],app.trace[i])
                if angle != None:
                    if hasGap == False:
                        result[i] = angle
                    else: #new segment will start at index 25, proving a fixed point to NN
                        result.append(angle)
            i += 1
        else: 
            hasGap = True
            startingPoint = True
            if app.trace[i-1] == app.trace[0]:
                result[1] = 28 # add "closed" feature to array
            if i+2<len(app.trace) and app.trace[i+1] != "gap" and app.trace[i+2] != "gap":
                angle1 = getSortOfAngle((-1,0),(0,0),app.trace[i+1])
                if angle1 != None:
                    result.append(angle1)
                angle2 = getSortOfAngle((0,0),app.trace[i+1],app.trace[i+2])
                if angle2 != None:
                    result.append(angle2)
            i +=3 
    return result[:36]


# returns an "angle" value 0 and 10*Pi between two head to tail vectors 
def getSortOfAngle(coord1,coord2,coord3):
    x1,y1 = coord1
    x2,y2 = coord2
    x3,y3 = coord3
    sign = -1
    if isLeft(coord1,coord2,coord3): sign = 1
    try:
        angle = math.pi+sign*(math.acos(((x2-x1)*(x3-x2)+(y2-y1)*(y3-y2))
        /(math.sqrt((x2-x1)**2+(y2-y1)**2)
        *math.sqrt((x3-x2)**2+(y3-y2)**2))))
        return angle*5
    except: 
        return None

#https://stackoverflow.com/questions/1560492/how-to-tell-whether-a-point-is-to-the-right-or-left-side-of-a-line
def isLeft(coord1,coord2,coord3):
    x1,y1 = coord1
    x2,y2 = coord2
    x3,y3 = coord3
    return ((x2 - x1)*(y3 - y1) - (y2 - y1)*(x3 - x1)) > 0