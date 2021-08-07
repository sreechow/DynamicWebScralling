import os
from scrapy.cmdline import execute

os.chdir(os.path.dirname(os.path.realpath(__file__)))

try:
    execute(
        [
            'scrapy',
            'crawl',
            'WebCrawl',

        ]
    )
except Exception as ex:
    print(ex)
except SystemExit as se:
   pass