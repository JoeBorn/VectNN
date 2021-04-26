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

#createCSVFile(app)

def createCSVFile(app):
    with open('mnist_1_testing.csv', newline='',mode='a') as csvfile: # https://realpython.com/python-csv/#:~:text=Reading%20from%20a%20CSV%20file,which%20does%20the%20heavy%20lifting.
                traceWriter = csv.writer(csvfile, delimiter=',') # delimiter here means what it writes to delimit 
                traceWriter.writerow([i for i in range(35)]) #headers
    for i in range(10):
        #path = f'C:/mnist/mnist_all_files/testing/{i}/'
        path = f'C:/mnist/mnist_all_files/testing/{i}/'
        for filename in glob.glob(os.path.join(path, '*.png')):
            with open(os.path.join(os.getcwd(), filename), 'r') as f: # open in readonly mode
                app.img = Image.open(filename)
                #print(filename)
                try:
                    getMidPoints(app, app.img)
                    findEnds(app)
                    getTrace(app)
                except: 
                    print(filename)
                
            with open('mnist_1_testing.csv', newline='',mode='a') as csvfile: # https://realpython.com/python-csv/#:~:text=Reading%20from%20a%20CSV%20file,which%20does%20the%20heavy%20lifting.
                traceWriter = csv.writer(csvfile, delimiter=',') # delimiter here means what it writes to delimit 
                traceWriter.writerow(traceConverter(i,app))
    print(f"done! no {i}")

def traceConverter(i,app):
    hasGap = False
    result = [0 for i in range(25)]
    for i in range(min(len(app.trace), 25)): #truncates at 25 (w/o gap)
        if app.trace[i] != "gap":
            if hasGap == False:
                (x,y) = app.trace[i]
                result.insert(i,x)
                result.insert(i,y)
            else: #new segment will start at index 25, proving a fixed point to NN
                (x,y) = app.trace[i]
                result.append(x)
                result.insert(y)
        else: 
            hasGap = True
    return result


