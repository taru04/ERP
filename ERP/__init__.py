# __init__.py
from flask import Flask
import sqlite3

DB_PATH = "ERP.db"

def create_app():
    app = Flask(__name__)
    app.secret_key = "taru_erp_secret_key"
    return app

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
