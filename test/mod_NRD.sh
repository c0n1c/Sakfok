#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import requests

class NRD(object):
	def __init__(self, db, logger):
		self.HTTP_OK = 200
		self.logger = logger

	def downloader(self, site, path):
		try:
			urllib.request.urlretrieve(site, path)
		except Exception as e:
			self.logger.warning(e)
			pass

	def unzip(self):
		cookie = self.grab_cookie()


#!/bin/bash

TODAY=$(date --date='-2 day' +'%Y-%m-%d')
DESTDIR="./"
URL="https://whoisds.com/whois-database/newly-registered-domains/$TODAY.zip/nrd"
USERAGENT="XmeBot/1.0 (https://blog.rootshell.be/bot/)"
TEMPFILE=$(mktemp /tmp/wget_XXXXXX.zip)
LOGFILE=$(mktemp /tmp/wget_XXXXXX.log)
# CSVFILE="/opt/splunk/etc/apps/search/lookups/newdomains.csv"

# Check if the destination directory exists
[ -d "$DESTDIR" ] || mkdir -p "$DESTDIR"
# Ensure that the file does not exist already
[ -r "$DESTDIR/$TODAY.txt" ] && rm "$DESTDIR/$TODAY.txt"

wget -o $LOGFILE -O $TEMPFILE --user-agent="$USERAGENT" $URL
RC=$?
if [ "$RC" != "0" ]; then
	echo "[ERROR] Cannot fetch $URL"
	cat $LOGFILE
else
	unzip -d $DESTDIR $TEMPFILE >$LOGFILE 2>&1
	RC=$?
	if [ "$RC" != "0" ]; then
		echo "[ERROR] Cannot unzip $TEMPFILE"
		cat $LOGFILE
	# else
	# 	echo "newdomain" >$CSVFILE
	# 	cat "$DESTDIR/$TODAY.txt" >>$CSVFILE
	# 	rm $LOGFILE $TEMPFILE
	fi
fi

