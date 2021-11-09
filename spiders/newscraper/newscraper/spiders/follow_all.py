
import scrapy
from bs4 import BeautifulSoup
import yake
from bs4 import BeautifulSoup

kw_extractor = yake.KeywordExtractor()


class FollowAllSpider(scrapy.Spider):
    name = 'follow_all'
    allowed_domains = ['theprint.in','indianexpress.com','ndtv.com','timesofindia.indiatimes.com','indiatoday.in','thehindu.com','scroll.in','hindustantimes.com','telegraphindia.com','timesnownews.com']
    start_urls = ['https://theprint.in/','https://indianexpress.com/','https://www.ndtv.com/','https://timesofindia.indiatimes.com/','https://www.indiatoday.in/','https://www.thehindu.com/','https://scroll.in/','https://www.hindustantimes.com/','https://www.telegraphindia.com/','https://www.timesnownews.com/']

    def __init__(self):
        self.links=[]

    def parse(self, response):
        self.links.append(response.url)
        soup = BeautifulSoup(response.text,'html.parser')
        text=soup.get_text().strip()
        keywords_with_weights = kw_extractor.extract_keywords(text)
        keywords=[]
        for key in keywords_with_weights:
            keywords.append(key[0].lower())

        title=soup.find('title').get_text()

        for href in response.css('a::attr(href)'):
            try:
                yield response.follow(href, self.parse,headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}) 
            except ValueError:
                continue
        yield {
                'url':response.url,
                'keywords':keywords,
                'title':title
                }