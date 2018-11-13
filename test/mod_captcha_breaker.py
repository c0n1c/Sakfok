#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess

try:
	import pytesseract
except:
	subprocess.call(["sudo", "python3.6", "-m", "pip", "install", "pytesseract"])
	import pytesseract

import sys
import argparse
try:
    import Image
except ImportError:
    from PIL import Image
from subprocess import check_output

def grab_image(url):
	pass

def resolve(path):
	check_output(['convert', path, '-resample', '600', path])
	return pytesseract.image_to_string(Image.open(path))