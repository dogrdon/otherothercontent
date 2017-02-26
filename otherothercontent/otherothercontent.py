#!/usr/bin/env python
# -*- coding: utf-8 -*-

# standard libs
import csv
import sys
import time

# selenium for rendering
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# beautiful soup for parsing
from bs4 import BeautifulSoup

# multiprocessing for threads
from multiprocessing import Pool


def fetchSiteGuide(PATHTOSITEGUIDE):
    """Function which takes in the csv of sites and
       where their other content are and produces a 
       more traversable pyton dictionary for 
       extracting article details
    """
    fetched_sites = []
    with open(PATHTOSITEGUIDE, 'r') as f:
        rows = csv.DictReader(f)
        fields = rows.fieldnames
        for row in rows:
            entry = {f: row[f] for f in fields}
            fetched_sites.append(entry)

    return fetched_sites

def getArticles(target):
    articles = {}
    initialDriver = SessionManager()
    initialDriver.driver.get(target['site'])
    soup = initialDriver.requestParsed()
    articles[target['site']] = [i.attrs['href'] for i in soup.select(
        target['articles_selector'])[0:ARTICLES_MAX]]
    del initialDriver
    return articles

def getArticleData(article):
    hlSel = article['']
    imgSel = article['']
    linkSel = article['']
    pass

class SessionManager(object):
    """A class for managing Selenium Driver sessions.


    """

    def __init__(self,
                 userAgent="Mozilla/5.0 (Linux; U; Android 2.3.3; en-us; LG-LU3000 Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
                 dcap=dict(DesiredCapabilities.PHANTOMJS),
                 driver=None,
                 logPath="./logs/ghostdriver_{}.log"):
        super(SessionManager, self).__init__()
        self.userAgent = userAgent
        self.dcap = dcap
        self.logPath = logPath.format(str(int(time.time())))
        self.dcap['phantomjs.page.settings.userAgent'] = userAgent
        self.driver = webdriver.PhantomJS(
            desired_capabilities=self.dcap, service_log_path=self.logPath)

    def __del__(self):
        self.driver.quit()

    def requestParsed(self, html=None):
        """Function to input html and get out a BeautifulSoup Parser

        Provide the driver.page_source in your SessionManager to get
        back a parser to navigate the HTML returned from your request

        Keyword Arguments:
                html {[selenium webdriver page_source]} -- [html page source returned from selenium webdriver.page_source] (default: {driver.page_source})

        Returns:
                [class 'bs4.BeautifulSoup'] -- [html parsed by beautiful soup]
        """

        self.html = self.driver.page_source
        return BeautifulSoup(self.html, 'html.parser')



if __name__ == '__main__':

    RESOURCES = sys.argv[1]
    ARTICLES_MAX = 3
    WORKERS_MAX = 3
    targets = fetchSiteGuide(RESOURCES)


    p = Pool(WORKERS_MAX)
    results = p.map(getArticles, targets)

    print results
    
  

