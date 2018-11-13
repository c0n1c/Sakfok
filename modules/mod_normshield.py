#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests

class Normshield(object):

	def __init__(self, db, logger):
		self.db = db
		self.logger = logger
		self.apikey = ""
		self.URL_BASE = 'https://api.fraudguard.io'
		self.headers = {'Content-Type': 'application/json'}

	def ip_lookup(ip, username, password):
		response = requests.get('https://api.cymon.io/v2/auth/login', data=self.apikey, headers=self.headers)
		token = json.loads(response)["jwt"]
		self.headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
		res = requests.get(self.URL_BASE + '/ip/' + ip , verify=True, auth=HTTPBasicAuth(username, password))
		jsonObj = res.json()
		with open('output_fraudguard.csv', 'a') as file:
			file.write(ip + ',' + jsonObj['isocode'] + ',' + jsonObj['country'] + ',' + jsonObj['threat'] + ',' + jsonObj['risk_level'] + '\n')
