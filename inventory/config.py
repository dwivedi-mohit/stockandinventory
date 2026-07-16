import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST") or os.getenv("MYSQLHOST") or "localhost",
    "port": int(os.getenv("DB_PORT") or os.getenv("MYSQLPORT") or "3306"),
    "user": os.getenv("DB_USER") or os.getenv("MYSQLUSER") or "root",
    "password": os.getenv("DB_PASSWORD") or os.getenv("MYSQLPASSWORD") or "",
    "database": os.getenv("DB_NAME") or os.getenv("MYSQLDATABASE") or os.getenv("DB_DATABASE") or "inventory_db",
}

APP_CONFIG = {
    "title": os.getenv("APP_TITLE", "Inventory Management System"),
    "company": os.getenv("APP_COMPANY", "Your Company Name"),
    "version": "1.0.0",
}

PASSWORD_HASH_ROUNDS = 12
