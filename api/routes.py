from flask import jsonify

from . import app, mongo


# @app.route('/province', methods=['GET'])
# def get_by_province():
#     records = mongo.db['DXYProvince'].find()
#     return jsonify({'result': records})
#
#
# @app.route('/news', methods=['GET'])
# def get_by_province():
#     records = mongo.db['DXYNews'].find()
#     output = []
#     for r in records:
#         output.append({'name': r['name'], 'pwd': r['pwd']})
#     return jsonify({'result': output})
#
#
# @app.route('/area', methods=['GET'])
# def get_by_province():
#     records = mongo.db['DXYArea'].find()
#     output = []
#     for r in records:
#         output.append({'name': r['name'], 'pwd': r['pwd']})
#     return jsonify({'result': output})
