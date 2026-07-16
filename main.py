#!/usr/bin/env python3
import sys
import os
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from inventory.config import APP_CONFIG
from inventory.database import DatabaseManager
from inventory.exceptions import DatabaseConnectionError
from inventory.services.auth_service import AuthService
from ui.theme import theme_manager
from ui.app import MainWindow


def seed_admin(db):
    try:
        auth_service = AuthService(db)
        auth_service.seed_admin()
    except Exception:
        pass


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_CONFIG["title"])
    app.setApplicationVersion(APP_CONFIG["version"])
    app.setOrganizationName(APP_CONFIG["company"])

    theme_manager.apply(app)

    db = DatabaseManager()
    if not db.test_connection():
        result = QMessageBox.critical(
            None,
            "Database Connection Failed",
            "Could not connect to the MySQL database.\n\n"
            f"Host: {db._config.get('host', 'localhost')}\n"
            f"Database: {db._config.get('database', 'inventory_db')}\n\n"
            "Please check your .env file or environment variables.\n\n"
            "Do you want to continue anyway? (Some features will be disabled)",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if result == QMessageBox.No:
            sys.exit(1)

    seed_admin(db)

    window = MainWindow(db)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
