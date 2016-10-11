import os
import re
import numpy as np
from PIL import Image, ImageFile
import random
from glob import glob


def datagen(path, source_rescale=(50,50), target_size=(100, 100), batch_size=32, shuffle=True):
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
				img = img.convert('L').resize(target_size)
				# %50 of the time flip images horizontally
				if random.randint(0,1):
					img = img.transpose(Image.FLIP_LEFT_RIGHT)

				# Scale down the input and then scale it back up
				source_img = img.resize(source_rescale).resize(target_size)
				# PIL images are (width, height) and numpy arrays are (height, width)
				source[j] = (np.asarray(source_img)/255).reshape(target_size[1], target_size[0], 1)
				target[j] = (np.asarray(img)/255.).reshape(target_size[1], target_size[0], 1)

		yield (source, target)



		if i <= 0:
			# After going through all the images reshuffle
			i = len(files)
			if shuffle:
				random.shuffle(files)

if __name__ == '__main__':
	gen = datagen('../../../data/bing/test')
	x = next(gen)