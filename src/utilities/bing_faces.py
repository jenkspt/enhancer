

import requests
import json
from urllib.parse import urlsplit, parse_qs
from pandas import read_csv
import os
from time import sleep

"""
(Image Search Api Reference)[https://msdn.microsoft.com/en-us/library/dn760791.aspx]
"""


class BingFaces():

	def __init__(self, key_file='api_keys.json', male_names_tsv='male_names.tsv', female_names_tsv='female_names.tsv'):

		with open(key_file) as f:
			api_key = json.load(f)['bing']

		male = list(read_csv(male_names_tsv, sep='\t', index_col='Rank')['Name'])
		female = list(read_csv(female_names_tsv, sep='\t', index_col='Rank')['Name'])

		# List of 2000 names, alternating male-female.
		# Capitalize first letter in name and lowercase the rest
		self.names = [item.title() for sublist in zip(male, female)
		                         for item in sublist]

		self.api_url = 'https://api.cognitive.microsoft.com/bing/v5.0/images/search'

		headers = {'Ocp-Apim-Subscription-Key': api_key}

		self.s = requests.Session()
		self.s.headers = headers


	def get_name(self, name, offset=0):
		payload = {
			'q': name,
			'offset': offset,
			'count': '150',
    		'mkt': 'en-us',
    		'safeSearch': 'Moderate',
    		'imageContent': 'Face',
    		'imageType': 'Photo',
    		'color': 'ColorOnly',
    		'aspect': 'Square',
    		'height': 400,
    		'width': 400
		}
		r = self.s.get(self.api_url, params=payload).json()
		# Get the image from the json response
		# For some reason it redirects through bing, so I extract the link from
		# the query param r
		links = [parse_qs(urlsplit(item['contentUrl']).query)['r'][0]
		                  for item in r['value']]

		path = os.path.join('../../data/bing', name.lower())
		os.makedirs(path)
		with open(os.path.join(path, name.lower() + '.txt'), 'w') as f:
			f.write('\n'.join(links))




	def get_names(self):
		while self.names:
			try:
				self.get_name(self.names.pop(0))
			except Exception as e:
				print(e)
				break
			# Api limits 5 requests per second
			sleep(.21)
		with open('remaining_names.txt', 'w') as f:
			f.write('\n'.join(self.names))


if __name__ == '__main__':
	bing = BingFaces()
	bing.names = list(set([line.rstrip('\n') for line in open('remaining_names.txt')]))
	bing.get_names()
	

