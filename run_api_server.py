import platform

from flask import jsonify
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
import tornado.options
import tornado.log
import logging

from api import app
from api.settings import AppConfig
from db.db import DB

db = DB()


class LogFormatter(tornado.log.LogFormatter):

    def __init__(self):
        super(LogFormatter, self).__init__(
            fmt='%(color)s[%(asctime)s %(filename)s:%(funcName)s:%(lineno)d %(levelname)s]%(end_color)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )


@app.route('/api/province', methods=['GET'])
def get_by_province():
    records = db.query_collection('DXYProvince')
    return jsonify({'results': records})


@app.route('/api/news', methods=['GET'])
def get_by_news():
    records = db.query_collection('DXYNews')
    return jsonify({'results': records})


@app.route('/api/area', methods=['GET'])
def get_by_area():
    records = db.query_collection('DXYArea')
    return jsonify({'results': records})


if __name__ == '__main__':
    if platform.system() == "Windows":
        import asyncio

        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    tornado.options.define("port", default=AppConfig.SERVER_PORT, help="run on the given port", type=int)
    tornado.options.parse_command_line()
    tornado.options.log_file_prefix = AppConfig.LOG_PATH + 'tornado_main.log'
    [i.setFormatter(LogFormatter()) for i in logging.getLogger().handlers]
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(AppConfig.SERVER_PORT)
    IOLoop.instance().start()
