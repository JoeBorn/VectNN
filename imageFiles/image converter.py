
from cmu_112_graphics import *
from PIL import Image, ImageOps
import glob

path = f'imageFiles/fonts/'
for filename in glob.glob(os.path.join(path, '*.png')):
    with open(os.path.join(os.getcwd(), filename), 'r') as f: # open in readonly mode
        img = Image.open(filename)
        img = ImageOps.grayscale(img)
        img = ImageOps.invert(img)
        img =img.resize((28,28), Image.NEAREST)
        filename = filename + "scaled.png"
        img.save(filename)
'''
file = 'imageFiles/fonts/0.png'

img = Image.open(file)
img = ImageOps.grayscale(img)
img =img.resize((28,28), Image.NEAREST)
img.save('0converted.png')
'''
