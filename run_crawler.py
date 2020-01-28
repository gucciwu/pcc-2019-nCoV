from app.crawler import Crawler
from app.db import DB

db = DB()
if __name__ == '__main__':
    crawler = Crawler(db)
    crawler.run()
