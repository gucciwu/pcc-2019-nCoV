DEFAULT_SECRET_KEY = "7b973e25e0d4478e8128e6055a43707a"


class AppConfig(object):
    SECRET_KEY = DEFAULT_SECRET_KEY
    SERVER_PORT = 9081
    LOG_PATH = "logs/pcc/"
    DB_COLLECTION_AREA = 'DXYArea'
    DB_COLLECTION_NEWS = 'DXYNews'
    DB_COLLECTION_RUMOR = 'DXYRumor'
    DB_COLLECTION_PROVINCE = 'DXYProvince'
    DB_COLLECTION_OVERALL = 'DXYOverall'
    DB_COLLECTION_STR = 'mongodb://localhost:27017/'
    DB_DATABASE = 'pcc_core'
    CRAWLER_FREQUENCY = 60  # in seconds

