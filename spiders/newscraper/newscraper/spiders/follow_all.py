
import scrapy
from bs4 import BeautifulSoup
import yake
# from bs4 import BeautifulSoup
import re
from dateutil  import parser

kw_extractor = yake.KeywordExtractor()


class FollowAllSpider(scrapy.Spider):
    name = 'follow_all'
    allowed_domains = ['theprint.in','indianexpress.com','ndtv.com','timesofindia.indiatimes.com','indiatoday.in','thehindu.com','scroll.in','hindustantimes.com','telegraphindia.com','timesnownews.com']
    start_urls = ['https://theprint.in/','https://indianexpress.com/','https://www.ndtv.com/','https://timesofindia.indiatimes.com/','https://www.indiatoday.in/','https://www.thehindu.com/','https://scroll.in/','https://www.hindustantimes.com/','https://www.telegraphindia.com/','https://www.timesnownews.com/']

    def __init__(self):
        self.links=[]

    def get_datetime_from_site(self,response):
        # if("theprint.in" in response.url):
        #     date=response.css()
        soup=BeautifulSoup(response.text,'html.parser')
        
        if "theprint.in" in response.url:
            date_str=soup.find_all("span",class_="update_date")[0].get_text()
            
            return parser.parse()

        else:
            return None
    
    def getting_links_from_site(self,response):
        reg_links=[]
        URL_REG=r"(https?:\/\/(www\.)?([-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b)([-a-zA-Z0-9()@:%_\+.~#?&//=]*))"
        reg_links=re.findall(URL_REG,response.text)
        links=[]
        css_links=response.css('a::attr(href)')
        for link in css_links:
            links.append(link.extract())
        for link in reg_links:
            if link[0] in links:
                continue
            links.append(link[0])
        return links

    def parse(self, response):
        self.links.append(response.url)
        soup = BeautifulSoup(response.text,'html.parser')
        try:
            text=soup.get_text().strip()
            title=soup.find('title').get_text()
        except AttributeError:
            return
            
        keywords_with_weights = kw_extractor.extract_keywords(text)
        keywords=[]

        for key in keywords_with_weights:
            keywords.append(key[0].lower())
        self.get_datetime_from_site(response)
        images=response.css('img')
        images_with_keys=[]
        for i in images:
            try:
                img={
                    "link":i.xpath("@src").extract()[0],
                    "alt":[],
                    "title":[]
                }
                # if  i.xpath("@alt").extract():
                #     img['alt']=list(list(zip(*kw_extractor.extract_keywords(i.xpath("@alt").extract()[0])))[0])
                # if  i.xpath("@title").extract():
                #     img['title']=list(list(zip(*kw_extractor.extract_keywords(i.xpath("@title").extract()[0])))[0])
                URL_REG=r"(https?:\/\/(www\.)?([-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b)([-a-zA-Z0-9()@:%_\+.~#?&//=]*))"
                if not re.search(URL_REG,i.xpath("@src").extract()[0]):
                    continue
                if  i.xpath("@alt").extract():
                    img['alt']=i.xpath("@alt").extract()[0]
                if  i.xpath("@title").extract():
                    img['title']=i.xpath("@title").extract()[0]
                
                if img['alt'] or img['title']:
                    images_with_keys.append(img)
            except IndexError:
                continue
            except AttributeError:
                return
        yield {
                'url':response.url,
                'keywords':keywords,
                'title':title,
                'images':images_with_keys
                }

        links=self.getting_links_from_site(response)
        for link in links:
            try:
                yield response.follow(link, self.parse,headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}) 
            except ValueError:
                continue
            except AttributeError:
                continue