"""
@ProjectName: DXY-2019-nCov-Crawler
@FileName: crawler.py
@Author: Jiabao Lin
@Date: 2020/1/21
"""
from bs4 import BeautifulSoup

from .countryTypeMap import country_type
from .db import DB
import re
import json
import time
import logging
import datetime
import requests

from app.parser import regex_parser

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'
}


class Crawler:
    def __init__(self):
        self.session = requests.session()
        self.session.headers.update(headers)
        self.db = DB()
        self.crawl_timestamp = int()
        self.url = "https://3g.dxy.cn/newh5/view/pneumonia"

    def run(self):
        while True:
            self.crawler()
            time.sleep(60)

    def crawler(self):
        while True:
            self.crawl_timestamp = int(datetime.datetime.timestamp(datetime.datetime.now()) * 1000)
            r = self.session.get(url=self.url)
            soup = BeautifulSoup(r.content, 'lxml')
            overall_information = re.search(r'\{("id".*?)\}', str(soup.find('script', attrs={'id': 'getStatisticsService'})))
            province_information = re.search(r'\[(.*?)\]', str(soup.find('script', attrs={'id': 'getListByCountryTypeService1'})))
            area_information = re.search(r'\[(.*)\]', str(soup.find('script', attrs={'id': 'getAreaStat'})))
            news = re.search(r'\[(.*?)\]', str(soup.find('script', attrs={'id': 'getTimelineService'})))

            if not overall_information or not province_information or not area_information or not news:
                continue

            self.overall_parser(overall_information=overall_information)
            self.province_parser(province_information=province_information)
            self.area_parser(area_information=area_information)
            self.news_parser(news=news)

            break

        logger.info('Successfully crawled.')

    def overall_parser(self, overall_information):
        overall_information = json.loads(overall_information.group(0))
        overall_information.pop('id')
        overall_information.pop('createTime')
        overall_information.pop('modifyTime')
        overall_information.pop('imgUrl')
        overall_information.pop('deleted')
        overall_information['countRemark'] = overall_information['countRemark'].replace(' 疑似', '，疑似').replace(' 治愈', '，治愈').replace(' 死亡', '，死亡').replace(' ', '')
        if not self.db.find_one(collection='DXYOverall', data=overall_information):
            overall_information['updateTime'] = self.crawl_timestamp
            overall_information = regex_parser(content=overall_information, key='countRemark')

            self.db.insert(collection='DXYOverall', data=overall_information)

    def province_parser(self, province_information):
        provinces = json.loads(province_information.group(0))
        for province in provinces:
            if self.db.find_one(collection='DXYProvince', province_name=province['provinceName'], modify_time=province['modifyTime']):
                continue
            province.pop('id')
            province['comment'] = province['comment'].replace(' ', '')
            province['crawlTime'] = self.crawl_timestamp
            province['country'] = country_type.get(province['countryType'])
            province['tags'] = province['tags'].replace(' ', '')

            province = regex_parser(content=province, key='tags')

            self.db.insert(collection='DXYProvince', data=province)

    def area_parser(self, area_information):
        area_information = json.loads(area_information.group(0))
        for area in area_information:
            area['comment'] = area['comment'].replace(' ', '')
            if self.db.find_one(collection='DXYArea', data=area):
                continue
            area['updateTime'] = self.crawl_timestamp
            self.db.insert(collection='DXYArea', data=area)

    def news_parser(self, news):
        news = json.loads(news.group(0))
        for _news in news:
            if self.db.find_one(collection='DXYNews', summary=_news['summary'], modify_time=_news['modifyTime']):
                continue
            _news.pop('pubDateStr')
            _news['crawlTime'] = self.crawl_timestamp
            self.db.insert(collection='DXYNews', data=_news)


if __name__ == '__main__':
    crawler = Crawler()
    crawler.run()
