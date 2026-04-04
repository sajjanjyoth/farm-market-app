import mysql.connector
from config import DB_CONFIG

# 🔌 CONNECT DB
def get_db():
    return mysql.connector.connect(**DB_CONFIG)

# ✅ ADD THIS (IMPORTANT FIX)
def get_cursor():
    db = get_db()
    return db.cursor(dictionary=True), db