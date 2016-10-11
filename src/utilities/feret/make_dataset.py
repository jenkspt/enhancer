from PIL import Image
import random
import json
import boto3

import tarfile
import os
from os import path
import shutil
import glob

from multiprocessing import cpu_count
from multiprocessing.pool import Pool


class MakeDataset():
	def __init__(self, config='../../config.json'):
		'''
		Load s3 bucket and local directory configurations. Create paths
		based on info in config.json
		'''
		with open(config) as f:
			self.config = json.load(f)

		# Get the basename of the remote file i.e. "original-colorferet.tar"
		self.colorferet = path.basename(self.config['key']).replace('.tar', '')
		self.colorferet_dir = path.join(self.config['local'], self.colorferet)
		self.colorferet_tar = path.join(self.config['local'], self.colorferet + '.tar')
		self.feret = path.join(self.config['local'], 'feret')
		self.original = path.join(self.feret, 'original_512x768_color_True')

	def s3_download(self):
		'''
		Downloads the file from the s3 bucket specified in the config.json file.
		Doesn't download if the file already exists in specified local path
		'''

		# Cancel the download if directory or tar file or exists with the value of self.colorferet
		if os.path.isdir(self.colorferet_dir):
			print('(Cancelling download) The directory "{}" already exists.'.format(self.colorferet))
			return True
		elif tarfile.is_tarfile(self.colorferet_tar):
			print('(Cancelling download) The file "{}.tar" already exists.'.format(self.colorferet))
			return True
		
		# Download the s3 bucket
		s3 = boto3.resource('s3')
		s3.meta.client.download_file(self.config['bucket'], self.config['key'], self.colorferet_dir)
		return True

	def untar_colorferet(self):

		# cd to the data directory and untar the dataset
		print('(Unpacking) file: "{}"\n......'.format(self.colorferet_tar))
		os.chdir(self.config['local'])
		with tarfile.open(self.colorferet_tar, 'r:') as tar:
			# Only extract the specifi files needed in the tarball
			tar.extract(path.join(self.colorferet_dir, 'dvd1', 'data', 'images'))
			tar.extract(path.join(self.colorferet_dir, 'dvd1', 'data', 'images'))

	def move_files(self):
		'''
		Moves all compressed image files from colorfered directory to new directory structure
		'''

		# Make directories to hold dataset with new structure
		os.makedirs(self.feret, exist_ok=True)
		pool = Pool(processes=cpu_count())

		for dvd in ['dvd1', 'dvd2']:
			files = glob.glob(path.join(self.colorferet_dir, dvd, 'data', 'images', '*', '*.ppm.bz2'))
			dest = self.original
			os.makedirs(dest, exist_ok=True)
			# Creates an iterable of move args so that they can be mapped to different processes
			z = zip(files, [dest]*len(files))
			pool.starmap(shutil.move, z)
		pool.close()
		pool.join()

	def untar_images(self):
		'''
		Decompress all image files in 'images', 'smaller' and 'thumbnails' directories
		located at data/feret/originals.
		Uses multiprocessing pool
		'''
		pool = Pool(processes=cpu_count())
		dir = self.original
		bz2_files = glob.glob(os.path.join(dir, '*.ppm.bz2'))

		print('Extracting files in {}'.format(dir))
		# couldn't get python tarfile library to work on this
		cmd_list = ['bzip2 -d {}'.format(file) for file in bz2_files]
		pool.map(os.system, cmd_list)

		pool.close()
		pool.join()

	def make_dataset(source_dim, target_dim, color=False):
		'''
		args: 
		source_dim (tuple): Size for image to be scaled down to for model input
		target_dim (tuple): Image dimensions to be used in model
		color       (bool): Color or grayscale

		original image dimensions (512x768)
		'''

		feret = self.feret
		original = self.original

		# Get all the file names. remove the profile images
		original_files = set(glob.glob(path.join(original), '*.ppm'))\
			- set(glob.glob(path.join(original), '__pr__.ppm'))\
			- set(glob.glob(path.join(original), '__pl__.ppm'))

		scale_files(original_files, source_dim)
		scale_files(original_files, target_dim)
		


	def scale_files(original_files, dim):
		'''
		args:
		original_files (list): List of the full path of images to scale
		dim 		  (tuple): target (width, height) to scale the images to
		'''
		
		name = '{}x{}_color_{}'.format(*dim, color)
		new = path.join(feret, 'images', name)
		# Check if the directory already exists and as contents
		if os.path.isdir(new) and os.listdir(new):
			return

		pool = Pool(processes=cpu_count()*2)
		os.makedirs(new)
		train = path.join(new, 'train')
		test = path.join(new, 'test')
		os.mkdir(train)
		os.mkdir(test)
		# Create list of args for pool
		n = len(original_files)
		# Get the new file path with old file name
		new_files = [path.join(train, path.basename(original)) for original in original_files]
		z = zip(original_files, new_files, [dim]*n, [color]*n)
		pool.starmap(scale_image, z)

		# Sort the list of new files in place by basename
		new_files.sort(key=lambda x: path.basename(x))
		# seed to 42 so all test sets will have same random images
		random.seed(42)
		random.shuffle(new_files)
		# Get test files list
		n_test = int(len(new_files) * .1)
		test_files = new_files[-n_test:]
		# Use multithreaded move...just cause
		z = zip(test_files, [test]*n_test)
		pool.starmap(shutil.move, z)
		pool.close()
		pool.join()




	def scale_image(image_file, save_path, dim, color):
		'''
		args:
		(str) image_file: Path to the image file to be scaled
		(str) save_path: Path to save the scaled image
		(tuple) dim: dimensions to scale to with format (width, height)

		Open the images, transform (scale, color) and save to train directory
		'''
		if not color:
			Image.open(image_file).convert('L').resize(dim).save(save_path)
		else:
			Image.open(image_file).resize(dim).save(save_path)

if __name__ == '__main__':
	maker = MakeDataset(config='/Users/penn/galvanize/enhancer/config.json')
	#maker.s3_download()
	maker.untar_colorferet()
	#maker.move_files()
	#maker.untar_images()