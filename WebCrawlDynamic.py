import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor  
from scrapy.item import Item, Field
from scrapy.spiders import CrawlSpider, Rule
from scrapy.crawler import CrawlerProcess
import json
import dateutil.parser as dtparser
import datetime as dt
import os
from os.path import dirname
import configparser
import pandas as pd 
import csv

from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging


#In this example Collect the data and organise to save to Json file
class BCItems(Item):
    url = Field()
    publishedDate = Field()
    title = Field()
    content = Field()


class WebCrawlDynamic(CrawlSpider):
    name = 'WebCrawlDynamic'

    #create a json file with date at project directory to save the data
    filename = 'Data_' + dt.datetime.today().strftime('%y%m%d') + '.json'
    dirpath = dirname(dirname(dirname(os.path.realpath(__file__))))
    filename = "file:///" + os.path.join(dirpath, filename)

    #if any settings required to customise for this file to override scrapy settings

    #defineing data to export as Json format
    custom_settings = {
        'FEED_URI': filename,
        'FEED_FORMAT': 'json',
        'FEED_EXPORTERS': {
            'json': 'scrapy.exporters.JsonItemExporter',
        },
        'FEED_EXPORT_ENCODING': 'utf-8',
    }
  
    # import CSV using pandas to get the list of urls to crawl dynamically
    csvfile = os.path.join(dirpath, 'Monitoring_Urls.csv')
    df = pd.read_csv(csvfile, error_bad_lines=False, keep_default_na=False, encoding='ISO-8859-1')
    lstUrls = df['Urls'].tolist()
    lstAllowedDomains = df['AllowDomains'].tolist()
    lstExcludeUrls = df['DenyDomains']
    lstDenyUrls = []
    for dUrls in lstDenyUrls:
        lstDenyUrls.extend(dUrls.split(','))
    
    lstDenyUrls = list(filter(None, lstDenyUrls))

    start_urls = lstUrls

    rules = (
        # Extract link from this path only
        # <div class="articleBody">
        Rule(

            LxmlLinkExtractor(
                allow_domains = lstAllowedDomains,
                deny = lstDenyUrls
                ),
            callback='parse'
        ),

        # link should match this pattern and create new requests
        Rule(
            LxmlLinkExtractor(
                allow = lstAllowedDomains, 
                deny = lstDenyUrls
                ),

            callback = 'Parse_data'
        ),
    )

    def Parse_data(self, response):
        bcitem = BCItems()
        try:
            # try to collect when the article is published
            publishDate = ""
            pdscript = response.xpath(
                '//script[@type="application/ld+json"]/text()').extract()
            for dateScript in pdscript:
                val = json.loads(dateScript)
                if val["datePublished"] != "":
                    publishDate = val["datePublished"]
                    break

            if len(publishDate) == 0:
                publishDate = response.xpath(
                "//span[@class='article-byline']/span[@class='text-nowrap']/text()").extract()

            #if not able capture the published date of the article, default will be scrap date
            if len(publishDate) == 0:
                publishDate = dt.datetime.today()

            #capturing the content

            # case1: majoritiy will have 'p' tag for the palin text
            pscript = response.xpath("//p/text()").extract()
            content = ' '.join(pscript)

            # case2: let's try to use one more general xpath to extract text
            script = response.xpath(
                "//div[@class='articleBody']/p/text()").extract()
            script = ' '.join(script)

            content = content + script

            # case3: 
            # case4: can try with few other xpaths or css strings

            # Let's say want to collect specific link data from the response as so far collecting 
            # the data from specific xpaths or cssstrings

            #here collecting all the links starts with 'CVE_'

            cveData = response.xpath("//*[contains(text(), 'CVE-')]/text()").extract()
            if len(cveData) > 0:
                cveContent = ' '.join(list(dict.fromkeys(cveData)))
                content = content + ' CVES text ' + cveContent #combine with content

              
            #next item to collect is title, which will mostly common to use 'title' tag  
            title = response.xpath("//title/text()").extract()

            #url is straight farward from response

            # If still content is empty then no point to collect the data
           
            if content:
                bcitem['url'] = response.url
                bcitem['publishedDate'] = publishDate  # change format
                bcitem['content'] = content
                bcitem['title'] = ' '.join(title)
                yield bcitem

        except Exception as ex:
            print(ex)
            #log the error
