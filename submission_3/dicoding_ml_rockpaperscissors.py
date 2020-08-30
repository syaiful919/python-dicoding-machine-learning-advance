# -*- coding: utf-8 -*-
"""dicoding-ml-basic-rockpaperscissors.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1MPLpkRTbpWH9veJ91SzW8wuHN5wfbXr0
"""

import tensorflow as tf
from tensorflow.keras.optimizers import RMSprop
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# dataset yg digunakan adalah dataset rockpaperscrissors yang telah dipisahkan antara data training & validation
# dengan perbandingan 8 : 2, kemudian diupload ke g-drive
# link: https://drive.google.com/file/d/1yi-81Ni0IJA1OMV_VC9FqetKT0zc05c-/view?usp=sharing
from google.colab import drive
drive.mount('/content/gdrive')

!ls '/content/gdrive/My Drive/sample_data/'

import zipfile
local_zip = '/content/gdrive/My Drive/sample_data/rockpaperscissors82.zip'
zip_ref = zipfile.ZipFile(local_zip, 'r')
zip_ref.extractall('/content/gdrive/My Drive/sample_data/rockpaperscissors/')
zip_ref.close()

import os
base_dir = '/content/gdrive/My Drive/sample_data/rockpaperscissors/rockpaperscissors82/images'
train_dir = os.path.join(base_dir, 'train')
validation_dir = os.path.join(base_dir, 'val')

os.listdir('/content/gdrive/My Drive/sample_data/rockpaperscissors/rockpaperscissors82/images/train')

os.listdir('/content/gdrive/My Drive/sample_data/rockpaperscissors/rockpaperscissors82/images/val')

train_paper_dir = os.path.join(train_dir, 'paper')
train_rock_dir = os.path.join(train_dir, 'rock')
train_scissors_dir = os.path.join(train_dir, 'scissors')

validation_paper_dir = os.path.join(validation_dir, 'paper')
validation_rock_dir = os.path.join(validation_dir, 'rock')
validation_scissors_dir = os.path.join(validation_dir, 'scissors')

train_datagen = ImageDataGenerator(
                    rescale=1./255,
                    rotation_range=20,
                    horizontal_flip=True,
                    vertical_flip=True,
                    width_shift_range=20,
                    height_shift_range=20,
                    shear_range = 0.2,
                    fill_mode = 'nearest')

test_datagen = ImageDataGenerator(
                    rescale=1./255,
                    rotation_range=20,
                    horizontal_flip=True,
                    vertical_flip=True,
                    width_shift_range=20,
                    height_shift_range=20,
                    shear_range = 0.2,
                    fill_mode = 'nearest')

train_generator = train_datagen.flow_from_directory(
        train_dir, 
        target_size=(100, 150), 
        batch_size=32,
        color_mode='grayscale',
        class_mode='categorical')

validation_generator = test_datagen.flow_from_directory(
        validation_dir, 
        target_size=(100, 150),
        batch_size=32,
        color_mode='grayscale',
        class_mode='categorical')

model = tf.keras.models.Sequential([
    tf.keras.layers.Conv2D(32, (3,3), activation='relu', input_shape=(100, 150, 1)),
    tf.keras.layers.MaxPooling2D(2, 2),
    tf.keras.layers.Conv2D(64, (3,3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.Conv2D(128, (3,3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.Conv2D(128, (3,3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(512, activation='relu'),
    tf.keras.layers.Dense(3, activation='softmax')
])

model.compile(loss='categorical_crossentropy',
              optimizer=tf.optimizers.RMSprop(),
              metrics=['accuracy'])

class stopCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('accuracy')>0.92 and logs.get('val_accuracy')>0.92):
      print("\nAkurasi telah mencapai 92%!")
      self.model.stop_training = True
callbacks = stopCallback()

history = model.fit(
      train_generator,
      steps_per_epoch=25,  
      epochs=30,
      validation_data=validation_generator,
      validation_steps=5, 
      callbacks=[callbacks],
      verbose=2)

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
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])

plt.title('Model Accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train', 'Val'], loc='upper right')
plt.show()

converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

with tf.io.gfile.GFile('model.tflite', 'wb') as f:
  f.write(tflite_model)
