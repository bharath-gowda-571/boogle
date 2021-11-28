# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import requests

class NewscraperPipeline:

    def process_item(self, item, spider):
        print(type(item))
        res=requests.post("https://b9s8vxlhv6.execute-api.ap-south-1.amazonaws.com/dev/add_url/",json=item)    
        return item
