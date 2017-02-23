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


class SessionManager(object):
	"""A class for managing Selenium Driver sessions.

			
	"""
	def __init__(self, 
				 userAgent="Mozilla/5.0 (Linux; U; Android 2.3.3; en-us; LG-LU3000 Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
				 dcap=dict(DesiredCapabilities.PHANTOMJS),
				 driver=None,
				 logPath="./logs/ghostdriver.log"):
		super(SessionManager, self).__init__()
		self.userAgent = userAgent
		self.dcap = dcap
		self.logPath = logPath
		self.dcap['phantomjs.page.settings.userAgent'] = userAgent
		self.driver = webdriver.PhantomJS(desired_capabilities=self.dcap, service_log_path=self.logPath)
		

	@classmethod
	def requestParser(self, html=self.driver.page_source):
		"""Function to input html and get out a BeautifulSoup Parser
		
		Provide the driver.page_source in your SessionManager to get
		back a parser to navigate the HTML returned from your request
		
		Keyword Arguments:
			html {[type]} -- [description] (default: {driver.page_source})
		
		Returns:
			[type] -- [description]
		"""

		self.html = html
		return BeautifulSoup(html, 'html_parser')




if __name__ == '__main__':

	RESOURCES = sys.argv[1]
	ARTICLES_MAX = 3
	targets = fetch_sites(RESOURCES)
	
	initialDriver = SessionManager()

	for target in targets:
		# do the stuff to extract the things
		initialDriver.driver.get(target['site'])
		soup = initialDriver.requestParser()
		articles = [i.attrs['href'] for i in soup.select(target['articles_selector'])[0:ARTICLES_MAX]]

	articleDriver = SessionManager()
	
	for a in articles:
		pass
