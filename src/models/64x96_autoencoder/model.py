from keras.layers import Input, Dense, Convolution2D, MaxPooling2D, UpSampling2D
from keras.models import Model, Sequential

from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img
from keras.callbacks import TensorBoard

from datagen import datagen

# SETTINGS
target_size = (64, 96)
batch_size = 32
nb_epoch = 10
# training samples
samples_per_epoch = 7897
# testing samples
nb_val_samples = 766

train_path = '/Users/penn/galvanize/enhancer/data/feret/train/faces'
test_path = '/Users/penn/galvanize/enhancer/data/feret/test/faces'

train_generator = datagen(train_path, target_size)
test_generator = datagen(test_path, target_size)

model = Sequential()

model.add(Convolution2D(48, 3, 3, batch_input_shape=(32, 96, 64, 1), activation='relu', border_mode='same'))
model.add(MaxPooling2D((2, 2), border_mode='same'))
model.add(Convolution2D(24, 3, 3, activation='relu', border_mode='same'))
model.add(MaxPooling2D((2, 2), border_mode='same'))
model.add(Convolution2D(24, 3, 3, activation='relu', border_mode='same'))
model.add(MaxPooling2D((2, 2), border_mode='same'))

# at this point the representation is (8, 4, 4) i.e. 128-dimensional

model.add(Convolution2D(24, 3, 3, activation='relu', border_mode='same'))
model.add(UpSampling2D((2, 2)))
model.add(Convolution2D(24, 3, 3, activation='relu', border_mode='same'))
model.add(UpSampling2D((2, 2)))
model.add(Convolution2D(48, 3, 3, activation='relu', border_mode='same'))
model.add(UpSampling2D((2, 2)))
model.add(Convolution2D(1, 3, 3, activation='sigmoid', border_mode='same'))

model.compile(optimizer='rmsprop', loss='mse')

model.fit_generator(train_generator,
                nb_epoch=nb_epoch,
                samples_per_epoch=samples_per_epoch,
                validation_data=test_generator,
                nb_val_samples=nb_val_samples,
                callbacks=[TensorBoard(log_dir='tensorboard')])