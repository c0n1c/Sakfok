#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from requests.auth import HTTPBasicAuth
import logging
import sys
import os
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('logs_saxa.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(funcName)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
scrlog = logging.StreamHandler()
scrlog.setFormatter(logging.Formatter("[%(levelname)s] - %(message)s"))
logger.addHandler(scrlog)

def fraudguard(ip, username, password):
	res = requests.get('https://api.fraudguard.io/ip/' + ip , verify=True, auth=HTTPBasicAuth(username, password))
	jsonObj = res.json()
	with open('output_fraudguard.csv', 'a') as file:
		file.write(ip + ',' + jsonObj['isocode'] + ',' + jsonObj['country'] + ',' + jsonObj['threat'] + ',' + jsonObj['risk_level'] + '\n')

if __name__ == "__main__":

	try:
		with open(os.getenv("HOME") + '/.fraudguard.api') as keyfile:
			api_fraudguard = keyfile.read().strip()
			username = api_fraudguard.split(':')[0]
			password = api_fraudguard.split(':')[1]
			logger.info('API key has been loaded')
	except Exception as e:
		logger.warning('[Error] Please put your fraudguard API Key in file "$HOME/.fraudguard.api" %s', e)
		sys.exit()
	ips = open('ip.txt', 'r')
	for ip in ips:
		fraudguard(ip, username, password)