import sqlite3
from const import DEBUG_MODE, POSTS_PER_PAGE
from flask import request
from datetime import datetime
import cryptography

def construct_user(row):
    return {
        "username": row[0],
        "password": row[1],
        "creation": row[2]
    }

def construct_post(row):
    return {
        "id": row[0],
        "title": row[1],
        "body": row[2],
        "owner": row[3],
        "creation": row[4]
    }

class Database:
    connection = sqlite3.connect("staging.db" if DEBUG_MODE else "production.db", check_same_thread=False)
    cursor = connection.cursor()

    def __init__(self):
        # Construct tables
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (username text primary key, password blob, creation timestamp)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS tokens (token text primary key, username text, creation timestamp)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS posts (id integer primary key, title text, body text, owner text, creation timestamp)")
        self.connection.commit()
    
    def create_user(self, username, password_raw=None, password_hashed=None):
        if self.get_user_by_username(username) is None:
            self.cursor.execute("INSERT INTO users (username, password, creation) VALUES (:username, :password, :creation)", {
                "username": username, 
                "password": password_hashed if password_hashed is not None else cryptography.hash_password(password_raw),
                "creation": datetime.now()})
            self.connection.commit()
            return True, ""
        return False, f"The username \"{username}\" is taken."
    
    def create_token(self, username):
        if self.get_user_by_username(username) is not None:
            token = cryptography.generate_token()
            self.cursor.execute("INSERT INTO tokens (token, username, creation) VALUES (:token, :username, :creation)", {
                "token": token,
                "username": username,
                "creation": datetime.now()
            })
            self.connection.commit()
            return token
        return False

    def create_post(self, title, body, owner):
        if self.get_user_by_username(owner) is not None:
            self.cursor.execute("INSERT INTO posts (title, body, owner, creation) VALUES (:title, :body, :owner, :creation) RETURNING id", {
                "title": title,
                "body": body,
                "owner": owner,
                "creation": datetime.now()
            })
            self.connection.commit()
            return self.cursor.fetchone()
        return False

    def get_user_by_username(self, username):
        self.cursor.execute("SELECT * FROM users WHERE username IS :username", {"username": username})
        row = self.cursor.fetchone()
        if row is not None:
            return construct_user(row)
        return None
    
    def get_user_by_token(self, token):
        self.cursor.execute("SELECT * FROM tokens WHERE token IS :token", {"token": token})
        row = self.cursor.fetchone()
        if row is not None:
            return construct_user(row)
        return None
    
    def get_user_by_request(self):
        return self.get_user_by_token(request.cookies.get("token"))
    
    def get_posts_by_request(self):
        page = request.args["page"]
        start_time = request.args["startTime"]

        self.cursor.execute("SELECT * FROM posts WHERE creation < :starttime ORDER BY creation DESC LIMIT :limit OFFSET :offset", {
            "starttime": datetime.fromtimestamp(int(start_time)),
            "limit": POSTS_PER_PAGE,
            "offset": page * POSTS_PER_PAGE})
        
        return [construct_post(row) for row in self.cursor.fetchall()]
    
    def get_post_by_id(self, post_id):
        self.cursor.execute("SELECT * FROM posts WHERE id IS :id", {"id": post_id})
        return construct_post(self.cursor.fetchone())

    def login_or_signup_by_request(self) -> tuple[bool, str]:
        form = request.form
        if form["action"] == "Log In":
            pass
        else:
            success, result = self.create_user(form["username"], form["password"])
            if success:
                return True, self.create_token(form["username"])
            else:
                return False, result

    def close(self):
        self.connection.close()