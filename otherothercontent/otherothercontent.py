#!/usr/bin/env python
# -*- coding: utf-8 -*-

# standard libs
import csv
import json
import sys
import time
from urlparse import urlparse, urljoin
import pickle

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

def checkArticleURL(site, link):
    if link.startswith(site):
        return link
    else:
        return urljoin(site,link)

def getArticles(target):
    ARTICLES_MAX = 3

    articles = {}
    site = target['site']
    host = urlparse(site).netloc
    articleDriver = SessionManager(host=host)
    articleDriver.driver.get(target['site'])
    soup = articleDriver.requestParsed()
    articles[site] = [checkArticleURL(site,i.attrs['href']) for i in soup.select(
        target['articles_selector'])[0:ARTICLES_MAX]]
    del articleDriver
    return articles

def getArticleData(articles_pkg):
    contents = articles_pkg['contents_selector']
    hlSel = articles_pkg['content_hl']
    imgSel = article_pkg['content_img']
    linkSel = article_pkg['content_link']
    articles = article_pkg['articles']
    output = []
    contentDriver = SessionManager()

    for article in articles:
        contentDriver.driver.get(article)
        soup = contentDriver.requestParsed()
        content_soup = soup.select(contents)
        '''get the rest'''
    
class SessionManager(object):
    """A class for managing Selenium Driver sessions.


    """

    def __init__(self,
                 userAgent="Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
                 dcap=dict(DesiredCapabilities.PHANTOMJS),
                 driver=None,
                 host='',
                 bwidth=1400,
                 bheight=1000,
                 logPath="./logs/ghostdriver_{0}_{1}.log"):
        super(SessionManager, self).__init__()
        self.userAgent = userAgent
        self.dcap = dcap
        self.logPath = logPath.format(host, str(int(time.time())))
        self.dcap['phantomjs.page.settings.userAgent'] = userAgent
        self.driver = webdriver.PhantomJS(
            desired_capabilities=self.dcap, service_log_path=self.logPath)
        self.driver.set_window_size(bwidth,bheight)

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
    WORKERS_MAX = 3
    targets = fetchSiteGuide(RESOURCES)

    #use workers to grab new articles
    ap = Pool(WORKERS_MAX)
    articleResults = ap.map(getArticles, targets)
    print articleResults
    with open('./notes/tmp_articles_sample.json', 'w') as out:
        json.dump(articleResults, out, indent=4)
    ap.close()

    #if something goes wrong, we don't want to have to do that again
    pickle.dumps(articleResulsts, open('.tmp_store/tmp_articles_store.p'))

    for articles in articleResults:
        for target in targets:
            if target['site'] == list(articles.keys())[0]:
                target['articles'] = articles[target['site']]


    ctp = Pool(WORKERS_MAX)
    contentResults = ctp.map(getContent, targets)

