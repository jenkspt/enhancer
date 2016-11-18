from keras.layers import Input, Dense, Convolution2D, MaxPooling2D, UpSampling2D
from keras.models import Model, Sequential
from keras.callbacks import TensorBoard, ModelCheckpoint
# tensorboard --logdir=/tmp/

import numpy as np

from datagen import datagen
from loss import gradient_importance

# SETTINGS
target_size = (224, 224)
source_rescale = (56, 56)
batch_size = 32
nb_epoch = 50
# training samples
samples_per_epoch = 290496/batch_size
# testing samples
nb_val_samples = 3020/batch_size

### THE MODEL ####

input_img = Input(shape=(*target_size, 1))

x = Convolution2D(256, 3, 3, activation='relu', border_mode='same')(input_img)
x = MaxPooling2D((2, 2), border_mode='same')(x)

x = Convolution2D(256, 3, 3, activation='relu', border_mode='same')(x)
x = MaxPooling2D((2, 2), border_mode='same')(x)

x = Convolution2D(512, 3, 3, activation='relu', border_mode='same')(x)
x = Convolution2D(512, 3, 3, activation='relu', border_mode='same')(x)
x = UpSampling2D((2, 2))(x)

x = Convolution2D(256, 3, 3, activation='relu', border_mode='same')(x)
x = UpSampling2D((2, 2))(x)

x = Convolution2D(1, 3, 3, activation='sigmoid', border_mode='same')(x)


model = Model(input_img, x)
model.compile(optimizer='adadelta', loss=gradient_importance)


### (end) THE MODEL ####

### THE DATA ####

train_generator = datagen('/home/ec2-user/ebs/enhancer/data/bing/train', source_rescale, target_size, batch_size)
test_generator = datagen('/home/ec2-user/ebs/enhancer/data/bing/test', source_rescale, target_size, batch_size)


model.fit_generator(train_generator,
                validation_data=test_generator,
                nb_epoch=nb_epoch,
                samples_per_epoch=samples_per_epoch,
                nb_val_samples=nb_val_samples,
                nb_worker=1,
                callbacks=[TensorBoard(log_dir='/tmp/enhancer', histogram_freq=0, write_graph=False),
                ModelCheckpoint('saved_models/model_laplace.h5', monitor='val_loss', mode='auto')]
                )
