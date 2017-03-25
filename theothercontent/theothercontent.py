#!/usr/bin/env python
# -*- coding: utf-8 -*-

# standard libs
import csv
import json
import sys
import time
from urllib.parse import urlparse, urljoin, parse_qs
import pickle
import requests

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

def downloadImage(url, path):
    #image = 
    #path = 
    r = requests.get(url)
    if r.status_code == 200:
        with open(path, 'wb') as i:
            for chunk in r:
                i.write(chunk)

def _defineSel(selector):
    return [s.strip() for s in selector.split('!') if s != '']

def _getFinalURL(url):
    if url.startswith('//'):
        url = 'http:{}'.format(url)
    res = requests.get(url)
    if res.status_code == 200:
        return res.url
    else:
        return url


def getArticleData(articles_pkg):
    contents = articles_pkg['contents_selector']
    articles = articles_pkg['articles']

    hlSel = _defineSel(articles_pkg['content_hl'])
    imgSel = _defineSel(articles_pkg['content_img'])
    linkSel = _defineSel(articles_pkg['content_link'])
    provider = articles_pkg['farm']
    source = articles_pkg['site']
    
    output = []
    contentDriver = SessionManager()

    for article in articles:
        contentDriver.driver.get(article)
        soup = contentDriver.requestParsed()
        content_soup = soup.select(contents)
        if content_soup != []:
            try:
                for c in content_soup:

                    hl = c.attrs[hlSel[0]] if len(hlSel) < 2 else c.select(hlSel[0])[0].attrs[hlSel[1]]
                    ln = c.attrs[linkSel[0]] if len(linkSel) < 2 else c.select(linkSel[0])[0].attrs[linkSel[1]]
                    img = c.attrs[imgSel[0]] if len(imgSel) < 2 else c.select(imgSel[0])[0].attrs[imgSel[1]]

                    if 'background' in img:
                        img = parse_qs(urlparse(img[img.find("(")+1:img.find(")")]).query)['url'][0] # hack to extract revcontent img urls
                    if 'trends.revcontent' in ln:
                        ln = _getFinalURL(ln)


                    output.append({'headline':hl, 'link':ln, 'img':img, "provider":provider, "source":source})
            except Exception as e:
                print("Could not get contents of these native ads on {0} - {1}: {2}".format(source, article, e))
        else:
            print("content soup was empty for {} - {}".format(source, article))
    return output

def clearDupes(content):
    '''Given some content that we received, we want to remove dupes
    
    Dupes will be defined as both having the same content from the same site
    For now we'll keep same content, different site.
    
    Arguments:
        content {List} -- A list of dictionaries describing a site and the content returned from it
    '''

    for c in content:
        print('removing dupes')
        # remove dupes

    return content

    
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

    ap.close()

    # join articles to target output so we have a single package to send for content
    for articles in articleResults:
        for target in targets:
            if target['site'] == list(articles.keys())[0]:
                target['articles'] = articles[target['site']]



    ctp = Pool(WORKERS_MAX)
    # now use workers to grab content data from each article
    contentResults = ctp.map(getArticleData, targets)

    # now that we have everything, let's remove duplicates before storage
    #forStorage = clearDupes(contentResults)

    # and store it


    print(contentResults)
    with open('./notes/contentResults_run2.pickle', 'wb') as cr:
        pickle.dump(contentResults, cr)
