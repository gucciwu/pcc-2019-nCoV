from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'pcc_core'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/pcc_core'
app.url_map.strict_slashes = False

mongo = PyMongo(app)
