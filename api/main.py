
from typing import ItemsView, List
from fastapi import FastAPI,HTTPException,status
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from starlette.responses import StreamingResponse
import yake
import datetime
from fastapi.middleware.cors import CORSMiddleware
from pprint import pprint
import utils
from passlib.context import CryptContext

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

class SignUp(BaseModel):
    name:str
    email:str
    password:str


class History(BaseModel):
    query:str
    user_id:str

class Login(BaseModel):
    email:str
    password:str

while True:
    try:
        conn=psycopg2.connect(host='*******',database="website_keyword",user='postgres',password="********",cursor_factory=RealDictCursor)
        cursor=conn.cursor()
        print("Connection Succesfull")
        break
    
    except Exception as err:
        print(str(err))
        time.sleep(2)

app = FastAPI()


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/add_url/")
async def add_site(site:Site):
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

@app.get("/search_data")
async def search_data(inp:str,page_no:int=1):
    try:
        kw_extractor = yake.KeywordExtractor()
        keywords=kw_extractor.extract_keywords(inp)
        keywords=list(map(list,keywords))
        keywords=list(list(zip(*keywords))[0])
        keywords_set=set(keywords)
        print(keywords)
    except IndexError:
        raise HTTPException(status_code=404,detail="Page Not Found")
        
    query_string="SELECT * FROM all_data where ("+" OR ".join(["%s=any(keywords)"]*len(keywords)) + ")"
    #  AND ALT LIKE '%%" + "%%".join(keywords[0].split()) + "%%'"
    cursor.execute(query_string,keywords)
    data=cursor.fetchall()
    order_dic={}
    for i in data:
        commons=keywords_set.intersection(set(i['keywords']))
        try:
            order_dic[len(commons)].append(i)
        except KeyError:
            order_dic[len(commons)]=[]
            order_dic[len(commons)].append(i)

    rev_sort_keys=list(order_dic.keys())
    rev_sort_keys.sort(reverse=True)
    final_list=[]

    for l in rev_sort_keys:
        order_dic[l].sort(reverse=True,key=lambda x:datetime.datetime.strptime(x['datetime'],"%Y-%m-%d %H:%M:%S")if x['datetime']!="None" else datetime.datetime.min) 
        
        final_list+=order_dic[l]
    

    order_dic.clear()
    
    if(len(final_list)>50):
        return_data=final_list[(page_no-1)*50:page_no*50]
    else:
        return_data=final_list    
    if len(return_data)==0:
        raise HTTPException(status_code=404,detail="Page Not Found")
    return {
            "keywords":keywords,
            "total":len(return_data),
            "results":return_data,
            }

@app.get("/autocomplete")
async def autocomplete(query:str):  
    query_string="SELECT * FROM KEYWORDS WHERE WORDS LIKE %s"
    cursor.execute(query_string,(query+"%%",))
    data=cursor.fetchall()
    keywordList = []
    for i in data:
        keywordList.append(i["words"])
    keywordList.sort(key=lambda x:utils.count_words(x))
       
    return {
        "total":len(keywordList[:10]),
        "keywords":keywordList[:10]   
    }
    

pwd_context=CryptContext(schemes=['bcrypt'],deprecated="auto")
@app.post("/signup")
def signup(signup:SignUp):
    hashed_pass=pwd_context.hash(signup.password)
    cursor.execute("""INSERT INTO USERS (name,email,password) values (%s,%s,%s)""",(signup.name,signup.email,hashed_pass))
    conn.commit()
    return "success"


@app.post("/login")
def login(login:Login):
    cursor.execute("""SELECT * FROM USERS WHERE email=%s""",(login.email,))
    user=cursor.fetchone()
    if user:
        if pwd_context.verify(login.password,user['password']):
            return user["user_id"]
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Email or Password Wrong")
    else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Email or Password Wrong")

@app.post("/add_history")
def add_history(data:History):
    cursor.execute("""
    INSERT INTO HISTORY (user_id,query) values (%s,%s);
    """,(data.user_id,data.query))
    conn.commit()
    return "success"

@app.get("/get_detial_history")
def get_detailed_history(user_id:str):
    cursor.execute("""
    SELECT * FROM HISTORY WHERE user_id=%s
    """,(user_id,))
    history=cursor.fetchall()
    history.sort(reverse=True,key=lambda x:x['searched_at']) 
    return history

@app.get("/get_just_history")
def get_just_history(user_id:str):
    cursor.execute(
        """
        SELECT * from HISTORY WHERE user_id=%s
        """,(user_id,))
    history =cursor.fetchall()
    
    history.sort(reverse=True,key=lambda x:x['searched_at']) 
    
    history=[hist['query'] for hist in history]
    return history[:20]
