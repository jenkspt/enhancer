import os
import re
import numpy as np
from PIL import Image, ImageFile
import random
from glob import glob


def datagen(path, target_size=(100, 100), batch_size=32):
	files = glob(os.path.join(path, '*', '*.png'))
	random.shuffle(files)
	i = len(files)

	while True:
		i-=1
		target = np.ndarray((batch_size, target_size[1], target_size[0], 1), dtype=np.float32)
		for j in range(batch_size):
			ImageFile.LOAD_TRUNCATED_IMAGES = True
			with Image.open(os.path.join(path, files[i])) as img:
				img = img.convert('L').resize(target_size)
				# %50 of the time flip images horizontally
				if random.randint(0,1):
					img = img.transpose(Image.FLIP_LEFT_RIGHT)
				# PIL images are (width, height) and numpy arrays are (height, width)
				target[j] = (np.asarray(img)/255.).reshape(target_size[1], target_size[0], 1)
				target[j] = np.clip(target[j], 0., 1.)
		yield (target, target)



		if i <= 0:
			# After going through all the images reshuffle
			i = len(files)
			random.shuffle(files)

if __name__ == '__main__':
	gen = datagen('../../../data/bing/test')
	x = next(gen)