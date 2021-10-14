# 愛料理爬蟲

from __future__ import with_statement
import contextlib
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

try:
    from urllib.request import urlopen
except:
    from urllib2 import urlopen

import sys

from random import random

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time



def make_tiny(url):
    request_url = ('http://tinyurl.com/api-create.php?' + urlencode({'url':url}))
    with contextlib.closing(urlopen(request_url)) as response:
        return response.read().decode('utf-8')


class Cook_search:
    def __init__(self, type_, style):
        self.type_ = type_
        self.style = style

    def scrape(self):
        ## 使用假header
        ua = UserAgent()
        user_agent = ua.safari
        # user_agent = ua.ie
        # user_agent = 'Firefox browser\'s user-agent'
        # user_agent = 'Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0)'
        headers = {'User-Agent': user_agent}

        response = requests.get(
            "https://cookpad.com/tw/%E6%90%9C%E5%B0%8B/" + self.type_ +
            "%20" + self.style +
            "?event=search.history", headers=headers)

        soup = BeautifulSoup(response.content, "html.parser")
        # print(soup)

        # 爬取前五筆餐廳卡片資料
        cards = soup.find_all(
            'li', {'class': 'block-link card border-cookpad-gray-400 border-t-0 border-l-0 border-r-0 border-b flex m-0 rounded-none overflow-hidden ranked-list__item xs:border-b-none xs:mb-sm xs:rounded'}, limit=5)

        content = []
        result = []
        for card in cards:
            # 料理名稱
            title = card.find(
                "a", {"class": "block-link__main"}).getText()
            title = title.replace('/', '-')
            title = title[:13]

            # 花費時間
            try:
                spantime = card.find("span", {"class": "mise-icon-text"}).getText()
            except:
                spantime = 'None'

            # 簡介
            try:
                info = card.find("div", {"class": "clamp-2 break-words"}).getText()
                info = info[:40]
            except:
                info = 'None'

            # 連結
            try:
                url = card.find("a")
                url = 'https://cookpad.com' + url["href"]
                url = make_tiny(url)

            except:
                url = 'https://cookpad.com'

            # 圖片網址
            try:
                response = requests.get(url, headers=headers)
                soup = BeautifulSoup(response.content, "html.parser")
                img_url = soup.find('div', {'class', 'tofu_image'})
                img_url = img_url.select_one("img").get('data-original')
                img_url = make_tiny(img_url)
            except:
                img_url = 'https://i.imgur.com/bUTHY8X.jpg'

            # 預備食材
            # ingredients = ''
            # response = requests.get(url, headers=headers)
            # soup = BeautifulSoup(response.content, "html.parser")
            # ingredients = ingredients + soup.find('div', {'class', 'ingredient-list'}, 'li').getText()


            # 將取得的餐廳名稱、評價及地址連結一起，並且指派給content變數
            content = [title, spantime, info, url, img_url]
            # print(ingredients)
            result.append(content)

        return result

class Cook_keyword:
    def __init__(self, keyword):
        self.keyword = keyword

    def scrape(self):
        ## 使用假header
        ua = UserAgent()
        user_agent = ua.safari
        # user_agent = ua.ie
        # user_agent = 'Firefox browser\'s user-agent'
        # user_agent = 'Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0)'
        headers = {'User-Agent': user_agent}
                       #'Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0)'}

        response = requests.get(
            "https://cookpad.com/tw/%E6%90%9C%E5%B0%8B/" + self.keyword +
            "?event=search.history", headers=headers)

        soup = BeautifulSoup(response.content, "html.parser")
        # print(soup)

        # 爬取前五筆餐廳卡片資料
        cards = soup.find_all(
            'li', {'class': 'block-link card border-cookpad-gray-400 border-t-0 border-l-0 border-r-0 border-b flex m-0 rounded-none overflow-hidden ranked-list__item xs:border-b-none xs:mb-sm xs:rounded'}, limit=5)

        content = []
        result = []
        for card in cards:
            # 料理名稱
            title = card.find(
                "a", {"class": "block-link__main"}).getText()
            title = title.replace('/', '-')
            title = title[:13]

            # 花費時間
            try:
                spantime = card.find("span", {"class": "mise-icon-text"}).getText()
            except:
                spantime = 'None'

            # 簡介
            try:
                info = card.find("div", {"class": "clamp-2 break-words"}).getText()
                info = info[:40]
            except:
                info = 'None'

            # 連結
            try:
                url = card.find("a")
                url = 'https://cookpad.com' + url["href"]
                url = make_tiny(url)

            except:
                url = 'https://cookpad.com'

            # 圖片網址
            try:
                response = requests.get(url, headers=headers)
                soup = BeautifulSoup(response.content, "html.parser")
                img_url = soup.find('div', {'class', 'tofu_image'})
                img_url = img_url.select_one("img").get('data-original')
                img_url = make_tiny(img_url)
            except:
                img_url = 'https://i.imgur.com/bUTHY8X.jpg'

            # 預備食材
            # ingredients = ''
            # response = requests.get(url, headers=headers)
            # soup = BeautifulSoup(response.content, "html.parser")
            # ingredients = ingredients + soup.find('div', {'class', 'ingredient-list'}, 'li').getText()


            # 將取得的餐廳名稱、評價及地址連結一起，並且指派給content變數
            content = [title, spantime, info, url, img_url]
            # print(content)
            # print(ingredients)
            result.append(content)
            # time.sleep(1)


        return result

if __name__ == '__main__':
    # cook = Cook_search('晚餐', '其他')
    # content = cook.scrape()
    cook = Cook_keyword('布丁')
    content = cook.scrape()
    print(content)
