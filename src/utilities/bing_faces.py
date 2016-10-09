

import requests
import json
from urllib.parse import urlsplit, parse_qs
from pandas import read_csv
import os
from time import sleep

"""
Microsoft Image Search API reference:
https://msdn.microsoft.com/en-us/library/dn760791.aspx

Website with list of names:
http://names.mongabay.com/male_names.htm
"""


class BingFaces():

	def __init__(self, key_file='api_keys.json'):
		'''
		args:
		key_file (str): path to json file {"bing": "<api key>"}

		initialize a session for pooled requests
		'''
		with open(key_file) as f:
			api_key = json.load(f)['bing']

		self.api_url = 'https://api.cognitive.microsoft.com/bing/v5.0/images/search'

		headers = {'Ocp-Apim-Subscription-Key': api_key}

		self.s = requests.Session()
		self.s.headers = headers


	def get_name(self, name, offset=0):
		'''
		A list of links to 400x400 faces is retreived by searching bing for common
		names.

		args:
		name (str): the name to be used in the bing search i.e. 'Robert'
		offset (int): for pagination. Not used in this implimentation
		'''
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
		'''
		Loop through names and retrieve links.
		'''
		while self.names:
			try:
				self.get_name(self.names.pop(0))
			except Exception as e:
				print(e)
			# Api limits 5 requests per second
			sleep(.21)
		with open('remaining_names.txt', 'w') as f:
			f.write('\n'.join(self.names))


if __name__ == '__main__':
	names = []
	if os.path.isfile('remaining_names.txt'):
		# If the program exits prematurely for any reason, pick up where we left off
		names = [line.rstrip('\n') for line in open('remaining_names.txt')]

	else:
		# start with a list of names
		male = list(read_csv('male_names_2.tsv', sep='\t')['Name'])
		female = list(read_csv('female_names_2.tsv', sep='\t')['Name'])

		# List of 2000 names, alternating male-female.
		# Capitalize first letter in name and lowercase the rest
		names = list(set([item.title() for sublist in zip(male, female) for item in sublist]))
		bing = BingFaces()


	bing.names = names
	bing.get_names()
	

