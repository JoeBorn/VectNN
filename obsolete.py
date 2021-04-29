#trains a standard NN directly from images without trace or any filters from this project
#https://github.com/lmoroney/dlaicourse/blob/master/Exercises/Exercise%202%20-%20Handwriting%20Recognition/Exercise2-Answer.ipynb
def standardFCTrain(app):
  mnist = tf.keras.datasets.mnist

  (x_train, y_train),(x_test, y_test) = mnist.load_data()
  x_train, x_test = x_train / 255.0, x_test / 255.0

  app.model = tf.keras.models.Sequential([
    tf.keras.layers.Flatten(input_shape=(28, 28)),
    tf.keras.layers.Dense(512, activation=tf.nn.relu),
    tf.keras.layers.Dense(10, activation=tf.nn.softmax)
  ])
  app.model.compile(optimizer='adam',
                loss='sparse_categorical_crossentropy',
                metrics=['accuracy'])

  app.model.fit(x_train, y_train, epochs=4,validation_data=(x_test,y_test))

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