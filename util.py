from flask import request, render_template

def get_is_logged_in():
    return "token" in request.cookies.keys()

def get_error_template(header, text, link, link_text):
    return render_template("error.html", error_header=header, error_message=text, error_link=link, error_link_text=link_text)