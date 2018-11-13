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
import datetime
import subprocess
from configparser import ConfigParser
import pymongo
import re
from urllib.parse import urlparse
from modules.mod_virustotal import VirusTotal
from modules.mod_lookingglass import LookingGlass
from modules.mod_web_crawler import WebCrawler
from modules.mod_cymon import Cymon
from modules.mod_fraudguard import Fraudguard
from modules.mod_whois import Whois
from modules.mod_riskdiscovery import Riskdiscovery
from modules.mod_normshield import Normshield
from modules.mod_onyphe import Onyphe

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('logs_saxa.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(funcName)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
scrlog = logging.StreamHandler()
scrlog.setFormatter(logging.Formatter("[%(levelname)s] - (%(funcName)s) - %(message)s"))
logger.addHandler(scrlog)

# allowed_extensions = ('pdf', 'exe', 'hta', 'html', 'jpeg', 'txt', 'zip', 'docx', 'doc', 'vbs', 'lnk', 'c', 'jpg', 'php', 'pem', 'py', 'png', 'gif',
# 					'xlb', 'pl', 'rtf', 'ps1', 'dll', 'xlsm', 'docm', 'sh')

if (sys.version_info < (3, 0)):
	logger.warning("ERROR: Please, use Python3.X")
	sys.exit()

def read_config(option ,section='scheduler', filename='config.ini'):
	parser = ConfigParser()
	parser.read(filename)
	if parser.has_section(section):
		if parser.has_option(section, option):
			value = parser.get(section, option)
		else:
			raise Exception('{0} option not found in the {1} section'.format(option, section))
	else:
		raise Exception('{0} section not found in the {1} file'.format(section, filename))
	return value

def list_all_files(path):
	fileList = []
	dirPath = os.path.dirname(os.path.abspath(__file__)) + "/" + path + "/"

	for dirName, subdirList, file_list in os.walk(dirPath):
		for file in file_list:
			file_path = dirPath + file
			fileList.append(file_path)
	return fileList
	
def crawling(p, line):
	# Crawling/Downloading
	if '.' in '/'.join(p.split('/')[-1:]):
		logger.debug("Downloading %s", line)
		wc.downloader(line, "sources/files/" + '/'.join(p.split('/')[-1:]))
	wc.get_index_of(line)

def api(api_name):
	try:
		with open(os.getenv("HOME") + '/.' + api_name + '.api') as keyfile:
			logger.info('%s API key has been loaded', api_name)
			return keyfile.read().strip()
	except:
		logger.warning('[Error] Please put your %s API Key in file "$HOME/.%s.api"', api_name)
		sys.exit()

if __name__ == "__main__":

	# Check Dirs and files presence
	if not os.path.exists("malwares/"):
		os.makedirs("malwares/")
		logger.info('Malware Dir created')
	if not os.path.exists("sources/"):
		os.makedirs("sources/")
		logger.info('Dir sources created')
	if not os.path.exists("sources/URL.txt"):
		os.mknod("sources/URL.txt")
		logger.info('file URL created')
	if not os.path.exists("sources/IP.txt"):
		os.mknod("sources/IP.txt")
		logger.info('file IP created')
	if not os.path.exists("sources/hash.txt"):
		os.mknod("sources/hash.txt")
		logger.info('file Hash created')
	if not os.path.exists("sources/domain.txt"):
		os.mknod("sources/domain.txt")
		logger.info('file domain created')
	if not os.path.exists("sources/files"):
		os.makedirs("sources/files")
		logger.info('Dir files created')

	# Connect to DB
	try:
		mongohost = read_config('host', 'mongodb')
		mongoport = read_config('port', 'mongodb')
		dbname = read_config('database', 'mongodb')

		connection = pymongo.MongoClient(mongohost, int(mongoport), serverSelectionTimeoutMS=1)
		connection.server_info()
		db = connection[dbname]
		logger.info('Connected to MongoDB')
	except pymongo.errors.ServerSelectionTimeoutError as e:
		logger.warning("Mongod is not started. Tape \"sudo mongod --fork --logpath /var/log/mongodb.log\" in a terminal")
		if not os.path.exists("/data/db"):
			os.makedirs("/data/db")
			logger.info('database created')
		logger.warning("Error %s", e)
		sys.exit()

	# Init class
	# lg = LookingGlass(db, logger)
	wc = WebCrawler(db, logger)

	# vt_url = VirusTotal(db, logger)
	# vt_url.type_item = "url"
	# vt_url.apikey = api("virustotal")

	# Malicious URL
	urls = open("sources/URL.txt", 'rb')
	logger.debug("%s opened", "sources/URL.txt")

	for line in urls:
		line = line.decode("utf-8")[:-1]
		s,n,p,pa,q,f = urlparse(line)
		crawling(p, line)

		# Reputation
		# malicious = vt_url.submit_item(line)
		# if malicious == True:
		# 	logger.info('%s is potentially dangerous', line)
		# else:
		# 	logger.info('%s has to be checked manually', line)
		# 	lg.looking(line)

	open('sources/URL.txt', 'w').close()

	# test Domain
	# domains = open("sources/domain.txt", 'rb')
	# logger.debug("%s opened", "sources/domain.txt")

	# for line in domains:
	# 	line = line.decode("utf-8")[:-1]

	# # test IP
	# wh_ip = Whois(db, logger)
	# vt_ip = VirusTotal(db, logger)
	# vt_ip.type_item = "ip"
	# vt_ip.apikey = api("virustotal")
	# ips = open("sources/IP.txt", 'rb')
	# logger.debug("%s opened", "sources/IP.txt")

	# for line in ips:
	# 	line = line.decode("utf-8")[:-1]
	# 	wh_ip.submit_item(line)
	# 	vt_ip.submit_item(line)
	# 	wc.get_index_of(line, allowed_extensions)
	# open('sources/IP.txt', 'w').close()

	# # test file
	# vt_file = VirusTotal(db, logger)
	# vt_file.type_item = "file"
	# vt_file.apikey = api
	# hashes = open("sources/hash.txt", 'rb')
	# logger.debug("%s opened", "sources/hash.txt")

	# for line in hashes:
	# 	line = line.decode("utf-8")[:-1]
	# 	vt_file.submit_item(line)
	# open('sources/hash.txt', 'w').close()
	# file_list = list_all_files("sources/files")
	# if len(file_list) != 0:
	# 	for line in file_list:
	# 		logger.debug("%s opened", line)
	# 		BUF_SIZE = 65536
	# 		sha256 = hashlib.sha256()
	# 		with open(line, 'rb') as f:
	# 			while True:
	# 				data = f.read(BUF_SIZE)
	# 				if not data:
	# 					break
	# 				sha256.update(data)
	# 		logger.info('%s is hashed as %s', line, sha256.hexdigest())
	# 		malicious = vt_file.submit_item(sha256.hexdigest())
	# 		# http://www.malshare.com/
	# 		# https://metadefender.opswat.com
	# 		# https://virusshare.com
	# 		if malicious == True:
	# 			logger.info('%s is put in archive', line)
	# 			today = datetime.datetime.now().strftime("%Y%m%d")
	# 			subprocess.call(["zip", "--password", "infected", "-rj", "./malwares/" + today + ".zip", line])
	# 		else:
	# 			logger.info('%s will be submitted and do a manual analysis', line)
	# 			vt_file.send_item(line)
	# 		os.remove(line)

# -------------------------------------------------------------------------------------------------------------
		# if ':' in n:
		# 	n = n.split(':')[0]
		# add ip from url
		# regex_ip = re.compile(r'(?:\d{1,3}\.){3}\d{1,3}')
		# if regex_ip.search(n) != None:
		# 	with open('sources/IP.txt', 'a') as file:
		# 		file.write(n)
		# 		logger.info('%s added in IP.txt', n)
		# add domain name from url
		# n = line.split('/')[:3:]
		# n[1] = '//'
		# n = ''.join(n)
		# with open('sources/domain.txt', 'a') as file:
		# 	file.write(n)
		# 	logger.info('%s added in domain.txt', n)