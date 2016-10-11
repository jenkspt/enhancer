from keras.layers import Input, Dense, Convolution2D, MaxPooling2D, UpSampling2D
from keras.models import Model, Sequential
from keras.callbacks import TensorBoard, ModelCheckpoint
# tensorboard --logdir=/tmp/

import numpy as np

from datagen import datagen

# SETTINGS
target_size = (100, 100)
source_rescale = (25, 25)
batch_size = 1
nb_epoch = 50
# training samples
samples_per_epoch = 290496/32
# testing samples
nb_val_samples = 3020/32

### THE MODEL ####

input_img = Input(shape=(100, 100, 1))

x = Convolution2D(128, 3, 3, activation='relu', border_mode='same')(input_img)
# x = MaxPooling2D((2, 2), border_mode='same')(x)
# x = Convolution2D(64, 4, 4, activation='relu', border_mode='same')(x)
# x = MaxPooling2D((2, 2), border_mode='same')(x)


x = Convolution2D(128, 5, 5, activation='relu', border_mode='same')(x)
# x = UpSampling2D((2, 2))(x)
x = Convolution2D(64, 10, 10, activation='relu', border_mode='same')(x)
x = Convolution2D(16, 20, 20, activation='relu', border_mode='same')(x)
# x = UpSampling2D((2, 2))(x)
decoded = Convolution2D(1, 3, 3, activation='sigmoid', border_mode='same')(x)

autoencoder = Model(input_img, decoded)
autoencoder.compile(optimizer='adadelta', loss='mae')


### (end) THE MODEL ####

### THE DATA ####

train_generator = datagen('/home/ubuntu/enhancer/data/bing/train', source_rescale, target_size, batch_size)
test_generator = datagen('/home/ubuntu/enhancer/data/bing/test', source_rescale, target_size, batch_size)


autoencoder.fit_generator(train_generator,
                validation_data=test_generator,
                nb_epoch=nb_epoch,
                samples_per_epoch=samples_per_epoch,
                nb_val_samples=nb_val_samples,
                nb_worker=1,
                callbacks=[TensorBoard(log_dir='/tmp/enhancer', histogram_freq=0, write_graph=False),
                ModelCheckpoint('saved_models/model', monitor='val_loss', mode='auto')]
                )
