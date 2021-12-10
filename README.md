**Vectorized Character Recognizer**

Intro:

This program creates vector strokes that approximately trace the outline of characters in the MNIST handwritten digits database 
it then feeds those vectors into a neural network and makes a prediction of which number it is 
You can compare that prediction with the with the output of a fully connected neural network that received the raw pixel information

This exercise was meant to test if a 'human interpretable' algorithm/layer could improve the performance of the network.  So far, I found that it
makes it more resistant to adversarial attacks (you can see for yourself in the "fool the robot" game) and seems to perform better when 
tested on samples outside of the training data (ie computer fonts) 

The vector layer also powers a "Fool the Robot" game where the users goal is to create digits that are 
recognizable to users, but can "fool the AI" into thinking they are different numbers. I found it useful in giving some clues on 
the standard neural network makes its predictions.  

It is worth noting that this program compares the results of of the vectorizer + fully connected neural network 
to feeding the pixels directly into a standard fully connected neural network. The best performance on this database 
uses a convolutional neural network: http://yann.lecun.com/exdb/mnist/ which increases the performance of the predictions substantially.

So a lot more testing and experimentation would be needed to say anything conclusive, but I nonetheless find it interesting
in what it illustrates about the potential role of hybrid systems that integrate NN and "explainable" layers.

Demo video here: https://youtu.be/Y5XkBUskwu8

to run:

Put the following 8 files and 1 directory into whatever directory you'd like to run the program from:

cmu_112_graphics.py, 
vectorizer.py, 
vnn_fileParser.py, 
vnn_TF.py, 
mnist_standard_testing.csv, 
mnist_standard_training.csv, 
mnist_VNN_testing.csv, 
mnist_VNN_training.csv,
imageFiles

in the imageFiles directory, place all the included image files

Libraries needed to run the application:

PIL, tensorflow, pandas

[![Github Dark](https://github.com/JoeBorn/VectNN/blob/main/VNN_Screenshot_2.png)](https://youtu.be/Y5XkBUskwu8)
