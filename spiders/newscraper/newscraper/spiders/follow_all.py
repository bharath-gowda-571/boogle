
from datetime import date
import scrapy
from bs4 import BeautifulSoup
import yake
# from bs4 import BeautifulSoup
import re
from dateutil  import parser

kw_extractor = yake.KeywordExtractor()


class FollowAllSpider(scrapy.Spider):
    name = 'follow_all'
    # allowed_domains=['timesnownews.com']
    # start_urls=['https://www.timesnownews.com/']
    allowed_domains = ['theprint.in','indianexpress.com','ndtv.com','timesofindia.indiatimes.com','indiatoday.in','thehindu.com','scroll.in','hindustantimes.com','telegraphindia.com','timesnownews.com',"sportstar.thehindu.com"]
    start_urls = ['https://theprint.in/','https://indianexpress.com/','https://www.ndtv.com/','https://timesofindia.indiatimes.com/','https://www.indiatoday.in/','https://www.thehindu.com/','https://scroll.in/','https://www.hindustantimes.com/','https://www.telegraphindia.com/','https://www.timesnownews.com/','https://sportstar.thehindu.com/']

    def __init__(self):
        self.links=[]

    def get_datetime_from_site(self,response):
        
        soup=BeautifulSoup(response.text,'html.parser')
        date_str=""
        try:
            if "theprint.in" in response.url:
                date_str=soup.find_all("span",class_="update_date")[0].get_text()
                # return parser.parse(date_str)
            elif "indianexpress.com" in response.url:
                date_str=soup.find_all('span',{'itemprop':'dateModified'})[0].get_text().replace("Updated:","")
                # return parser.parse(date_str)
            elif "ndtv.com" in response.url:
                date_str=soup.find_all('span',{'itemprop':'dateModified'})[0].get_text().replace("Updated:","")
                # return parser.parse(date_str)
            
            elif "timesofindia.indiatimes.com" in response.url:
                date_str=soup.find_all('div',class_="yYIu- byline")[0].find("span").get_text().replace("Updated:","")
                # return parser.parse(date_str)
            elif 'indiatoday.in' in response.url:
                date_str=soup.find_all("span",class_="update-data")[0].get_text().replace("UPDATED:","")
                # return parser.parse(date_str)
            elif 'sportstar.thehindu.com' in response.url:
                date_str=" ".join(soup.find_all("span",class_="home-content-date")[0].get_text().split(" ")[1:])
                # return parser.parse(date_str)
            elif 'thehindu.com' in response.url:
                date_str=soup.find_all("div",class_="update-time")[0].get_text().replace("Updated:","")
                # return parser.parse(date_str)
            elif 'scroll.in' in response.url:
                date_str=soup.find_all("time",class_="article-published-time")[0]['datetime']
                # return parser.parse(date_str)
            elif 'hindustantimes.com' in response.url:
                
                    date_str=soup.find_all("div",class_="dateTime")[0].get_text()
                    # return parser.parse(date_str)
                    if "Published" in date_str:
                        date_str=date_str.replace("Published on","")
                    elif "Updated" in date_str:
                        date_str=date_str.replace("Updated on","")
                    

            elif 'telegraphindia.com' in response.url:
                date_str=soup.find_all("div",class_="fs-12 float-left")[0].get_text().split("|")[-1].replace("Published","")
                # return parser.parse(date_str)
            elif 'timesnownews.com' in response.url:
                date_str=soup.find_all("time")[0]['datetime']
                # return parser.parse(date_str)
            else:
                return None
        except IndexError:
            return None
        except Exception as e: 
            print(str(e))
            return None
        
        return parser.parse(date_str)

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
        datetime=self.get_datetime_from_site(response)
        if datetime:
            datetime=datetime.replace(tzinfo=None)
        images=response.css('img')
        just_image_links=[]
        images_with_keys=[]
        for i in images:
            try:
                link=i.xpath("@src").extract()[0]
                if link in just_image_links:
                    continue
                
                img={
                    "link":link,
                    "alt":"",
                    "title":""
                }
                URL_REG=r"(https?:\/\/(www\.)?([-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b)([-a-zA-Z0-9()@:%_\+.~#?&//=]*))"
                if not re.search(URL_REG,i.xpath("@src").extract()[0]):
                    continue
                if  i.xpath("@alt").extract():
                    img['alt']=i.xpath("@alt").extract()[0].lower()
                if  i.xpath("@title").extract():
                    img['title']=i.xpath("@title").extract()[0].lower()
                
                if img['alt'] or img['title']:
                    images_with_keys.append(img)
                    just_image_links.append(link)
            except IndexError:
                continue
            except AttributeError:
                return
        yield {
                'url':response.url,
                'datetime':str(datetime),
                'keywords':keywords,
                'title':title,
                'images':images_with_keys
                }

        links=self.getting_links_from_site(response)
        for link in links:
            if link.endswith(".png") or link.endswith(".jpg") or link.endswith(".jpeg"):
                continue
            try:
                yield response.follow(link, self.parse,headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}) 
            except ValueError:
                continue
            except AttributeError:
                continue