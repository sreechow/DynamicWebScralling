# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json

#not using ??
class WebCrawlPipeline:
    
    def open_spider(self, spider):
        spidername = str(spider.name) + '.json'
        self.file = open(spidername, 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        print( "++++++++++++++++++++++++++++++++++++++++++++ =====>")
        #json.dumps(item, indent=4)
        #self.file.write(line) 
        #print(item)
        
        line = ''
        try:
            line = item.toJSON()
        except:
            line = item.__dict__
        #val = json.dumps(line)
        self.file.write(str(line)) 
        
    
        return item
