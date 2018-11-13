#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests
from urllib.parse import quote_plus

class Cymon(object):

	def __init__(self, db, logger):
		self.db = db
		self.logger = logger
		self.apikey = ""
		self.URL_BASE = 'https://cymon.io/v2/ioc/search'
		self.headers = {'Content-Type': 'application/json'}

	def get(self, method, params=None):
		response = requests.get('https://api.cymon.io/v2/auth/login', data=self.apikey, headers=self.headers)
		token = response.json()["jwt"]
		self.headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
		r = self.session.get(self.URL_BASE + method, params=params)
		r.raise_for_status()
		return r

	def post(self, method, params, headers=None):
		r = self.session.post(self.URL_BASE + method, data=json.dumps(params), headers=headers)
		r.raise_for_status()
		return r

	def ip_lookup(self, ip_addr):
		r = self.get('/ip/' + ip_addr)
		return json.loads(r.text)

	def ip_events(self, ip_addr):
		r = self.get('/ip/' + ip_addr + '/events')
		return json.loads(r.text)

	def ip_domains(self, ip_addr):
		r = self.get('/ip/' + ip_addr + '/domains')
		return json.loads(r.text)

	def ip_urls(self, ip_addr):
		r = self.get('/ip/' + ip_addr + '/urls')
		return json.loads(r.text)

	def domain_lookup(self, name):
		r = self.get('/domain/' + name)
		return json.loads(r.text)

	def url_lookup(self, location):
		r = self.get('/url/' + quote_plus(location))
		return json.loads(r.text)

	def ip_blacklist(self, tag, days=1, limit=10, offset=0):
		''' supported tags: malware, botnet, spam, phishing, dnsbl, blacklist '''
		r = self.get('/blacklist/ip/' + tag + '/?days=%d&limit=%d&offset=%d' %(days,limit,offset))
		return json.loads(r.text)

	def domain_blacklist(self, tag, days=1, limit=10, offset=0):
		''' supported tags: malware, botnet, spam, phishing, dnsbl, blacklist '''
		r = self.get('/blacklist/domain/' + tag + '/?days=%d&limit=%d&offset=%d' %(days,limit,offset))
		return json.loads(r.text)