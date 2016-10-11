
import os
from PIL import Image
from glob import glob

train='/home/ubuntu/enhancer/data/bing/train'
test='/home/ubuntu/enhancer/data/bing/test'
train_files = glob(os.path.join(train, '*', '*.png'))
test_files = glob((os.path.join(test, '*', '*.png')))

target_size = (100,100)

for file in train_files:
	try:
		with Image.open(file) as img:
			img = img.convert('L').resize(target_size)
	except:
		print('Removing: ', file)
		os.remove(file)

for file in test_files:
	try:
		with Image.open(file) as img:
			img = img.convert('L').resize(target_size)
	except:
		print('Removing: ', file)
		os.remove(file)