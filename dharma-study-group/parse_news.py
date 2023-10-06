import json
import requests
from bs4 import BeautifulSoup

from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker, declarative_base


BASE_URL = "https://www.tcnews.com.tw"

def get_next_page_link(url, news_urls, index=0, limit=25):
    res = requests.get(f"{BASE_URL}{url}")
    soup = BeautifulSoup(res.text, 'html.parser')

    news_list = soup.find_all('div', class_='grid-item-inner')
    for news in news_list:
        news_urls.append(news.find('a', class_='post-thumb').get('href'))

    if index < limit:
        index += 1
        link = soup.select_one('a[aria-label="Next"]')
        if link:
            href = link.get('href')
            print(f"next: {href}")
            get_next_page_link(href, news_urls, index, limit)
        else:
            print("no links found")

def parse_news(url):
    ret = {"url": url}
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    script = soup.find("script", type="application/ld+json")
    # 取得 script 內容
    script_json = json.loads(script.text)

    # 取得 headline
    ret["title"] = script_json["headline"]

    # 取得 datePublished
    ret["date"] = script_json["datePublished"]

    # 取得 div 節點
    div = soup.find("div", class_="post-content")

    # 取得 div 節點中的 p 節點
    ps = div.find_all("p")
    texts = []
    for p in ps:
        if p.has_attr("style") and "text-align: right;" in p["style"]:
            break
        if not p.find("img"):
            texts.append(p.text.strip())

    # text = text.replace('\xa0', '').replace('\n', '').replace('\r', '').replace(' ', '')
    ret["content"] = "".join(texts)

    # print(f"{headline}\n{datePublished}\n{text}")
    return ret


engine = create_engine("sqlite:///my_database.db")

Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

class News(Base):
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    date = Column(String)
    url = Column(String)
    content = Column(String)

Base.metadata.create_all(engine)

news_urls = []
get_next_page_link("/news/itemlist/category/142.html", news_urls)
get_next_page_link("/education/itemlist/category/196.html", news_urls, 0, 12)

for url in news_urls:
    print(url)
    session.add(News(**parse_news(url)))
    session.commit()
# print(news_urls)

session.close()