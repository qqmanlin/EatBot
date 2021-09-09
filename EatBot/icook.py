# 愛料理爬蟲
import requests
from bs4 import BeautifulSoup

class Icook:
    def __init__(self, type_, style):
        self.type_ = type_
        self.style = style

    def scrape(self):
        response = requests.get(
            "https://icook.tw/search/" + self.type_ +
            "/%20/" + self.style +
            "/")

        soup = BeautifulSoup(response.text, "html.parser")

        sel = soup.select("div.title a")
        content = ""

        return sel

if __name__ == '__main__':
    Icook = Icook('晚餐', '炸')
    content = Icook.scrape()
    print(content)