#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import hashlib
import argparse
import logging
import requests
import json
import time
from configparser import ConfigParser
import pymongo

class VirusTotal(object):
	def __init__(self, db, logger):
		self.apikey = ""
		self.URL_BASE = "https://www.virustotal.com/vtapi/v2/"
		self.HTTP_OK = 200
		self.db = db
		self.is_public_api = True
		self.PUBLIC_API_SLEEP_TIME = 15
		self.logger = logger
		self.type_item = ""

	def retrieve_report(self, item):
		try:
			if self.type_item == "ip":
				url = self.URL_BASE + self.type_item + "-address/report"
			else:
				url = self.URL_BASE + self.type_item + "/report"
			# self.logger.debug(url)
			if self.type_item == "file":
				attr = {"apikey": self.apikey, "resource": item}
			else:
				attr = {"apikey": self.apikey, self.type_item: item}
			# self.logger.debug(attr)
			res = requests.get(url, params=attr)
			self.logger.debug(res.text)
			return res
		except Exception as e:
			self.logger.warning("Something wrong %s", e)

	def send_item(self, item):
		try:
			url = self.URL_BASE + self.type_item + "/scan"
			attr = {"apikey": self.apikey, self.type_item: item}
			self.logger.debug(url)
			self.logger.debug(attr)
			if self.type_item == "file":
				files = {"file": open(item, 'rb')}
				res = requests.post(url, params=attr, files=files)
			else:
				res = requests.post(url, data=attr)
			self.logger.debug(res.text)
			if res.status_code == self.HTTP_OK:
				resmap = json.loads(res.text)
				self.logger.debug("sent: %s, %s", item, resmap["verbose_msg"])
			else:
				self.logger.warning("sent: %s, HTTP: %d", item, res.status_code)
			
			self.logger.info("Wait 60 seconds for retrieving item")
			time.sleep(60)
			if self.type_item == "file":
				self.submit_item(resmap["sha256"])
			else:
				self.submit_item(item)
		except Exception as e:
			self.logger.warning("Something wrong in send_item: %s", e)

	def submit_item(self, line):
		try:
			if self.db.virustotal.find({self.type_item: line}).count() == 0:
				self.logger.debug("%s is unknown by DB", line)
				res = self.retrieve_report(line)

				if res.status_code == self.HTTP_OK:
					resmap = json.loads(res.text)
					self.logger.debug(resmap)
					if resmap["response_code"] == 1:
						self.logger.info("Report of %s has been retrieved with %d positives", line, resmap["positives"])
						CurrentTimestamp = int(time.time())
						self.db.virustotal.insert({"timestamp": CurrentTimestamp, self.type_item: line, "positives": resmap["positives"], "engines": []})
						for engine in resmap["scans"]:
							self.db.virustotal.update({self.type_item: line}, {"$push": {"engines": {"engine": engine, "result": resmap["scans"][engine]["result"]}}})
						if resmap["positives"] > 0:
							self.logger.warning("%s is potentally malicious with %d positives", line, resmap["positives"])
							# return True
						else:
							self.logger.warning("%s has no positives", line)
							# return False
					if resmap["response_code"] == 0:
						self.logger.warning("response code is %d", resmap["response_code"])
						if self.type_item != "file":
							self.send_item(line)
						# else:
							# return False

					if resmap["response_code"] == -2:
						self.logger.warning("%s is still in analysis in VT, wait 30s more", line)
						time.sleep(30)
				if self.is_public_api:
					self.logger.info("Wait %d seconds for the next item", self.PUBLIC_API_SLEEP_TIME)
					time.sleep(self.PUBLIC_API_SLEEP_TIME)
			else:
				self.logger.debug("%s is already in DB", line)
				if self.db.virustotal.find({"$and": [{self.type_item: line}, {"positives": {"$gt": 0}}]}).count() != 0:
					self.logger.warning("%s is potentally malicious with %d positives", line)
					# return True
				else:
					self.logger.warning("%s has no positives", line)
					# return False

		except Exception as e:
			self.logger.warning(e)