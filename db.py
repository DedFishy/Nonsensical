import os
import sqlite3
from const import DEBUG_MODE, MAX_BODY_LENGTH, MAX_TITLE_LENGTH, POSTS_PER_PAGE, UPLOAD_FOLDER
from flask import request
from datetime import datetime
import cryptography
from threading import Lock
from werkzeug.utils import secure_filename

def construct_user(row):
    return {
        "username": row[0],
        "password": row[1],
        "creation": row[2]
    }

def construct_post(row):
    file_path = os.path.join(UPLOAD_FOLDER, str(row[0]))
        
    return {
        "id": row[0],
        "title": row[1],
        "body": row[2],
        "owner": row[3],
        "creation": row[4],
        "files": os.listdir(file_path) if os.path.exists(file_path) else []
    }

class Database:
    connection = sqlite3.connect("staging.db" if DEBUG_MODE else "production.db", check_same_thread=False)
    cursor = connection.cursor()

    db_lock = Lock()

    def __init__(self):
        # Construct tables
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (username text primary key, password blob, creation timestamp)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS tokens (token text primary key, username text, creation timestamp)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS posts (id integer primary key, title text, body text, owner text, creation timestamp)")
        self.connection.commit()
    
    def create_user(self, username, password_raw=None, password_hashed=None):
        if self.get_user_by_username(username) is None:
            self.db_lock.acquire()
            self.cursor.execute("INSERT INTO users (username, password, creation) VALUES (:username, :password, :creation)", {
                "username": username, 
                "password": password_hashed if password_hashed is not None else cryptography.hash_password(password_raw),
                "creation": datetime.now()})
            self.connection.commit()
            self.db_lock.release()
            return True, ""
        return False, f"The username \"{username}\" is taken."
    
    def create_token(self, username):
        if self.get_user_by_username(username) is not None:
            token = cryptography.generate_token()
            self.db_lock.acquire()
            self.cursor.execute("INSERT INTO tokens (token, username, creation) VALUES (:token, :username, :creation)", {
                "token": token,
                "username": username,
                "creation": datetime.now()
            })
            self.connection.commit()
            self.db_lock.release()
            return token
        return False

    def create_post(self, title, body, owner):
        if self.get_user_by_username(owner) is not None:
            self.db_lock.acquire()
            self.cursor.execute("INSERT INTO posts (title, body, owner, creation) VALUES (:title, :body, :owner, :creation) RETURNING id", {
                "title": title,
                "body": body,
                "owner": owner,
                "creation": datetime.now()
            })
            post_id = self.cursor.fetchone()[0]
            self.connection.commit()
            self.db_lock.release()
            return post_id
        return False
    
    def create_post_by_request(self):
        form = request.form
        
        user = self.get_user_by_request()
        if user is None: return False, "Invalid user token"
        if len(form["title"]) > MAX_TITLE_LENGTH: return False, "Title is too long"
        if len(form["body"]) > MAX_BODY_LENGTH: return False, "Body is too long"
        post_id = self.create_post(form["title"], form["body"], user["username"])

        files = request.files.getlist("media")
        print("FILES")
        print(files)
        upload_folder = os.path.join(UPLOAD_FOLDER, str(post_id))
        os.makedirs(upload_folder, exist_ok=True)
        for file in files:
            if file.filename == '': continue
            filename = secure_filename(file.filename)
            file.save(os.path.join(upload_folder, filename))
        return True, post_id

    def get_user_by_username(self, username):
        self.db_lock.acquire()
        self.cursor.execute("SELECT * FROM users WHERE username IS :username", {"username": username})
        row = self.cursor.fetchone()
        self.db_lock.release()
        if row is not None:
            return construct_user(row)
        return None
    
    def get_user_by_token(self, token):
        self.db_lock.acquire()
        self.cursor.execute("SELECT * FROM tokens WHERE token IS :token", {"token": token})
        row = self.cursor.fetchone()
        self.db_lock.release()
        if row is not None:
            return self.get_user_by_username(row[1])
        return None
    
    def get_user_by_request(self):
        return self.get_user_by_token(request.cookies.get("token"))
    
    def get_posts_by_request(self):
        page = int(request.args["page"])
        start_time = request.args["startTime"]
        self.db_lock.acquire()
        print(f"Limit: {POSTS_PER_PAGE}, Offset: {page * POSTS_PER_PAGE}, Start Time: {datetime.fromtimestamp(int(start_time))}")
        self.cursor.execute("SELECT * FROM posts WHERE creation < :starttime ORDER BY creation DESC LIMIT :limit OFFSET :offset", {
            "starttime": datetime.fromtimestamp(int(start_time)),
            "limit": POSTS_PER_PAGE,
            "offset": page * POSTS_PER_PAGE})
        rows = self.cursor.fetchall()
        self.db_lock.release()
        
        return [construct_post(row) for row in rows]
    
    def get_post_by_id(self, post_id):
        self.db_lock.acquire()
        self.cursor.execute("SELECT * FROM posts WHERE id IS :id", {"id": post_id})
        post = self.cursor.fetchone()
        self.db_lock.release()
        return construct_post(post)

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
        self.db_lock.acquire()
        self.connection.close()