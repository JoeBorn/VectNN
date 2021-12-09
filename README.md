**Vectorized Character Recognizer**

This program creates vector strokes that approximately trace the outline of characters in the MNIST handwritten digits database 
it then feeds those vectors into a neural network and makes a prediction of which number it is 
You can compare that prediction with the with the output of a fully connected neural network that received the raw pixel information

This exercise was meant to test if a 'human interpretable' algorithm/layer could improve the performance of the network.  So far, I found that it
makes it more resistant to adversarial attacks (you can see for yourself in the "fool the robot" game) and seems to perform better when 
tested on samples outside of the training data (ie computer fonts) 

The vector layer also powers a "Fool the Robot" game where the users goal is to create digits that are 
recognizable to users, but can "fool the AI" into thinking they are different numbers. I found it useful in giving some clues on 
the standard neural network makes its predictions.  

It is worth noting that this program compares the results of a standard fully connected neural network. Adding convolutional layers
increase the performance of the predictions substantially.

You can watch a video demo here: https://youtu.be/Y5XkBUskwu8



[![Github Dark](https://github.com/JoeBorn/VectNN/blob/main/VNN_Screenshot_2.png)](https://youtu.be/Y5XkBUskwu8)
