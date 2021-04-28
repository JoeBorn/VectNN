import csv
from cmu_112_graphics import *
import glob
from PIL import Image

def createStandardCSVFile(app):
    with open('mnist_standard_training.csv', newline='',mode='a') as csvfile: # https://realpython.com/python-csv/#:~:text=Reading%20from%20a%20CSV%20file,which%20does%20the%20heavy%20lifting.
                traceWriter = csv.writer(csvfile, delimiter=',') # delimiter here means what it writes to delimit 
                traceWriter.writerow([i for i in range(785)]) #headers
    for i in range(10):
        #path = f'C:/mnist/mnist_all_files/testing/{i}/'
        path = f'C:/mnist/mnist_all_files/training/{i}/'
        for filename in glob.glob(os.path.join(path, '*.png')):
            with open(os.path.join(os.getcwd(), filename), 'r') as f: # open in readonly mode
                app.img = Image.open(filename)
                app.pixels = list(app.img.getdata())
                try:
                    with open('mnist_standard_training.csv', newline='',mode='a') as csvfile: # https://realpython.com/python-csv/#:~:text=Reading%20from%20a%20CSV%20file,which%20does%20the%20heavy%20lifting.
                        traceWriter = csv.writer(csvfile, delimiter=',') # delimiter here means what it writes to delimit 
                        traceWriter.writerow([i]+app.pixels)
                except: 
                    print(filename)          
    print(f"done! no {i}")
