import os
import flask
from db import Database
import util
from const import DEBUG_MODE, MAX_UPLOAD_SIZE, TOKEN_EXPIRY_TIME, UPLOAD_FOLDER

import faulthandler

from config import SECRET_KEY


faulthandler.enable()

app = flask.Flask(__name__)
db = Database()

if DEBUG_MODE: app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_SIZE * 1000 * 1000
app.config["SECRET_KEY"] = SECRET_KEY

@app.route("/")
def index():
    return flask.render_template("homepage_list.html")
        
    
@app.route("/favicon.ico")
def favicon():
    return flask.send_file("static/img/N.ico")
    
@app.route("/user/<username>")
def user(username):
    user = db.get_user_by_username(username)
    if user == None:
        return flask.Response(util.get_error_template("404", "That user was not found", "/", "Return"), 404)
    return flask.render_template("user_list.html", username=username)

@app.route("/pfp/<user>")
def get_pfp(user):
    path = os.path.join("pfp", user)
    if os.path.exists(path):
        return flask.send_from_directory("pfp", user)
    else:
        return flask.send_file("static/img/default-pfp.png")
    
@app.route("/updatepfp", methods=["POST"])
def update_pfp():
    user = db.get_user_by_request()
    if not user: return flask.redirect("/", 301)
    db.update_pfp_by_request()
    return flask.redirect("/account", 301)

@app.route("/login", methods=["GET", "POST"])
def login():
    if flask.request.method == "GET":
        return flask.render_template("login.html")
    else:
        succeeded, result = db.login_or_signup_by_request()
        if not succeeded:
            print("Failed login/signup:", result)
            return util.get_error_template("Error", result, "/login", "Return")
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
    user = db.get_user_by_request()
    post_data = db.get_post_by_id(post)
    return flask.render_template("post.html", title=post_data["title"], poster=post_data["owner"], is_owned=post_data["owner"]==user["username"] if user else False, body=post_data["body"], post_id=post_data["id"], files=post_data["files"], date=post_data["creation"])


@app.route("/posts/<post>/<control>")
def control_post(post, control):
    user = db.get_user_by_request()
    post_data = db.get_post_by_id(post)
    if user is None or post_data is None: return util.get_error_template("Error", "Invalid user or invalid post", "/", "Return")
    if user["username"] != post_data["owner"]: return util.get_error_template("Error", "You don't own this post", "/", "Return")

    if control == "edit":
        return flask.render_template("newpost.html", username=user["username"], title=post_data["title"], body=post_data["body"], post_id=post_data["id"])
    elif control == "delete":
        db.delete_post(post)
        return flask.redirect("/", 301)

@app.route("/newpost")
def new_post():
    user = db.get_user_by_request()
    if not user: return flask.redirect("/", 301)
    return flask.render_template("newpost.html", username=user["username"], title="", body="", post_id=-1)

@app.route("/editpost/<post>", methods=["post"])
def edit_post(post):
    user = db.get_user_by_request()
    post_data = db.get_post_by_id(post)
    if user is None or post_data is None: return util.get_error_template("Error", "Invalid user or invalid post", "/", "Return")
    if user["username"] != post_data["owner"]: return util.get_error_template("Error", "You don't own this post", "/", "Return")
    success, message = db.edit_post_by_request(post)
    if success:
        return flask.redirect(f"/posts/{post}", 301)
    return util.get_error_template("Error", message, "/newpost", "Return")


@app.route("/account")
def account_settings():
    user = db.get_user_by_request()
    if not user: return flask.redirect("/", 301)
    return flask.render_template("account.html", username=user["username"], tokens=db.get_user_tokens(user["username"]), active_token=flask.request.cookies.get("token"))

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

@app.route("/deletetoken/<token>")
def deletetoken(token):
    user = db.get_user_by_request()
    if not user: return flask.redirect("/", 301)
    db.delete_token(user["username"], token)
    return flask.redirect("/account", 301)

@app.route("/deletealltokens")
def deletealltokens():
    user = db.get_user_by_request()
    if not user: return flask.redirect("/", 301)
    db.delete_all_tokens(user["username"])
    return flask.redirect("/", 301)

if __name__ == "__main__":
    app.run("0.0.0.0", 8080)
    db.close()