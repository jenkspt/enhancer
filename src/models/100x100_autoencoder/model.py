from keras.layers import Input, Dense, Convolution2D, MaxPooling2D, UpSampling2D
from keras.models import Model, Sequential
from keras.callbacks import TensorBoard, ModelCheckpoint

import numpy as np

from datagen import datagen

# SETTINGS
target_size = (28, 28)
# batch_size = 128
nb_epoch = 50
# training samples
samples_per_epoch = 290496
# testing samples
nb_val_samples = 3020

### THE MODEL ####

input_img = Input(shape=(28, 28, 1))

x = Convolution2D(16, 3, 3, activation='relu', border_mode='same')(input_img)
x = MaxPooling2D((2, 2), border_mode='same')(x)
x = Convolution2D(8, 3, 3, activation='relu', border_mode='same')(x)
x = MaxPooling2D((2, 2), border_mode='same')(x)
x = Convolution2D(8, 3, 3, activation='relu', border_mode='same')(x)
encoded = MaxPooling2D((2, 2), border_mode='same')(x)

# at this point the representation is (8, 4, 4) i.e. 128-dimensional

x = Convolution2D(8, 3, 3, activation='relu', border_mode='same')(encoded)
x = UpSampling2D((2, 2))(x)
x = Convolution2D(8, 3, 3, activation='relu', border_mode='same')(x)
x = UpSampling2D((2, 2))(x)
x = Convolution2D(16, 3, 3, activation='relu')(x)
x = UpSampling2D((2, 2))(x)
decoded = Convolution2D(1, 3, 3, activation='sigmoid', border_mode='same')(x)

autoencoder = Model(input_img, decoded)
autoencoder.compile(optimizer='adadelta', loss='binary_crossentropy')


### (end) THE MODEL ####

### THE DATA ####

train_generator = datagen('/home/ubuntu/enhancer/data/bing/train', target_size=target_size)
test_generator = datagen('/home/ubuntu/enhancer/data/bing/test', target_size=target_size)


autoencoder.fit_generator(train_generator,
                validation_data=test_generator,
                nb_epoch=nb_epoch,
                samples_per_epoch=samples_per_epoch,
                nb_val_samples=nb_val_samples,
                nb_worker=1,
                callbacks=[TensorBoard(log_dir='/tmp/autoencoder', histogram_freq=0, write_graph=False),
                ModelCheckpoint('model', monitor='val_loss', mode='auto')]
                )
