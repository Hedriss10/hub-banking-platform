from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restx import Api

from src.database.database import db
from src.database.uri import ensure_sync_postgres_uri
from src.router import ROUTER_NAMESPACES
from src.settings._base import config_by_name, flask_env


def create_app():
    app = Flask(__name__, static_folder='static')
    config_class = config_by_name[flask_env]
    app.config.from_object(config_class)
    app.config['SQLALCHEMY_DATABASE_URI'] = ensure_sync_postgres_uri(
        app.config.get('SQLALCHEMY_DATABASE_URI')
    )

    db.init_app(app)

    authorizations = {
        'Bearer Auth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
        }
    }

    api = Api(
        app,
        prefix=f'/{app.config["APPLICATION_ROOT"]}',
        doc=f'/{app.config["DOCS"]}',
        authorizations=authorizations,
        security='Bearer Auth',
        version='3.0',
        title='Hub Banking Platform API',
        description='API for the Hub Banking Platform',
    )
    app.config['CORS_HEADERS'] = 'Content-Type'
    CORS(
        app,
        resources={r'/*': {'origins': '*'}, r'/static/*': {'origins': '*'}},
    )

    JWTManager(app)

    for ns in ROUTER_NAMESPACES:
        api.add_namespace(ns)

    return app
