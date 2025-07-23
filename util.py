from flask import request

def get_is_logged_in():
    return "token" in request.cookies.keys()