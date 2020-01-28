"""
@ProjectName: DXY-2019-nCov-Crawler
@FileName: crawler.py
@Author: Jiabao Lin
@Date: 2020/1/21
"""
from bs4 import BeautifulSoup
import re
import json
import time
import logging
import datetime
import requests

from app.crawler.countryTypeMap import country_type
from app.crawler.parser import regex_parser
from app.settings import AppConfig

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'
}


class Crawler:
    def __init__(self, db):
        self.session = requests.session()
        self.session.headers.update(headers)
        self.db = db
        self.crawl_timestamp = int()
        self.url = "https://3g.dxy.cn/newh5/view/pneumonia"
        self.rumor_url = "https://file1.dxycdn.com/2020/0127/797/3393185293879908067-115.json"
        self.overall_count = 0
        self.province_count = 0
        self.area_count = 0
        self.news_count = 0
        self.rumor_count = 0

    def run(self):
        while True:
            self.crawler()
            time.sleep(AppConfig.CRAWLER_FREQUENCY)

    def crawler(self):
        while True:
            self.overall_count = 0
            self.province_count = 0
            self.area_count = 0
            self.news_count = 0
            self.rumor_count = 0

            self.crawl_timestamp = int(datetime.datetime.timestamp(datetime.datetime.now()) * 1000)
            r = self.session.get(url=self.url)
            soup = BeautifulSoup(r.content, 'lxml')
            overall_information = re.search(r'\{("id".*?)\}', str(soup.find('script', attrs={'id': 'getStatisticsService'})))
            province_information = re.search(r'\[(.*?)\]', str(soup.find('script', attrs={'id': 'getListByCountryTypeService1'})))
            area_information = re.search(r'\[(.*)\]', str(soup.find('script', attrs={'id': 'getAreaStat'})))
            abroad_information = re.search(r'\[(.*)\]', str(soup.find('script', attrs={'id': 'getListByCountryTypeService2'})))
            news = re.search(r'\[(.*?)\]', str(soup.find('script', attrs={'id': 'getTimelineService'})))

            top_rumor_information = re.search(r'\[(.*)\]', str(soup.find('script', attrs={'id': 'getIndexRumorList'})))
            rumor_resp = self.session.get(url=self.rumor_url + '?t=' + str(self.crawl_timestamp))
            rumor_information = rumor_resp.json()

            if not overall_information \
                    or not province_information \
                    or not area_information \
                    or not news \
                    or not rumor_information \
                    or not top_rumor_information:
                continue

            self.overall_parser(overall_information=overall_information)
            self.province_parser(province_information=province_information)
            self.area_parser(area_information=area_information)
            self.abroad_parser(abroad_information=abroad_information)
            self.news_parser(news=news)
            self.rumor_parser(rumor_information=top_rumor_information)
            self.rumor_parser(rumor_information=rumor_information, is_json_data=True)

            break

        logger.info('Successfully crawled. Added %d overall, %d province, %d area, %d news, %d rumor.' %
                    (self.overall_count, self.province_count, self.area_count, self.news_count, self.rumor_count))

    def overall_parser(self, overall_information):
        if not overall_information:
            return
        overall_information = json.loads(overall_information.group(0))
        overall_information.pop('id')
        overall_information.pop('createTime')
        overall_information.pop('modifyTime')
        overall_information.pop('imgUrl')
        overall_information.pop('deleted')
        overall_information['countRemark'] = overall_information['countRemark'].replace(' 疑似', '，疑似').replace(' 治愈', '，治愈').replace(' 死亡', '，死亡').replace(' ', '')
        if not self.db.find_one(collection=AppConfig.DB_COLLECTION_OVERALL, data=overall_information):
            overall_information['updateTime'] = self.crawl_timestamp
            overall_information['crawlTime'] = self.crawl_timestamp

            overall_information = regex_parser(content=overall_information, key='countRemark')
            self.overall_count += 1
            self.db.insert(collection=AppConfig.DB_COLLECTION_OVERALL, data=overall_information)

    def province_parser(self, province_information):
        if not province_information:
            return
        provinces = json.loads(province_information.group(0))
        for province in provinces:
            province.pop('id')
            province.pop('tags')
            province.pop('sort')
            province['comment'] = province['comment'].replace(' ', '')
            if self.db.find_one(collection=AppConfig.DB_COLLECTION_PROVINCE, data=province):
                continue
            province['crawlTime'] = self.crawl_timestamp
            province['country'] = country_type.get(province['countryType'])

            self.province_count += 1
            self.db.insert(collection=AppConfig.DB_COLLECTION_PROVINCE, data=province)

    def area_parser(self, area_information):
        if not area_information:
            return
        area_information = json.loads(area_information.group(0))
        for area in area_information:
            area['comment'] = area['comment'].replace(' ', '')
            if self.db.find_one(collection=AppConfig.DB_COLLECTION_AREA, data=area):
                continue
            area['country'] = '中国'
            area['updateTime'] = self.crawl_timestamp
            area['crawlTime'] = self.crawl_timestamp

            self.area_count += 1
            self.db.insert(collection=AppConfig.DB_COLLECTION_AREA, data=area)

    def abroad_parser(self, abroad_information):
        if not abroad_information:
            return
        countries = json.loads(abroad_information.group(0))
        for country in countries:
            country.pop('id')
            country.pop('tags')
            country.pop('countryType')
            country.pop('provinceId')
            country['country'] = country.pop('provinceName')
            country.pop('provinceShortName')
            country.pop('cityName')
            country.pop('sort')

            country['comment'] = country['comment'].replace(' ', '')
            if self.db.find_one(collection=AppConfig.DB_COLLECTION_AREA, data=country):
                continue
            country['updateTime'] = self.crawl_timestamp
            country['crawlTime'] = self.crawl_timestamp
            self.area_count += 1
            self.db.insert(collection=AppConfig.DB_COLLECTION_AREA, data=country)

    def news_parser(self, news):
        if not news:
            return
        news = json.loads(news.group(0))
        for _news in news:
            _news.pop('pubDateStr')
            if self.db.find_one(collection=AppConfig.DB_COLLECTION_NEWS, data=_news):
                continue
            _news['crawlTime'] = self.crawl_timestamp

            self.news_count += 1
            self.db.insert(collection=AppConfig.DB_COLLECTION_NEWS, data=_news)

    def rumor_parser(self, rumor_information, is_json_data=False):
        if not rumor_information:
            return

        if not is_json_data:
            rumor = json.loads(rumor_information.group(0))
        else:
            rumor = rumor_information['data']
        for _rumor in rumor:
            # drop top prefix
            if _rumor['title'].startswith('NO.'):
                _rumor['title'] = _rumor['title'][5:]

            if self.db.find_one(collection=AppConfig.DB_COLLECTION_RUMOR,
                                data={'summary': _rumor['summary'], 'title': _rumor['title']}):
                continue

            _rumor['crawlTime'] = self.crawl_timestamp

            self.rumor_count += 1
            self.db.insert(collection=AppConfig.DB_COLLECTION_RUMOR, data=_rumor)

