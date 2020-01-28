from flask import Blueprint, jsonify

from app.db.db import DB

db = DB()

api_view = Blueprint("api", __name__, url_prefix='/api')


@api_view.route('/province', methods=['GET'])
def fetch_province():
    records = db.query_collection('DXYProvince')
    return jsonify({'results': records})


@api_view.route('/news', methods=['GET'])
def fetch_news():
    records = db.query_collection('DXYNews')
    return jsonify({'results': records})


@api_view.route('/area', methods=['GET'])
def fetch_area():
    records = db.query_collection('DXYArea')
    return jsonify({'results': records})


@api_view.route('/area/<string:province_name>', methods=['GET'])
def get_area_by_province(province_name):
    records = db.query_collection('DXYArea',
                                  {'$or': [{'provinceName': province_name}, {'provinceShortName': province_name}]})
    return jsonify({'results': records})


@api_view.route('/area/<string:province_name>/<string:city_name>', methods=['GET'])
def get_area_by_city(province_name, city_name):
    records = db.query_collection('DXYArea',
                                  {'$or': [{'provinceName': province_name}, {'provinceShortName': province_name}]})
    ret = {}
    # '武汉市' => '武汉'
    if city_name[-1] == '市':
        city_name = city_name[:-1]

    if len(records) > 0:
        cities = records[0]['cities']
        for c in cities:
            if city_name in c['cityName']:
                ret = c
                break

    return jsonify({'results': ret})


@api_view.route('/rumors', methods=['GET'])
def fetch_rumor():
    records = db.query_collection('DXYRumor')
    return jsonify({'results': records})
