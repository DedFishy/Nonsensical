import flask
from db import Database
import util
from const import DEBUG_MODE

app = flask.Flask(__name__)
db = Database()

if DEBUG_MODE: app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.route("/")
def index():
    if util.get_is_logged_in():
        pass
    else:
        return flask.render_template("login.html")

if __name__ == "__main__":
    app.run("0.0.0.0", 8080)