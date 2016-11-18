import os
import re
import numpy as np
from PIL import Image, ImageFile
import random
from glob import glob
import cv2


def datagen(path, source_rescale, target_size, batch_size=32, shuffle=True):
	files = glob(os.path.join(path, '*', '*.png'))
	if shuffle:
		random.shuffle(files)
	i = len(files)

	while True:
		source = np.ndarray((batch_size, target_size[1], target_size[0], 1), dtype=np.float32)
		target = np.ndarray((batch_size, target_size[1], target_size[0], 1), dtype=np.float32)

		for j in range(batch_size):
			i-=1
			ImageFile.LOAD_TRUNCATED_IMAGES = True
			with Image.open(os.path.join(path, files[i])) as img:
				# img = img.convert('L').resize(target_size)
				img = img.convert('L').resize(target_size)
				# %50 of the time flip images horizontally
				if random.randint(0,1):
					img = img.transpose(Image.FLIP_LEFT_RIGHT)

				# Scale down the input and then scale it back up
				source_img = img.resize(source_rescale).resize(target_size)
				# PIL images are (width, height) and numpy arrays are (height, width)
				source_scaled = np.asarray(source_img)/255.
				target_scaled = np.asarray(img)/255.
				source[j] = source_scaled.reshape(target_size[1], target_size[0], 1)
				target[j] = target_scaled.reshape(target_size[1], target_size[0], 1)

		yield (source, target)


		if i <= 0:
			# After going through all the images reshuffle
			i = len(files)
			if shuffle:
				random.shuffle(files)

if __name__ == '__main__':
	# path = '/home/ec2-user/ebs/enhancer/data/bing/test'
	path = '/Users/penn/galvanize/enhancer/data/test'
	gen = datagen(path, source_rescale=(56,56), target_size=(224, 224))
	X, y = next(gen)

	Image.fromarray(y[0].reshape((224, 224))*255).show()
	Image.fromarray(X[0].reshape((224, 224))*255).show()