import flask
from db import Database
import util
from const import DEBUG_MODE, TOKEN_EXPIRY_TIME

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
    return flask.render_template("post.html", title=post_data["title"], poster=post_data["owner"], body=post_data["body"])
    
@app.route("/header")
def header():
    return flask.render_template("header.html")
@app.route("/footer")
def footer():
    return flask.render_template("footer.html")


if __name__ == "__main__":
    app.run("0.0.0.0", 8080)