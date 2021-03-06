# -*- coding: utf-8 -*-
"""timeseries (submission).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/19F3V8am8OCsN2si83rwXvqGlw_T6pHoV
"""

import pandas as pd
import numpy as np
from keras.layers import Dense, LSTM
import matplotlib.pyplot as plt
import tensorflow as tf

dataset_url = "https://raw.githubusercontent.com/syaiful919/datasets/master/szeged_weather/weatherHistory.csv"

"""note: data diperoleh dari https://www.kaggle.com/budincsevity/szeged-weather?select=weatherHistory.csv"""

df = pd.read_csv(dataset_url)

df.head()

df.isnull().sum()

dates = df['Formatted Date'].values
temp  = df['Temperature (C)'].values
 
 
plt.figure(figsize=(15,5))
plt.plot(dates, temp)
plt.title('Temperature average',
          fontsize=20);

def windowed_dataset(series, window_size, batch_size, shuffle_buffer):
    series = tf.expand_dims(series, axis=-1)
    ds = tf.data.Dataset.from_tensor_slices(series)
    ds = ds.window(window_size + 1, shift=1, drop_remainder=True)
    ds = ds.flat_map(lambda w: w.batch(window_size + 1))
    ds = ds.shuffle(shuffle_buffer)
    ds = ds.map(lambda w: (w[:-1], w[1:]))
    return ds.batch(batch_size).prefetch(1)

from sklearn.model_selection import train_test_split
dates_train, dates_test, label_train, label_test = train_test_split(dates, temp, test_size=0.2)

data_train = windowed_dataset(label_train, window_size=60, batch_size=100, shuffle_buffer=1000)
data_test = windowed_dataset(label_test, window_size=60, batch_size=100, shuffle_buffer=1000)

model = tf.keras.models.Sequential([
  tf.keras.layers.LSTM(60, return_sequences=True),
  tf.keras.layers.LSTM(60),
  tf.keras.layers.Dense(30, activation="relu"),
  tf.keras.layers.Dense(10, activation="relu"),
  tf.keras.layers.Dense(1),
])

optimizer = tf.keras.optimizers.SGD(lr=1.0000e-04, momentum=0.9)
model.compile(loss=tf.keras.losses.Huber(),
              optimizer=optimizer,
              metrics=["mae"])

class stopCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('mae')<10):
      print("\n MAE < 10 %!")
      self.model.stop_training = False
    if(logs.get('val_mae')<5):
      print("\n MAE val < 5 %!")
      self.model.stop_training = True
callbacks = stopCallback()

history = model.fit(data_train,  validation_data=(data_test), epochs=30, callbacks=[callbacks], verbose=2)

import matplotlib.pyplot as plt

fig, ax = plt.subplots()
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])

plt.title('Model loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train', 'Val'], loc='upper right')
plt.show()

fig, ax = plt.subplots()
plt.plot(history.history['mae'])
plt.plot(history.history['val_mae'])

plt.title('Model MAE')
plt.ylabel('MAE')
plt.xlabel('Epoch')
plt.legend(['Train', 'Val'], loc='upper right')
plt.show()

