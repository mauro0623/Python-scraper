""" Script for scraping ebay and barnes and nobles products given product list url """
import abc
from collections import namedtuple
from datetime import date
from typing import List

from bs4 import BeautifulSoup
import pandas as pd
import requests

Item = namedtuple("Item", "url img_url name price")


class Scraper(abc.ABC):
    NAME: str

    def scrape_shop(self, url: str):
        soup = make_request(url)
        items = self.parse_page_items(soup)
        file_name = save_to_csv(items, self.NAME)
        print(f"{len(items)} items saved to {file_name}")

    @abc.abstractmethod
    def parse_page_items(self, soup) -> List[Item]:
        pass

    @staticmethod
    @abc.abstractmethod
    def parse_item(soup) -> Item:
        pass


class EbayScraper(Scraper):
    NAME = 'ebay'

    def parse_page_items(self, soup) -> List[Item]:
        results = soup.find("ul", {"class": "srp-results"})
        items = results.find_all("li", {"class": "s-item"})
        return [self.parse_item(x) for x in items]

    @staticmethod
    def parse_item(soup) -> Item:
        url = soup.find("a")["href"]
        img_url = soup.find("img", {"class": "s-item__image-img"})["src"]
        name = soup.find("h3", {"class": "s-item__title"}).text.strip()
        price = soup.find("span", {"class": "s-item__price"}).text.strip()
        return Item(url, img_url, name, price)

    
class BarnesScraper(Scraper):
    NAME = 'barnesandnoble'

    def parse_page_items(self, soup) -> List[Item]:
        items = soup.find_all("div", {"class": "product-shelf-tile-book"})
        return [self.parse_item(x) for x in items]

    @staticmethod
    def parse_item(soup) -> Item:
        pricing = soup.find('div', {'class': 'product-shelf-pricing'})
        link_tag = pricing.find('a')
        url = link_tag['href']
        name = link_tag['title']
        price = link_tag.find_all('span')[-1].text.strip()
        img_url = soup.find("img")["src"]
        return Item(url, img_url, name, price)


def save_to_csv(data, file_name):
    file_name = f"{file_name}_{date.today()}.csv"
    df = pd.DataFrame(data)
    df.to_csv(file_name, index=None)
    return file_name


def make_request(url: str):
    headers = {
        "User-Agent": ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/81.0.4044.122 Safari/537.36')
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raises an exception if request gives status code like 503, 404, 502 etc.
    return BeautifulSoup(response.content, "html.parser")


if __name__ == "__main__":
    BarnesScraper().scrape_shop('https://www.barnesandnoble.com/s/python+book?_requestid=11773493')
    EbayScraper().scrape_shop('https://www.ebay.com/sch/i.html?_from=R40&_trksid=p2380057.m570.l1313.'
                              'TR11.TRC2.A0.H0.Xpython+bo.TRS1&_nkw=python+book&_sacat=0')
