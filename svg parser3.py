#https://stackoverflow.com/questions/15857818/python-svg-parser
import os
import numpy
import csv
import glob #https://stackoverflow.com/questions/18262293/how-to-open-every-file-in-a-folder
#import re #https://stackoverflow.com/questions/1249388/removing-all-non-numeric-characters-from-string-in-python
from xml.dom import minidom

#TODO: Open all svg files, see if there's something off the shelf

path = 'C:/Users/joebo_000/Downloads/VNN/mnist_all_files/testing/9'
for filename in glob.glob(os.path.join(path, '*.svg')):
    with open(os.path.join(os.getcwd(), filename), 'r') as f: # open in readonly mode
        doc = minidom.parse(filename)  # parseString also exists
        path_strings = [path.getAttribute('d') for path
            in doc.getElementsByTagName('path')]
        doc.unlink() # no idea what this does
        for line in path_strings: # removing the back square background and all the alpha characters (M, c,l, etc), "line = 6" adds the classifier
            line = "9 " + line.replace("M0 140 l0 -140 140 0 140 0 0 140 0 140 -140 0 -140 0 0 -140z","").replace("M","").replace("m","").replace("l","").replace("L","").replace("c","").replace("C","").replace("z","")
            #line = re.sub("[^0-9]","",line) #removed spaces too
        delimited_path_strings = line.split()
        #delimited_path_strings = line.replace('\r','') # tried to get rid of the extra line breaks, but this broke up everything.

        for line in delimited_path_strings:
            abs_val_line = line.replace("-","") #I'm a hack, but I forgive myself 
            if abs_val_line.isnumeric() != True:
                print("theres a non numeric value in the delimited_path_strings: ",line) 

        with open('mnist_all_svg_testing.csv', mode='a') as csvfile: # https://realpython.com/python-csv/#:~:text=Reading%20from%20a%20CSV%20file,which%20does%20the%20heavy%20lifting.
            svg_writer = csv.writer(csvfile, delimiter=',') # delimiter here means what it writes to delimit 
            svg_writer.writerow(delimited_path_strings)

#Note: padding, regularization will be done in VNN program

