#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nicegui import ui
from inventory.database import DatabaseManager
from inventory.services.auth_service import AuthService

import web.app  # noqa: F401 — register routes

if __name__ in {'__main__', '__mp_main__'}:
    db = DatabaseManager()
    if not db.test_connection():
        print('ERROR: Could not connect to MySQL database.')
        print(f'Host: {db._config.get("host", "localhost")}')
        print(f'Database: {db._config.get("database", "inventory_db")}')
        sys.exit(1)

    print(f'Connected to MySQL: {db._config["host"]}:{db._config["port"]}/{db._config["database"]}')

    auth = AuthService(db)
    try:
        auth.seed_admin()
        print('Admin account ready (admin/admin123)')
    except Exception:
        pass

    port = int(os.getenv('PORT', '8080'))
    print()
    print(f'Starting Invictus web app on port {port}...')
    print()

    ui.run(
        title='Invictus — Inventory Management System',
        favicon='📦',
        dark=False,
        host='0.0.0.0',
        port=port,
        show=False,
        storage_secret=os.getenv('STORAGE_SECRET') or 'invictus-secret-change-in-production',
    )
