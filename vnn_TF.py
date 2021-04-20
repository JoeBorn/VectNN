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

import pandas as pd
import tensorflow as tf

#************************************************
# Importing and formatting the data -pandas
#************************************************

csv_file = 'C:/GitHub/VectNN/mnist_1_training.csv'
csv_test_file = 'C:/GitHub/VectNN/mnist_1_testing.csv'
csv_samples = 'C:/GitHub/VectNN/mnist_1_samples.csv'

dataframe = pd.read_csv(csv_file) 
dataframe_testing = pd.read_csv(csv_test_file)
dataframe_samples = pd.read_csv(csv_samples) 
dataframe = dataframe.fillna(value=0) #equiv to padding
dataframe_testing = dataframe_testing.fillna(value=0)
dataframe_samples = dataframe_samples.fillna(value=0)

print ("dataframe.head() \n",dataframe.head()) #prints out the table

# A utility method to create a tf.data dataset from a Pandas Dataframe, 
# from https://colab.research.google.com/drive/1ElCfhpOmmyKiG4jzdhadoi5YEjYq0YP8?usp=sharing
def df_to_dataset(dataframe, shuffle=True, batch_size=32):
  dataframe = dataframe.copy()
  labels = dataframe.pop('0') # 0 is the column holding the classifier- 
  dataframe = abs(dataframe) / 28.0 #normalize the features
  ds = tf.data.Dataset.from_tensor_slices((dataframe,labels)) 
  if shuffle:
    ds = ds.shuffle(buffer_size=len(dataframe))
  ds = ds.batch(batch_size)
  ds = ds.prefetch(batch_size)
  return ds

#************************************************
# Inputting, setting up, running the Neural Net
#************************************************

(train_ds) = df_to_dataset(dataframe, batch_size = 512) 
(test_ds) = df_to_dataset(dataframe_testing, batch_size = 500)
(sample_ds) = df_to_dataset(dataframe_samples, shuffle=False,batch_size = 10)

model = tf.keras.models.Sequential([
  tf.keras.layers.Dense(512, activation=tf.nn.relu),
  tf.keras.layers.Dense(10, activation=tf.nn.softmax) 
])

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

model.fit(train_ds, epochs=20, validation_data=test_ds)

#************************************************
# Evaluating the Results
#************************************************

test_loss, test_acc = model.evaluate(sample_ds, verbose=2)

print("\nTest accuracy: %5.2f" % (test_acc*100),"%\n")

print("Raw SoftMax Output:")
predictions = model.predict(sample_ds)
for i in range(10):
  print("No.",i,predictions[i])
  print()
