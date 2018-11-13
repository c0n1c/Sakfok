#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib.request
from bs4 import BeautifulSoup
import sys
import subprocess
from urllib.parse import urlparse
import zlib
import os
import gzip
import zipfile
import socket
import datetime
# subprocess.call(["sudo", "python3.6", "-m", "pip", "install", "lxml"])

headers = {
			"User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:36.0) Gecko/20100101 Firefox/36.0",
			"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
			"Accept-Language": "en-US,en;q=0.5",
			"Accept-Encoding": "gzip, deflate"
		}

allowed_extensions = ('pdf', 'exe', 'hta', 'html', 'jpeg', 'txt', 'zip', 'docx', 'doc', 'vbs', 'lnk', 'c', 'jpg', 'php', 'pem', 'py', 'png', 'gif',
					'xlb', 'pl', 'rtf', 'ps1', 'dll', 'xlsm', 'docm', 'sh')

today = datetime.datetime.now().strftime("%Y%m%d")

class WebCrawler(object):
	def __init__(self, db=None, logger=None):
		self.db = db
		self.logger = logger
		self.rootDir = "Data"

	def downloader(self, site, path):
		try:
			urllib.request.urlretrieve(site, path)
		except Exception as e:
			self.logger.warning(e)
			pass

	def crawler(self, site):
			page = set()
			self.logger.debug("crawling %s", site)
			s,n,p,pa,q,f = urlparse(site)
			href_exclude = ('?C=N;O=D',
							'?C=M;O=A',
							'?C=S;O=A',
							'?C=D;O=A',
							'.',
							'..',
							'.DS_Store',
							'?ND',
							'?MA',
							'?SA',
							'?DA')

			try:
				conn = urllib.request.Request(site, None, headers)
				raw = urllib.request.urlopen(conn, timeout=20)
				if raw.info().get('Content-Encoding') == None:
					bsObj = BeautifulSoup(raw.read(), "lxml")
				if raw.info().get('Content-Encoding') == "gzip":
					decoded = zlib.decompress(raw.read(), 16+zlib.MAX_WBITS)
					bsObj = BeautifulSoup(decoded, "lxml")
				for links in bsObj.findAll('a', href=True):
					if links.attrs['href'] not in href_exclude:
						self.logger.debug(links.attrs['href'].split(".")[-1])
						if links.attrs['href'].split(".")[-1].lower() not in allowed_extensions:
							page.add(links.attrs['href'])
							self.crawler(s + "://" + n + p + links.attrs['href'] + "/")
						else:
							self.logger.info("Download file: %s", links.attrs['href'])
							self.downloader(site + links.attrs['href'].replace(' ', '%20'), "sources/files/" + links.attrs['href'])
							if links.attrs['href'].split(".")[-1] == "zip":
								with zipfile.ZipFile("sources/files/" + links.attrs['href'], "r") as z:
									z.extractall("sources/files/")
									os.remove("sources/files/" + links.attrs['href'])
							# Archive malwares
							self.logger.info('%s is put in archive', links.attrs['href'])
							today = datetime.datetime.now().strftime("%Y%m%d")
							if not os.path.exists("malwares/" + today):
								os.makedirs("malwares/" + today)
							subprocess.call(["zip", "--password", "infected", "-rj", "./malwares/" + today + "/" + site.split('//')[1].split('/')[0] + ".zip", "sources/files/" + links.attrs['href'][1:]])
							os.remove("sources/files/" + links.attrs['href'])

			except Exception as e:
				self.logger.warning(e)
				pass

	def get_index_of(self, site):
		s,n,p,pa,q,f = urlparse(site)
		test_path = 1

		try:
			self.logger.debug("path: %s", p)
			for char in p:
				self.logger.debug("test char: %s", char)
				if char == '/':
					if "." not in p.split('/')[test_path]:
						self.logger.debug("test dir: %s with test_path= %d", '/'.join(p.split('/')[:test_path]) + "/", test_path)
						new_url = (s + "://" + n + '/'.join(p.split('/')[:test_path]) + "/")
						self.logger.debug("new_url: %s", new_url)
						conn = urllib.request.Request(new_url, None, headers)
						raw = urllib.request.urlopen(conn, timeout=20)
						if raw.info().get('Content-Encoding') == None:
							bsObj = BeautifulSoup(raw.read(), "lxml")
						if raw.info().get('Content-Encoding') == "gzip":
							decoded = zlib.decompress(raw.read(), 16+zlib.MAX_WBITS)
							bsObj = BeautifulSoup(decoded, "lxml")
						# self.logger.debug(bsObj)
						if bsObj.find('title') != None:
							form = bsObj.find('title').getText()
							self.logger.debug(bsObj.find('title').getText())
							if 'Index of' in form:
								self.logger.debug("Index Of found")
								self.crawler(new_url)
							else:
								self.logger.debug("no Index Of")
						else:
							self.logger.debug("no Title")
						test_path += 1
		except Exception as e:
			self.logger.warning("Error: %s with %s", e, new_url)
			pass

	# def get_kit(self, url):
	# 	headers = {
	# 		"User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:36.0) Gecko/20100101 Firefox/36.0",
	# 		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
	# 		"Accept-Language": "en-US,en;q=0.5",
	# 		"Accept-Encoding": "gzip, deflate"
	# 	}
	# 	socket.setdefaulttimeout(5)
	# 	page = set()
	# 	dirList = []
	# 	extensions = ['.zip']#, '.7z', '.rar', '.xz', '.gz']
	# 	test_char = 0
	# 	s,n,p,pa,q,f = urlparse(url)

	# 	try:
	# 		for char in p:
	# 			if char == '/' or char == '.':
	# 				new_url = (n + p[:test_char])
	# 				for extension in extensions:
	# 					try:
	# 						if not os.path.exists(self.rootDir + '/phishing/' + today + "/" + n):
	# 							for dirName, subdirList, fileList in os.walk(self.rootDir + '/phishing/' + today):
	# 								dirName = dirName.rsplit("/", 1)[1]
	# 								dirList.append(dirName)
	# 								if n not in dirList:
	# 									os.makedirs(self.rootDir + '/phishing/' + today + "/" + n)
	# 						urllib.request.urlretrieve('http://' + new_url + extension, self.rootDir + '/phishing/' + today + "/" + n + '/' + new_url.rsplit('/', 1)[1] + extension)
	# 						try:
	# 							with zipfile.ZipFile(self.rootDir + '/phishing/' + today + "/" + n + '/' + new_url.rsplit('/', 1)[1] + extension, "r") as z:
	# 								z.extractall(self.rootDir + '/phishing/' + today + "/" + n + '/')
	# 								self.db.phishing.insert({"kit_name": new_url.rsplit('/', 1)[1] + extension, "kit_presence": "true", "frauder_checked": "false"})
	# 						except zipfile.BadZipFile as i:
	# 							os.remove(self.rootDir + '/phishing/' + today + "/" + n + '/' + new_url.rsplit('/', 1)[1] + extension)
	# 							self.logger.debug(i)
	# 							pass
	# 					except Exception as e:
	# 						self.logger.debug(e)
	# 						pass
	# 				self.get_index_of('http://' + new_url)
	# 				test_char += 1
	# 			else:
	# 				test_char += 1
	# 		if not os.listdir(self.rootDir + '/phishing/' + today + "/" + n):
	# 			os.rmdir(self.rootDir + '/phishing/' + today + "/" + n)
	# 			self.db.phishing.insert({"kit_presence": "false"})
	# 		# return email frauder
	# 	except Exception as e:
	# 		self.logger.debug(e)
	# 		pass