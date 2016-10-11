
import os
import random
from shutil import move

random.seed(1)

data_path='../../data/bing'
dirs = os.listdir(data_path)
random.shuffle(dirs)

split = .01
index = int(split*len(dirs))
train = dirs[index:]

os.makedirs(os.path.join(data_path, 'train'))
for dir_path in train:
	move(os.path.join(data_path, dir_path), os.path.join(data_path, 'train'))


os.makedirs(os.path.join(data_path, 'test'))
test = dirs[:index]
for dir_path in test:
	move(os.path.join(data_path, dir_path), os.path.join(data_path, 'test'))
