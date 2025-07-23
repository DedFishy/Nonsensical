import sqlite3
from const import DEBUG_MODE
from flask import request
from datetime import datetime
import cryptography

def construct_user(row):
    return {
        "username": row[0],
        "password": row[1],
        "creation": row[2]
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
            return self.cursor.fetchone()
        return False

    def get_user_by_username(self, username):
        self.cursor.execute("SELECT * FROM users WHERE username IS :username", {"username": username})
        row = self.cursor.fetchone()
        if row is not None:
            return construct_user(row)
        return None
    
    def get_user_by_request(self):
        pass

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