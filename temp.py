import PIL, copy
from PIL import Image 
import decimal

#TODO: grid screws up when canvas stretched
file = 'C:/GitHub/VectNN/JB_5.png'
#file = 'C:/mnist/mnist_all_files/training/7/10394.png'  
img = Image.open(file)
img.show()