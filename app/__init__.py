import os
from flask import Flask
from flask_cors import CORS


def create_app(config=None):
    app = Flask(__name__)
    # load default configuration
    app.config.from_object('app.settings')
    CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "*"}})
    # load environment configuration
    if 'FLASK_CONF' in os.environ:
        app.config.from_envvar('FLASK_CONF')
    # load app sepcified configuration
    if config is not None:
        if isinstance(config, dict):
            app.config.update(config)
        elif config.endswith('.py'):
            app.config.from_pyfile(config)
    return app


