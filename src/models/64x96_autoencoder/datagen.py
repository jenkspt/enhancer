
import os
import re
import numpy as np
from PIL import Image
import random


# original image dimensions (512x768)
def crop_center(im):
	width, height = im.size   # Get dimensions
	left = (width - new_width)/2
	top = (height - new_height)/2
	right = (width + new_width)/2
	bottom = (height + new_height)/2

	im.crop((left, top, right, bottom))

"""
768-512 = 256

"""


PATTERN = re.compile('.+\.png')

# def datagen(path, target_size=(64, 96), batch_size=32):
# 	files = [f for f in os.listdir(path) if bool(PATTERN.match(f))]
# 	random.shuffle(files)
# 	i = len(files)

# 	while True:
# 		i-=1
# 		for _ in range(batch_size):
# 			with Image.open(os.path.join(path, files[i])) as img:
# 				img = img.convert('L').resize(target_size)
# 				# %50 of the time flip images horizontally
# 				if random.randint(0,1):
# 					img = img.transpose(Image.FLIP_LEFT_RIGHT)
# 				# PIL images are (width, height) and numpy arrays are (height, width)
# 				ar = (np.asarray(img, dtype=np.float32)/255).reshape(target_size[1], target_size[0], 1)
# 				yield (ar, ar)

# 		if i <= 0:
# 			# After going through all the images reshuffle
# 			i = len(files)
# 			random.shuffle(files)



def datagen(path, target_size=(64, 96), batch_size=32):
	files = [f for f in os.listdir(path) if bool(PATTERN.match(f))]
	random.shuffle(files)
	i = len(files)

	while True:
		for j in range(batch_size):
			target = np.ndarray((batch_size, target_size[1], target_size[0], 1), dtype=np.float32)
			i-=1
			with Image.open(os.path.join(path, files[i])) as img:
				img = img.convert('L').resize(target_size)
				# %50 of the time flip images horizontally
				if random.randint(0,1):
					img = img.transpose(Image.FLIP_LEFT_RIGHT)
				# PIL images are (width, height) and numpy arrays are (height, width)
				target[j] = (np.asarray(img)/255).reshape(target_size[1], target_size[0], 1)
			yield (target, target)

		if i <= 0:
			# After going through all the images reshuffle
			i = len(files)
			random.shuffle(files)

if __name__ == '__main__':
	gen = datagen('/home/ubuntu/enhancer/data/feret/test')
	x = next(gen)
