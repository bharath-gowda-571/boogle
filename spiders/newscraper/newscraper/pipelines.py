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
        res=requests.post("http://localhost:8000/add_url/",json=item)
        # print(res.status_code)
        return item
