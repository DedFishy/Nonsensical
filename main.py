import os
import flask
from db import Database
import util
from const import DEBUG_MODE, TOKEN_EXPIRY_TIME, UPLOAD_FOLDER

import faulthandler


faulthandler.enable()

app = flask.Flask(__name__)
db = Database()

if DEBUG_MODE: app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.route("/")
def index():
    if util.get_is_logged_in() and db.get_user_by_request() is not None:
        return flask.render_template("list.html")
    else:
        return flask.render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    succeeded, result = db.login_or_signup_by_request()
    if not succeeded:
        print("Failed login/signup:", result)
        return util.get_error_template("Error", result, "/", "Return")
    else:
        response = flask.redirect("/", 301)
        response.set_cookie("token", result, max_age=TOKEN_EXPIRY_TIME)
        return response

@app.route("/posts")
def post_fetch():
    return {"posts": db.get_posts_by_request()}

@app.route("/posts/<post>")
def single_post(post):
    print(post)
    post_data = db.get_post_by_id(post)
    return flask.render_template("post.html", title=post_data["title"], poster=post_data["owner"], body=post_data["body"], post_id=post_data["id"], files=post_data["files"], date=post_data["creation"])

@app.route("/newpost")
def new_post():
    user = db.get_user_by_request()
    if not user: return flask.redirect("/", 301)
    return flask.render_template("newpost.html", username=user["username"])

@app.route("/makepost", methods=["POST"])
def make_post():
    success, message = db.create_post_by_request()
    if success:
        return flask.redirect(f"/posts/{message}", 301)
    return util.get_error_template("Error", message, "/newpost", "Return")

@app.route("/postmedia/<post>/<file>")
def get_post_media(post, file):
    return flask.send_from_directory(UPLOAD_FOLDER, os.path.join(post, file), as_attachment=True)
    
@app.route("/header")
def header():
    user = db.get_user_by_request()
    return flask.render_template("header.html", username=user["username"] if user is not None else "")


if __name__ == "__main__":
    app.run("0.0.0.0", 8080)
    db.close()