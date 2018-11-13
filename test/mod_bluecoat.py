#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from argparse import ArgumentParser
from bs4 import BeautifulSoup
import logging
import json
import requests
import sys
import urllib.request
import time
import os
import subprocess
from PIL import Image
from modules.mod_captcha_breaker import resolve
try:
	from selenium import webdriver
except:
	subprocess.call(["sudo", "python3.6", "-m", "pip", "install", "selenium"])
	# wget https://github.com/mozilla/geckodriver/releases/download/v0.18.0/geckodriver-v0.18.0-linux64.tar.gz
	# tar -xvzf geckodriver-v0.18.0-linux64.tar.gz
	# rm geckodriver-v0.18.0-linux64.tar.gz
	# chmod +x geckodriver
	# sudo cp geckodriver /usr/local/bin/

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('logs/logs_bc.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(funcName)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
scrlog = logging.StreamHandler()
scrlog.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
logger.addHandler(scrlog)

class SiteReview(object):
	def __init__(self):
		self.baseurl = "http://sitereview.bluecoat.com/rest/categorization"
		self.useragent = {"User-Agent": "Mozilla/5.0"}
		self.spleep_time = 2

	def sele_captcher(self, line):
		try:
			profile = webdriver.FirefoxProfile()
			driver = webdriver.Firefox(profile)
			driver.get("https://sitereview.bluecoat.com")
			element = driver.find_element_by_class_name('captcha')
			location = element.location
			size = element.size
			driver.save_screenshot('screenshot.png')
			im = Image.open('screenshot.png')
			left = location['x']
			top = location['y']
			right = location['x'] + size['width']
			bottom = location['y'] + size['height']
			im = im.crop((left, top, right, bottom))
			im.save('captcha.png')
			captcha_text = resolve("captcha.png")
			logger.debug(captcha_text)
			inputCaptcha = driver.find_element_by_name("captcha")
			inputCaptcha.send_keys(captcha_text)
			inputUrl = driver.find_element_by_id("search")
			inputUrl.send_keys(line)
			inputUrl.submit()
			os.remove("./captcha.png")
			os.remove("./screenshot.png")
			driver.close()
			# return driver

		# try:
		# 	WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'header_block')))
		# 	try:
		# 		logger.debug("Old " + driver.find_element_by_class_name("timestampContent").text)
		# 		db.pastes.update({"hash": hash_cred}, {"$set" : {"account": "true", line[0]: "old", line[0] + " password age": driver.find_element_by_class_name("timestampContent").text}})
		# 	except NoSuchElementException:
		# 		# logger.debug("no luck")
		# 		db.pastes.update({"hash": hash_cred}, {"$set" : {line[0]: "false"}})
		# except Exception as e:
		# 	# logger.debug(e)
		# 	if line[4] in driver.current_url:
		# 		logger.debug(cred["email"] + ":" + cred["password"] + " locked")
		# 		db.pastes.update({"hash": hash_cred}, {"$set" : {"account": "true", line[0]: "locked"}})
		# 	else:
		# 		if "mobileprotection" in driver.current_url:
		# 			logger.debug(cred["email"] + ":" + cred["password"] + " locked")
		# 			db.pastes.update({"hash": hash_cred}, {"$set" : {"account": "true", line[0]: "locked"}})
		# 		else:
		# 			logger.debug(cred["email"] + ":" + cred["password"] + " WORKIIIING")
		# 			db.pastes.update({"hash": hash_cred}, {"$set" : {"account": "true", line[0]: "true"}})


		except Exception as e:
			logger.debug(e)

	def sitereview(self, filename):
		urls = open(filename, 'rb')
		logger.debug("%s opened", filename)

		try:
			for line in urls:
				line = line.decode("utf-8")[:-1]
				payload = {"url": line}
				self.req = requests.post(self.baseurl, headers=self.useragent, data=payload)
				time.sleep(10)
				ObjJson = json.loads(self.req.content.decode("UTF-8"))
				if "captcha" not in ObjJson["errorType"]:
					category = ObjJson["categorization"].split(">")[1].split("<")[0]
					logger.info("URL: %s Category: %s", ObjJson["url"], category)
				else:
					self.req = self.sele_captcher(line)
					ObjJson = json.loads(self.req.content.decode("UTF-8"))
					category = ObjJson["categorization"].split(">")[1].split("<")[0]
					logger.info("URL: %s Category: %s", ObjJson["url"], category)
					# logger.debug("captcha %s", captcha_text)
					# self.req = self.sele_captcher(line, captcha_text)
					# ObjJson = json.loads(self.req.content.decode("UTF-8"))
					# category = ObjJson["categorization"].split(">")[1].split("<")[0]
					# logger.info("URL: %s Category: %s", ObjJson["url"], category)
					# logger.info("Wait %d seconds for the next item", self.spleep_time)
					time.sleep(self.spleep_time)
					
		except Exception as e:
			logger.warning("Something wrong %s", e)