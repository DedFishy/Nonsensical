import flask
from db import Database
import util
from const import DEBUG_MODE, TOKEN_EXPIRY_TIME

app = flask.Flask(__name__)
db = Database()

if DEBUG_MODE: app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.route("/")
def index():
    if util.get_is_logged_in():
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
        response = flask.make_response(flask.render_template("list.html"))
        response.set_cookie("token", result, max_age=TOKEN_EXPIRY_TIME)
        return response

if __name__ == "__main__":
    app.run("0.0.0.0", 8080)