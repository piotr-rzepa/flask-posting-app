import functools

import delorean
import flask
from bson.objectid import ObjectId
from werkzeug.security import check_password_hash, generate_password_hash

from db.db import get_collection
from utils.common import HTTPMethod

bp = flask.Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=(HTTPMethod.GET.value, HTTPMethod.POST.value))
def register():
    """Route for creating an account in application."""
    if flask.request.method == "POST":
        username = flask.request.form["username"]
        password = flask.request.form["password"]
        users_collection = get_collection("users")
        user_hit = users_collection.find_one({"username": username})
        error = None
        if not username:
            error = "Username is required"
        elif not password:
            error = "Password is required"
        elif user_hit is not None:
            error = "User {username} already exists".format(username=username)

        if error is None:
            users_collection.insert_one(
                {
                    "username": username,
                    "password": generate_password_hash(password),
                    "created_at": delorean.Delorean().naive,
                }
            )
            flask.current_app.logger.debug(
                "Successfully created new user `{username}`".format(username=username),
            )
            return flask.redirect(flask.url_for("auth.login"))

        flask.flash(error)

    return flask.render_template("auth/register.html")


@bp.route("/login", methods=(HTTPMethod.GET.value, HTTPMethod.POST.value))
def login():
    """Route for logging in using created account."""
    if flask.request.method == "POST":
        username = flask.request.form["username"]
        password = flask.request.form["password"]
        users = get_collection("users")
        error = None

        user = users.find_one({"username": username})
        if user is None:
            error = "Could not find user {username}".format(username=username)

        elif not check_password_hash(user["password"], password):
            error = "Incorrect password"

        if error is None:
            flask.session.clear()
            flask.session["user_id"] = str(user["_id"])
            flask.current_app.logger.debug(
                "User `{username}` successfully logged in".format(username=username),
            )
            return flask.redirect(flask.url_for("index"))

        flask.flash(error)

    return flask.render_template("auth/login.html")


@bp.before_app_request
def load_logged_in_user():
    """Loads user information from session, if he was logged in before."""
    user_id = flask.session.get("user_id")

    if user_id is None:
        flask.g.user = None
    else:
        users = get_collection("users")
        flask.g.user = users.find_one({"_id": ObjectId(user_id)})


@bp.route("/logout")
def logout():
    """Route for logging out a user from his account."""
    flask.session.clear()
    flask.current_app.logger.debug(
        "User `{username}` logged out successfully".format(
            username=flask.g.user["username"],
        ),
    )
    return flask.redirect(flask.url_for("index"))


def login_required(view):
    """Helper decorator for imposing authorization for given route."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if flask.g.user is None:
            return flask.redirect(flask.url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view
