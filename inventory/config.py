import os
from urllib.parse import urlparse, unquote


def _load_env(path=".env"):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key, val = key.strip(), val.strip().strip("\"'")
            os.environ.setdefault(key, val)


_load_env()


def _config_from_url(url):
    if not url:
        return None
    parsed = urlparse(url)
    if not parsed.hostname:
        return None
    return {
        "host": parsed.hostname,
        "port": parsed.port or 3306,
        "user": unquote(parsed.username) if parsed.username else "root",
        "password": unquote(parsed.password) if parsed.password else "",
        "database": parsed.path.lstrip("/") or "railway",
    }


def _build_db_config():
    # 1. Railway/managed connection URL (most reliable, single source of truth)
    url_config = _config_from_url(os.getenv("MYSQL_URL") or os.getenv("DATABASE_URL"))
    if url_config:
        return url_config

    # 2. Railway individual MYSQL* variables
    if os.getenv("MYSQLHOST"):
        return {
            "host": os.getenv("MYSQLHOST"),
            "port": int(os.getenv("MYSQLPORT") or "3306"),
            "user": os.getenv("MYSQLUSER") or "root",
            "password": os.getenv("MYSQLPASSWORD") or "",
            "database": os.getenv("MYSQLDATABASE") or "railway",
        }

    # 3. Local dev / generic DB_* variables
    return {
        "host": os.getenv("DB_HOST") or "localhost",
        "port": int(os.getenv("DB_PORT") or "3306"),
        "user": os.getenv("DB_USER") or "root",
        "password": os.getenv("DB_PASSWORD") or "",
        "database": os.getenv("DB_NAME") or os.getenv("DB_DATABASE") or "inventory_db",
    }


DB_CONFIG = _build_db_config()

APP_CONFIG = {
    "title": os.getenv("APP_TITLE", "Inventory Management System"),
    "company": os.getenv("APP_COMPANY", "Your Company Name"),
    "version": "1.0.0",
}

