import os
import requests
from PIL import Image
from io import BytesIO
from multiprocessing.pool import ThreadPool
from glob import glob

def download_bing_images(data_dir='../../data/bing'):
	'''
	args:
	data_dir (str): path to bing data directory

	Download the images from the urls in all the text files
	'''
	pool = ThreadPool(150)
	files = glob(os.path.join(data_dir, '*', '*.txt'))
	for filename in files:
		print('Mapping links from {}'.format(filename))
		dest_path = os.path.dirname(filename)
		links = [line.rstrip('\n') for line in open(filename)]
		pool.starmap(save_image, zip(links, [dest_path]*len(links)))


def save_image(url, dest_path):
	'''
	args:
	url (str): remote image to save locally
	dest_path (str): location to save image

	Download and save an individual image
	'''
	try:
		im = Image.open(BytesIO(requests.get(url, timeout=1).content))

		name = os.path.basename(dest_path)
		original_name = os.path.splitext(os.path.basename(url))[0]
		if not im.size == (400, 400):
			return
		im.save(os.path.join(dest_path, '{}_{}.png'.format(name, original_name)))
	except Exception as e:
		print(e)
		return


if __name__ == '__main__':
	download_bing_images()