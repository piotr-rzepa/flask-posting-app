import os

import flask

from auth import auth
from blog import blog
from db import db


def create_app() -> flask.Flask:
    """Creates WSGI central application."""
    app = flask.Flask(__name__, instance_relative_config=True)

    app.teardown_appcontext(db.close_database)
    app.config.from_mapping(SECRET_KEY=os.getenv("SECRET_KEY"))

    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)
    app.add_url_rule("/", endpoint="index")

    return app
