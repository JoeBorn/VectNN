# -*- coding: utf-8 -*-

"""VNN.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1C1YLw4LHLHaysC7Q--J4Cjzg6JHZ-O_q


!pip install -q sklearn #not clear how long this install persists, given warnings about my freebee colab...
# incredibly, this doesn't work, downloads some corrupted variant: csv_file = tf.keras.utils.get_file('mnist_training_0s_svg.csv', 'https://drive.google.com/file/d/15wHU7o7GUr0242AbNdj_wqLbbM9MCVsx/view?usp=sharing')
# have to figure out the right format for google drive, seems like a joke, but take a deep breath.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# from https://github.com/lmoroney/dlaicourse/blob/master/Exercises/Exercise%202%20-%20Handwriting%20Recognition/Exercise2-Answer.ipynb
# I also stuck this up on colab: https://colab.research.google.com/drive/1_JhsMpNSwSgkdxFOPTbmL5ljW7YS8Dv6?usp=sharing

#fashion mnist with convolution layers is here: https://github.com/lmoroney/dlaicourse/blob/master/Course%201%20-%20Part%206%20-%20Lesson%202%20-%20Notebook.ipynb

# below comes from tutorial: https://www.tensorflow.org/tutorials/structured_data/preprocessing_layers
#my assesment is that a csv file is fine, with classification in column 0 and a series of numbers after that representing all the coordinates, with the alpha stripped out
"""

import numpy as np
import pandas as pd
import tensorflow as tf
import pathlib

from numpy import int32
from tensorflow import keras #different syntax, taken from https://colab.research.google.com/drive/1554Yoj9uIRyeeYLX6fPJqC9ZBgnXiSjX?usp=sharing
from sklearn.model_selection import train_test_split
from tensorflow.keras import layers

csv_file = 'C:/GitHub/VectNN/mnist_1_training_mostall_mod.csv'
csv_test_file = 'C:/GitHub/VectNN/mnist_1_testing_mod.csv'

max_features = 26 #

dataframe = pd.read_csv(csv_file) 
dataframe_testing = pd.read_csv(csv_test_file) # header=None, names = list(range(0,max_features)))
dataframe = dataframe.fillna(value=0) #equiv to padding
dataframe_testing = dataframe_testing.fillna(value=0)


print ("dataframe.head() \n",dataframe.head()) #prints out the table

# A utility method to create a tf.data dataset from a Pandas Dataframe, from https://colab.research.google.com/drive/1ElCfhpOmmyKiG4jzdhadoi5YEjYq0YP8?usp=sharing
def df_to_dataset(dataframe, shuffle=True, batch_size=32):
  dataframe = dataframe.copy()
  labels = dataframe.pop('0') # 0 is the column holding the classifier- 
  print("labels: ", labels)
  dataframe = abs(dataframe) / 28.0 #normalize the features
  ds = tf.data.Dataset.from_tensor_slices((dataframe,labels)) # was (dict(dataframe)),labels
  if shuffle:
    ds = ds.shuffle(buffer_size=len(dataframe))
  ds = ds.batch(batch_size)
  ds = ds.prefetch(batch_size)
  return ds

(train_ds) = df_to_dataset(dataframe, batch_size = 512) 
print(type(train_ds))
(test_ds) = df_to_dataset(dataframe_testing, batch_size = 500)

model = tf.keras.models.Sequential([
  #tf.keras.layers.Flatten()
  tf.keras.layers.Dense(512, activation=tf.nn.relu),
  tf.keras.layers.Dense(10, activation=tf.nn.softmax)
])
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

model.fit(train_ds, epochs=30, validation_data=test_ds)
#model.evaluate(x_test, y_test)

