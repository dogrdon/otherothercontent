#!/usr/bin/env python
# -*- coding: utf-8 -*-

# standard libs
import csv
import sys

# selenium for rendering
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# beautiful soup for parsing
from bs4 import BeautifulSoup

# multiprocessing for threads
from multiprocessing import Pool


def fetch_sites(PATHTOSITES):
	fetched_sites = []
	with open(PATHTOSITES, 'r') as f:
		rows = csv.DictReader(f)
		fields = rows.fieldnames
		for row in rows:
			entry = {f:row[f] for f in fields}
			fetched_sites.append(entry)

	return fetched_sites






if __name__ == '__main__':

	RESOURCES = sys.argv[1]
	USERAGENT_STRING = "Mozilla/5.0 (Linux; U; Android 2.3.3; en-us; LG-LU3000 Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"
	ARTICLES_MAX = 3
	dcap = dict(DesiredCapabilities.PHANTOMJS)
	dcap['phantomjs.page.settings.userAgent'] = USERAGENT_STRING
	driver = webdriver.PhantomJS(desired_capabilities=dcap, service_log_path="./logs/ghostdriver.log")

	targets = fetch_sites(RESOURCES)
	
	for target in targets:
		# do the stuff to extract the things
		driver.get(target['site'])
		soup = BeautifulSoup(driver.page_source, 'html_parser')
		articles = [i.attrs['href'] for i in soup.select(target['articles_selector'])[0:ARTICLES_MAX]]

	for a in articles:

		# extract.... design this better
