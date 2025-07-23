import sqlite3
from const import DEBUG_MODE
from flask import request
import bcrypt
import secrets

def construct_user(row):
    return {
        "username": row[0],
        "password": row[1],
        "creation": row[2]
    }

class Database:
    connection = sqlite3.connect("staging.db" if DEBUG_MODE else "production.db")
    cursor = connection.cursor()

    def __init__(self):
        # Construct tables
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (username text primary key, password text, creation text)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS tokens (token text primary key, username text, creation text)")
        self.connection.commit()

    def get_user_by_username(self, username):
        self.cursor.execute("SELECT * FROM users WHERE username IS :username", {"username": username})
        rows = self.cursor.fetchall()
        if len(rows) > 0:
            return construct_user(rows[0])
        return None
    
    def get_user_by_request(self):
        pass

    def close(self):
        self.connection.close()