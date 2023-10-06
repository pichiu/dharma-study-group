import requests
from bs4 import BeautifulSoup

from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker, declarative_base


BASE_URL = "https://tw.tzuchi.org"

def get_next_page_link(url, news_urls, index=0, limit=25):
    res = requests.get(f"{BASE_URL}{url}")
    soup = BeautifulSoup(res.text, 'html.parser')

    sec1_list = soup.find_all('tr', class_='sectiontableentry1')
    for news in sec1_list:
        news_urls.append(news.find('a').get('href'))
    
    sec2_list = soup.find_all('tr', class_='sectiontableentry2')
    for news in sec2_list:
        news_urls.append(news.find('a').get('href'))

    if index < limit:
        index += 1
        link = soup.find("a", title="下一個")
        if link:
            href = link.get('href')
            print(f"next: {href}")
            get_next_page_link(href, news_urls, index, limit)
        else:
            print("no links found")

def parse_news(url):
    full_url = f"{BASE_URL}{url}"
    ret = {"url": full_url}
    res = requests.get(full_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    ret["title"] = soup.find("title").text

    span = soup.find("span", class_="createby").text.strip()
    ret["date"] = span[:span.find("|")]

    texts = []
    div = soup.find("div", class_="article-content")
    for s in div.stripped_strings:
        text = s.replace('\xa0', '').replace('\n', '').replace('\r', '')
        if text == "< 前一個" or text == "下一個 >" or text == "Tweet":
            continue
        if text.startswith("圖左：") or text.startswith("圖右："):
            text = text[text.find("：")+1:]
        if "[攝影者" in text:
            text = text[:text.find("[攝影者")]
        texts.append(text)
    ret["content"] = "".join(texts)
    return ret


engine = create_engine("sqlite:///my_database.db")

Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

class CommunityNews(Base):
    __tablename__ = 'community_news'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    date = Column(String)
    url = Column(String)
    content = Column(String)

Base.metadata.create_all(engine)

news_urls = []
get_next_page_link("/community/index.php?option=com_content&view=category&id=62&Itemid=283", news_urls)

for url in news_urls:
    print(url)
    session.add(CommunityNews(**parse_news(url)))
    session.commit()
# print(news_urls)

session.close()