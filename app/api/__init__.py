from app.api.views import api_view


def init_app(app):
    app.register_blueprint(api_view)
