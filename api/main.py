from typing import ItemsView, List
from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import time

class Site(BaseModel):
    url:str
    keywords:List[str]
    title:str

while True:
    try:
        conn=psycopg2.connect(host='localhost',database="website_keyword",user='postgres',password="one1000one",cursor_factory=RealDictCursor)
        cursor=conn.cursor()
        print("Connection Succesfull")
        break
    except Exception as err:
        print(str(err))
        time.sleep(2)

app = FastAPI()


@app.post("/add_url/")
async def add_site(site:Site):
    print(site)
    try:
        cursor.execute("""INSERT INTO url_keywords values (%s,%s,%s)""",(site.url,site.keywords,site.title),)
    except psycopg2.errors.InFailedSqlTransaction:
        cursor.execute("rollback")
        cursor.execute("""INSERT INTO url_keywords values (%s,%s,%s)""",(site.url,site.keywords,site.title),)
    except psycopg2.errors.UniqueViolation:
        # pass
        cursor.execute("rollback")
        cursor.execute("""UPDATE url_keywords SET keywords=%s, title=%s where url=%s""",(site.keywords,site.url,site.url))
    conn.commit()
    return site
