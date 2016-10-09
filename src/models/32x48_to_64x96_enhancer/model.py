import keras
#import tensorflow as tf
from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img
from scipy.misc import imresize
from PIL import Image
import numpy as np

# SETTINGS
target_size = (64, 96)
source_rescale = (32, 48)
batch_size = 32
nb_epoch = 10
samples_per_epoch = 8000


datagen = ImageDataGenerator(
		horizontal_flip=True,
		fill_mode='nearest',
		dim_ordering='tf')

train_generator = datagen.flow_from_directory(
	'../../../data/feret/train',
	target_size=target_size,
	batch_size=batch_size,
	class_mode=None,
	color_mode='grayscale')

test_generator = datagen.flow_from_directory(
	'../../../data/feret/test',
	target_size=target_size,
	batch_size=batch_size,
	class_mode=None,
	color_mode='grayscale')


""" THE MODEL """
input_img = Input(shape=(64, 96, 1))

x = Convolution2D(64, 3, 3, activation='sigmoid', border_mode='same')(input_img)
x = Convolution2D(48, 3, 3, activation='relu', border_mode='same')(x)
x = MaxPooling2D((2, 2), border_mode='same')(x)
x = Convolution2D(32, 3, 3, activation='relu', border_mode='same')(x)
x = MaxPooling2D((2, 2), border_mode='same')(x)

# at this point the representation is (32, 7, 7)
x = Convolution2D(32, 3, 3, activation='relu', border_mode='same')(x)
x = Convolution2D(32, 3, 3, activation='relu', border_mode='same')(x)
x = UpSampling2D((2, 2))(x)

x = Convolution2D(32, 3, 3, activation='relu', border_mode='same')(x)
x = UpSampling2D((2, 2))(x)

x = Convolution2D(32, 3, 3, activation='relu', border_mode='same')(x)
x = UpSampling2D((2, 2))(x)
x = Convolution2D(32, 3, 3, activation='relu', border_mode='same')(x)
x = UpSampling2D((2, 2))(x)
decoded = Convolution2D(1, 3, 3, activation='sigmoid', border_mode='same')(x)

autoencoder = Model(input_img, decoded)
# per-pixel binary crossentropy loss
autoencoder.compile(optimizer='adadelta', loss='mse')






y_batch = train_generator.next()
X_batch = np.empty_like(y_batch)
im_scale = y_batch.shape[1:]

for i, b in enumerate(y_batch):
	# Only for grayscale
	X_batch[i] = imresize(imresize(b.reshape(b.shape[:-1]), source_rescale), target_size).reshape(b.shape)

print(X_batch.shape)
print(y_batch.shape)




# here's a more "manual" example
for e in range(nb_epoch):
    print 'Epoch', e
    batche_number = 0
    for batch in datagen.flow_from_directory():
    	# batch.shape = (samples, width, height, channels)
    	y_batch = batch
    	X_batch = 
        loss = model.train(X_batch, Y_batch)
        batche_number += 1
        if batch_number >= len(samples_per_epoch) / batch_size:
            # we need to break the loop by hand because
            # the generator loops indefinitely
            break


# for batch in train_generator:
# 	# original image dimensions (512x768)
# 	# batch.shape = (samples, width, height, channels)
# 	print(batch.shape)
# 	print(type(batch))
# 	i += 1
# 	if i >= 1:
# 		break  # otherwise the generator would loop indefinitely