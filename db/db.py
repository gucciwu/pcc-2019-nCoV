"""
@ProjectName: DXY-2019-nCov-Crawler
@FileName: db.py
@Author: Jiabao Lin
@Date: 2020/1/21
"""
from bson import ObjectId
from flask import jsonify
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['pcc_core']


class DB:
    def __init__(self):
        self.db = db

    def insert(self, collection, data):
        self.db[collection].insert(data)

    def find_one(self, collection, data=None, province_name=None, summary=None, modify_time=None):
        if collection == 'DXYOverall':
            return self.db[collection].find_one(data)

        if collection == 'DXYProvince':
            return self.db[collection].find_one(
                {
                    'provinceName': province_name,
                    'modifyTime': modify_time
                }
            )

        if collection == 'DXYArea':
            return self.db[collection].find_one(data)

        if collection == 'DXYNews':
            return self.db[collection].find_one(
                {
                    'summary': summary,
                    'modifyTime': modify_time
                }
            )

    def query_collection(self, collection, filter_data=None):
        if filter_data is None:
            filter_data = {}
        records = self.db[collection].find(filter_data, {"_id": 0})
        result = []
        for r in records:
            result.append(r)
        return result
