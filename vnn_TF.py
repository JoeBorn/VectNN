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
#fashion mnist with convolution layers is here: https://github.com/lmoroney/dlaicourse/blob/master/Course%201%20-%20Part%206%20-%20Lesson%202%20-%20Notebook.ipynb
# below comes from tutorial: https://www.tensorflow.org/tutorials/structured_data/preprocessing_layers

import pandas as pd
import tensorflow as tf
import csv

#************************************************
# Importing and formatting the data -pandas
# setting up and training the Neural Net
#************************************************
def trainNN(app):
  csv_file = 'C:/GitHub/VectNN/mnist_1_training_theta.csv'
  csv_test_file = 'C:/GitHub/VectNN/mnist_1_testing_theta.csv'
  dataframe = pd.read_csv(csv_file) 
  dataframe_testing = pd.read_csv(csv_test_file)
  dataframe = dataframe.fillna(value=0) #equiv to padding
  dataframe_testing = dataframe_testing.fillna(value=0)
  #print ("dataframe.head() \n",dataframe.head()) #prints out the table
  (train_ds) = df_to_dataset(dataframe, batch_size = 512) 
  (test_ds) = df_to_dataset(dataframe_testing, batch_size = 500)
  app.model = tf.keras.models.Sequential([
  tf.keras.layers.Dense(512, activation=tf.nn.relu),
  tf.keras.layers.Dense(10, activation=tf.nn.softmax)])
  app.model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])
  app.model.fit(train_ds, epochs=30, validation_data=test_ds)

# A utility method to create a tf.data dataset from a Pandas Dataframe, 
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
# Evaluating a new sample
#************************************************
def predictSample(app):
  csv_samples = 'sample.csv'
  dataframe_samples = pd.read_csv(csv_samples) 
  dataframe_samples = dataframe_samples.fillna(value=0)
  (sample_ds) = df_to_dataset(dataframe_samples, shuffle=False,batch_size = 1)
  print("Raw SoftMax Output:")
  predictions = app.model.predict(sample_ds)
  print(type(predictions[0]))
  print(predictions[0])
  return predictions[0]

def writeSample(app):
  with open('sample.csv', newline='',mode='w') as csvfile: # https://realpython.com/python-csv/#:~:text=Reading%20from%20a%20CSV%20file,which%20does%20the%20heavy%20lifting.
                traceWriter = csv.writer(csvfile, delimiter=',') # delimiter here means what it writes to delimit 
                traceWriter.writerow([i for i in range(36)]) #headers
                traceWriter.writerow(traceConverter(app))

'''
#(sample_ds) = df_to_dataset(dataframe_samples, shuffle=False,batch_size = 10)
csv_samples = 'C:/GitHub/VectNN/mnist_1_samples.csv'
dataframe_samples = pd.read_csv(csv_samples) 
dataframe_samples = dataframe_samples.fillna(value=0)

def openFile(app):
    with open('temp', newline='',mode='w') as csvfile: # https://realpython.com/python-csv/#:~:text=Reading%20from%20a%20CSV%20file,which%20does%20the%20heavy%20lifting.
                traceWriter = csv.writer(csvfile, delimiter=',')
                traceWriter.writerow([i for i in range(36)]) #headers
    for i in range(10):
        #path = f'C:/mnist/mnist_all_files/testing/{i}/'
        path = f'C:/mnist/mnist_all_files/training/{i}/'
        for filename in glob.glob(os.path.join(path, '*.png')):
            with open(os.path.join(os.getcwd(), filename), 'r') as f: # open in readonly mode
                app.img = Image.open(filename)
                try:
                    getMidPoints(app, app.img)
                    findEnds(app)
                    getTrace(app)
                except: 
                    print(filename)               
            with open('mnist_1_training.csv', newline='',mode='a') as csvfile: 
                traceWriter = csv.writer(csvfile, delimiter=',')
                traceWriter.writerow(traceConverter(app,i))
    print(f"done! no {i}")
'''

def traceConverter(app, i=0):
    hasGap = False
    result = [i] + [0]*25
    for i in range(min(len(app.trace), 12)): #truncates at 25 (w/o gap)
        if app.trace[i] != "gap":
            if hasGap == False:
                (x,y) = app.trace[i]
                result[2*i+1] =x
                result[2*i+2] =y 
            else: #new segment will start at index 25, proving a fixed point to NN
                (x,y) = app.trace[i]
                result.append(x)
                result.append(y)
        else: 
            hasGap = True
    return result[:36]

'''
test_loss, test_acc = model.evaluate(sample_ds, verbose=2)

print("\nTest accuracy: %5.2f" % (test_acc*100),"%\n")

print("Raw SoftMax Output:")
predictions = model.predict(sample_ds)
for i in range(10):
  print("No.",i,predictions[i])
  print()
'''