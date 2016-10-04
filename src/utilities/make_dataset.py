from PIL import Image
import os
import json
import boto3
import shutil
import tarfile
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
		self.colorferet = os.path.basename(self.config['key']).replace('.tar', '')
		self.colorferet_dir = os.path.join(self.config['local'], self.colorferet)
		self.colorferet_tar = os.path.join(self.config['local'], self.colorferet + '.tar')

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
			tar.extractall()

	def move_files(self):
		'''
		Moves all compressed image files from colorfered directory to new directory structure
		'''

		# Make directories to hold dataset with new structure
		os.makedirs(os.path.join(self.config['local'], 'feret', 'originals'), exist_ok=True)
		pool = Pool(processes=cpu_count())

		move_list = []
		for dvd in ['dvd1', 'dvd2']:
			files = glob.glob(os.path.join(self.colorferet_dir, dvd, 'data', 'images', '*', '*.ppm.bz2'))
			dest = os.path.join(self.config['local'], 'feret', 'originals', 'images')
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
		dir = os.path.join(self.config['local'], 'feret', 'originals', 'images')
		bz2_files = glob.glob(os.path.join(dir, '*.ppm.bz2'))

		print('Extracting files in {}'.format(dir))
		cmd_list = ['bzip2 -d {}'.format(file) for file in bz2_files]
		pool.map(os.system, cmd_list)

		pool.close()
		pool.join()


#for filename in os.listdir(os.getcwd()):

if __name__ == '__main__':
	maker = MakeDataset(config='/Users/penn/galvanize/enhancer/config.json')
	#maker.s3_download()
	#maker.untar_colorferet()
	maker.move_files()
	maker.untar_images()