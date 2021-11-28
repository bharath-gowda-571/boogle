from typing import ItemsView, List
from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from mangum import Mangum

class Image(BaseModel):
    link:str
    alt:str
    title:str

class Site(BaseModel):
    url:str
    keywords:List[str]
    title:str
    datetime:str
    images:List[Image]


while True:
    try:
        conn=psycopg2.connect(host='65.2.38.82',database="website_keyword",user='postgres',password="one1000one",cursor_factory=RealDictCursor)
        cursor=conn.cursor()
        print("Connection Succesfull")
        break
    
    except Exception as err:
        print(str(err))
        time.sleep(2)

app = FastAPI()


@app.post("/add_url/")
async def add_site(site:Site):
    # print(site)
    try:
        cursor.execute("""INSERT INTO url_keywords values (%s,%s,%s,%s)""",(site.url,site.keywords,site.title,site.datetime),)
    except psycopg2.errors.InFailedSqlTransaction:
        cursor.execute("rollback")
        cursor.execute("""INSERT INTO url_keywords values (%s,%s,%s,%s)""",(site.url,site.keywords,site.title,site.datetime),)
    except psycopg2.errors.UniqueViolation:
        cursor.execute("rollback")
        cursor.execute("""UPDATE url_keywords SET keywords=%s, title=%s,datetime=%s where url=%s""",(site.keywords,site.url,site.datetime,site.url))
    conn.commit()
    for image in site.images:
        try:
            try:
                cursor.execute("INSERT INTO images values (%s,%s,%s,%s)",(image.link,image.alt,image.title,site.url))
            except psycopg2.errors.InFailedSqlTransaction:
                cursor.execute("rollback")
                cursor.execute("INSERT INTO images values (%s,%s,%s,%s)",(image.link,image.alt,image.title,site.url))

        except psycopg2.errors.UniqueViolation:
            continue
    conn.commit()
    return site



handler=Mangum(app)