import flask
from bson.objectid import ObjectId
from delorean import Delorean
from werkzeug.exceptions import abort

from auth import auth
from db import db
from utils.common import HTTPMethod, StatusCode

bp = flask.Blueprint("blog", __name__)


@bp.route("/")
def index():
    """Route for rendering main page with all posts."""
    posts = db.get_collection("posts")
    all_posts = posts.find()
    return flask.render_template("blog/index.html", posts=all_posts)


@bp.route("/create", methods=(HTTPMethod.GET.value, HTTPMethod.POST.value))
@auth.login_required
def create():
    """Route for creating a new post."""
    if flask.request.method == HTTPMethod.POST.value:
        post_title = flask.request.form["title"]
        post_body = flask.request.form["body"]
        error = None

        if not post_title:
            error = "Post title is required"

        if error is not None:
            flask.flash(error)
        else:
            posts_collection = db.get_collection("posts")
            posts_collection.insert_one(
                {
                    "title": post_title,
                    "body": post_body,
                    "author": {
                        key: flask.g.user[key]
                        for key in flask.g.user
                        if key != "password"
                    },
                    "created_at": Delorean().naive,
                },
            )
            return flask.redirect(flask.url_for("blog.index"))
    return flask.render_template("blog/create.html")


@bp.route(
    "/<string:post_id>/update",
    methods=(HTTPMethod.GET.value, HTTPMethod.POST.value),
)
@auth.login_required
def update(post_id: str, verify_author: bool = True):
    """Route for updating an existing post.

    Applicable only to posts, which are created by logged in user.
    """
    posts_collection = db.get_collection("posts")
    post = posts_collection.find_one({"_id": ObjectId(post_id)})

    if post is None:
        abort(
            StatusCode.NOT_FOUND.value,
            "Post id {post_id} doesn't exist.".format(post_id=post_id),
        )

    if verify_author and str(post["author"]["_id"]) != str(flask.g.user["_id"]):
        abort(StatusCode.FORBIDDEN.value)

    if flask.request.method == HTTPMethod.POST.value:
        post_title = flask.request.form["title"]
        post_body = flask.request.form["body"]
        error = None

        if not post_title:
            error = "Post title is required."

        if error is not None:
            flask.flash(error)
        else:
            posts_collection.update_one(
                {"_id": ObjectId(post_id)},
                {"$set": {"title": post_title, "body": post_body}},
            )
            return flask.redirect(flask.url_for("blog.index"))

    return flask.render_template("blog/update.html", post=post)


@bp.post("/<string:post_id>/delete")
@auth.login_required
def delete(post_id: str, verify_author: bool = True):
    """Route for deleting given post."""
    posts_collection = db.get_collection("posts")
    post = posts_collection.find_one({"_id": ObjectId(post_id)})

    if post is None:
        abort(
            StatusCode.NOT_FOUND.value,
            "Post id {post_id} doesn't exist.".format(post_id=post_id),
        )

    if verify_author and str(post["author"]["_id"]) != str(flask.g.user["_id"]):
        abort(StatusCode.FORBIDDEN.value)

    posts_collection.delete_one({"_id": ObjectId(post_id)})
    return flask.redirect(flask.url_for("blog.index"))
