from PIL import Image
import random
import json
import boto3
import re

import tarfile
import bz2
import os
from os import path
import shutil
import glob

from multiprocessing import cpu_count
from multiprocessing.pool import Pool

# chmod 777 colorferet.tar


class DataUtil():
	def __init__(self, config='../../config.json'):
		'''
		Load s3 bucket and local directory configurations. Create paths
		based on info in config.json
		'''
		with open(config) as f:
			self.config = json.load(f)

		self.colorferet = path.basename(self.config['key']).replace('.tar', '')
		self.colorferet_dir = path.join(self.config['local'], self.colorferet)
		self.colorferet_tar = path.join(self.config['local'], self.colorferet + '.tar')
		self.feret = path.join(self.config['local'], 'feret')

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

	def make_dataset(self, split=.075, exclude_views={'pl', 'pr'}):
		'''
		args: 
		source_dim (tuple): Size for image to be scaled down to for model input
		target_dim (tuple): Image dimensions to be used in model
		color       (bool): Color or grayscale
		exclude_views (iterable): view to exlude, such as 'pr' for profile right, and pl for profile left

		original image dimensions (512x768)
		'''
		# Create the directories for the source and target data
		train_dir = path.join(self.feret, 'train')
		test_dir = path.join(self.feret, 'test')
		os.makedirs(train_dir, exist_ok=True)
		os.makedirs(test_dir, exist_ok=True)

		# all of the views -> see original-documentation.txt for description
		views = {'fa', 'fb', 'pl', 'hl', 'ql', 'pr', 'hr', 'qr', 'ra', 'rb', 'rc', 'rd', 're'} - set(exclude_views)
		pattern = re.compile('colorferet\/dvd[12]\/data\/images\/\d{5}\/.{13}('+ '|'.join(views) + ')_?[a-c]?\.ppm.bz2')
		# Read the tarfile and get the names of all directories and files in a list
		with tarfile.open(self.colorferet_tar, 'r:') as tarball:
			# select files in images folder with .bz2 extension
			image_names = list(filter(lambda x: bool(pattern.match(x)), tarball.getnames())) 

		print('IMAGE NAMES: ', len(image_names))
		# Create the jobs
		n_process = cpu_count()
		n_jobs = n_process*16
		chunk_size=int(1 + len(image_names)/n_jobs)
		chunks = [image_names[x:x+chunk_size] for x in range(0, len(image_names), chunk_size)]

		pool = Pool(processes=n_process)
		# These args are the same for each job
		other_args = [(self.colorferet_tar, train_dir, test_dir, split)]*len(chunks)
		z = zip(chunks, other_args)

		pool.starmap(extract_images, z)
		pool.close()
		pool.join()


def extract_images(image_paths, other_args):
	colorferet_tar, train_dir, test_dir, split = other_args
	# Seed so test set always has same files
	random.seed(42)
	with tarfile.open(colorferet_tar, 'r:') as tarball:
		for image_path in image_paths:
			basename = path.basename(image_path).replace('.ppm.bz2', '')
			# Extract the file from the tarball and then read as bz2 file object
			with bz2.open(tarball.extractfile(image_path)) as file:
				with Image.open(file) as img:
					# Easy way to make train test split with files
					if random.random() <= split:
						img.save(path.join(test_dir, basename + '.png'))
					else:
						img.save(path.join(train_dir, basename + '.png'))




if __name__ == '__main__':
	data_util = DataUtil('/Users/penn/galvanize/enhancer/config.json')
	data_util.make_dataset()
