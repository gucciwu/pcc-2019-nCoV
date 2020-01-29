"""
@ProjectName: DXY-2019-nCov-Crawler
@FileName: db.py
@Author: Jiabao Lin
@Date: 2020/1/21
"""
from pymongo import MongoClient

from app.settings import AppConfig

client = MongoClient(AppConfig.DB_COLLECTION_STR)
db = client[AppConfig.DB_DATABASE]


class DB:
    def __init__(self):
        self.db = db

    def insert(self, collection, data):
        self.db[collection].insert(data)

    def find_one(self, collection, data=None):
        return self.db[collection].find_one(data)

    def query_collection(self, collection, filter_data=None, sort_data=None, limit=None):
        if filter_data is None:
            filter_data = {}
        if sort_data is None:
            sort_data = [('updateTime', -1)] \
                if collection in (AppConfig.DB_COLLECTION_AREA, AppConfig.DB_COLLECTION_OVERALL) \
                else [('crawlTime', -1)]
        if limit is None:
            limit = 0
        records = self.db[collection].find(filter_data, {"_id": 0}).sort(sort_data).limit(limit)
        result = []
        for r in records:
            result.append(r)
        return result
