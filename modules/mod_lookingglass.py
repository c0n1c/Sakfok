#!/usr/bin/python
# -*- coding: utf-8 -*-

try:
	from selenium import webdriver
except:
	subprocess.call(["pip3", "install", "selenium"])
	# wget https://github.com/mozilla/geckodriver/releases/download/v0.18.0/geckodriver-v0.18.0-linux64.tar.gz
	# tar -xvzf geckodriver-v0.18.0-linux64.tar.gz
	# rm geckodriver-v0.18.0-linux64.tar.gz
	# chmod +x geckodriver
	# sudo cp geckodriver /usr/local/bin/

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
import time
from configparser import ConfigParser
import pymongo
import logging
import os

class LookingGlass(object):
	def __init__(self, db, logger):
		self.db = db
		self.logger = logger

	def looking(self, item):
		try:
			if self.db.virustotal.find({"$and": [{"url": item}, {"manual_check": "false"}]}).count() == 0:
				driver = webdriver.Firefox()
				driver.get(item)
				CurrentTimestamp = int(time.time())
				self.db.virustotal.insert({"timestamp": CurrentTimestamp, "url": item, "manual_check": "true"})
				time.sleep(2)
				driver.close()
		except TimeoutException as e:
			self.logger.warning(e)
			driver.close()
			pass
		except NoSuchElementException as j:
			self.logger.warning(j)
			driver.close()
			pass
		except WebDriverException as k:
			self.logger.warning(k)
			driver.close()
			pass