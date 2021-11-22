from flask import Flask, redirect
import os
from src.auth import auth
from src.bookmarks import bookmarks
from src.database import db
from flask_jwt_extended import JWTManager
from src.database import Bookmark
from src.constants.http_status_codes import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from flasgger import Swagger, swag_from
from src.config.swagger import template, swagger_config


def create(test_config=None):

    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.environ.get('SECRET_KEY'),
            SQLALCHEMY_DATABASE_URI=os.environ.get('SQLALCHEMY_DATABASE_URI'),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY'),
            SWAGGER={
                "title": "Bookmark API",
                "uiversion": 3
            }
        )

    else:
        app.config.from_mapping(test_config)

    db.app = app
    db.init_app(app)
    JWTManager(app)

    app.register_blueprint(auth)
    app.register_blueprint(bookmarks)

    Swagger(app, config=swagger_config, template=template)

    @app.get('/<string:short_url>')
    @swag_from('./docs/short_url.yaml')
    def redirect_to_url(short_url):
        bookmark = Bookmark.query.filter_by(short_url=short_url).first_or_404()

        if bookmark:
            bookmark.visiters = bookmark.visiters+1
            db.session.commit()

            return redirect(bookmark.url)

    @app.errorhandler(HTTP_404_NOT_FOUND)
    def handel_404(e):
        return({
            "error": "not found"
        }), HTTP_404_NOT_FOUND

    @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
    def handel_404(e):
        return({
            "error": "Internal Server Error"
        }), HTTP_500_INTERNAL_SERVER_ERROR

    return app


app = create()
