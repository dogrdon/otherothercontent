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
import hashlib
import datetime

# selenium for rendering
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# beautiful soup for parsing
from bs4 import BeautifulSoup

# multiprocessing for threads
from multiprocessing import Pool

# what else but mongo for safe keeping
from connection import MongoConn


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

def _getImgFormat(url, header):
    possible_formats = ['jpg', 'gif', 'png', 'jpeg']
    if header != '':
        if 'jpeg' in header:
            return '.jpg'
        elif 'png' in header:
            return '.png'
        elif 'gif' in header:
            return '.gif'
        else:
            print('content-type {} not recognized'.format(header))
    else:
        ext = url.split('.')[-1]
        if ext in possible_formats:
            return '.{}'.format(ext)
        else:
            print('could not find an extension for {}, have a look, for now leaving it without one.'.format(url))
            return ''        

def getArticleData(articles_pkg):
    contents = articles_pkg['contents_selector']
    articles = articles_pkg['articles']

    hlSel = _defineSel(articles_pkg['content_hl'])
    imgSel = _defineSel(articles_pkg['content_img'])
    linkSel = _defineSel(articles_pkg['content_link'])
    provider = articles_pkg['farm']
    source = articles_pkg['site']
    article_host = '{}_article'.format(urlparse(source).netloc)

    output = []
    contentDriver = SessionManager(host=article_host)

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
            continue
    return output

def clearDupes(content):
    '''Given some content that we received, we want to remove dupes
    
    Dupes will be defined as both having the same content from the same site
    For now we'll keep same content, different site.
    
    Arguments:
        content {List of lists} -- A list of lists of dictionaries describing a site and the content returned from it
    '''
    cleanContent = []
    for c in content:
        print('incoming dump of {} items'.format(str(len(c))))
        print('removing dupes')
        deduped = list({i['link']:i for i in c}.values())
        print('outgoing only {} items'.format(str(len(deduped))))

        cleanContent.append(deduped)

    return cleanContent

def downloadImages(content):
    '''Taking out cleaned content payload to download all the images locally
    
    For each entry that will go in our database, take the image url, make a hash of that (md5 is fine?)
    and then we'll download the image by that name and add that image id to the record and return the whole thing as a flatmapped list
    
    Arguments:
        content {List of lists} -- A list of lists of dictionaries describing a site and the content returned from it
    '''
    imagedContent = []
    for c in content:
        print("Attempting to download {} images".format(str(len(c))))
        for i in c:

            img_url = i['img']
            img_id = hashlib.sha1(img_url.encode('utf-8')).hexdigest()
            r = requests.get(img_url)
            img_format = _getImgFormat(img_url, r.headers.get('Content-Type', ''))
            path = './imgs/{}{}'.format(img_id, img_format)
            if r.status_code == 200:
                with open(path, 'wb') as imgbuffer:
                    for chunk in r:
                        imgbuffer.write(chunk)
                i['img_file'] = path

            else:
                print("count not download image for {}".format(img_url))
                i['img_file'] = ''

            
            imagedContent.append(i)

    return imagedContent

def finalizeRecords(records):
    finalRecords = []
    for r in records:
        # add date before we store
        r['date'] = datetime.datetime.utcnow()

        #get the final url for each link (if redirect)
        r['final_link'] = _getFinalURL(r['link'])
        finalRecords.append(r)
    return finalRecords

    
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
    WORKERS_MAX = 5
    targets = fetchSiteGuide(RESOURCES)
    MONGO = MongoConn('theothercontent', 'contents')

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
    forImaging = clearDupes(contentResults)

    # lets create a hash for each img location and use that as a filename for the image we'll store, and add the hash on the record
    withImages = downloadImages(contentResults)

    # finally wrap up with final details
    forStorage = finalizeRecords(withImages)

    print(forStorage)
    with open('./notes/contentResults_run5_clean.pickle', 'wb') as cr:
        pickle.dump(forStorage, cr)

    # and store it
    MONGO.save_records(forStorage)



