import os
import subprocess
from datetime import datetime
from inventory.exceptions import ValidationError, NotFoundError
from inventory.services.base_service import BaseService


class SettingsService(BaseService):
    def __init__(self, db):
        super().__init__(db, "settings")

    def get_company_settings(self):
        result = self.db.execute_query(
            "SELECT * FROM company_settings WHERE setting_id = 1",
            dictionary=True,
        )
        if not result:
            self.db.execute_update(
                "INSERT INTO company_settings (company_name, currency_symbol, tax_rate) "
                "VALUES ('My Company', '$', 0.00)"
            )
            return self.get_company_settings()
        return result[0]

    def update_company_settings(self, company_name, address="", phone="", email="",
                                 tax_id="", currency_symbol="$", tax_rate=0.0, logo_path=""):
        self.db.execute_update(
            """UPDATE company_settings SET company_name=%s, address=%s, phone=%s, email=%s,
               tax_id=%s, currency_symbol=%s, tax_rate=%s, logo_path=%s WHERE setting_id=1""",
            (company_name, address, phone, email, tax_id, currency_symbol, tax_rate, logo_path),
        )
        self._log("update_company_settings", None, {"company_name": company_name})

    def backup_database(self, filepath):
        config = self.db._config
        try:
            cmd = [
                "mysqldump",
                f"--host={config['host']}",
                f"--port={config['port']}",
                f"--user={config['user']}",
                f"--password={config['password']}",
                config["database"],
            ]
            with open(filepath, "w") as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"mysqldump failed: {result.stderr}")

            file_size = os.path.getsize(filepath)
            self._log("backup", None, {"file_size": file_size, "filepath": filepath})
            return file_size
        except FileNotFoundError:
            raise RuntimeError(
                "mysqldump not found. Ensure MySQL tools are installed and in PATH."
            )

    def restore_database(self, filepath):
        if not os.path.exists(filepath):
            raise ValidationError(f"Backup file not found: {filepath}")

        config = self.db._config
        try:
            cmd = [
                "mysql",
                f"--host={config['host']}",
                f"--port={config['port']}",
                f"--user={config['user']}",
                f"--password={config['password']}",
                config["database"],
            ]
            with open(filepath, "r") as f:
                result = subprocess.run(cmd, stdin=f, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"mysql restore failed: {result.stderr}")
            self._log("restore", None, {"filepath": filepath})
        except FileNotFoundError:
            raise RuntimeError("mysql client not found. Ensure MySQL tools are installed.")

    def log_backup(self, user_id, filepath, file_size):
        self.db.execute_update(
            "INSERT INTO backup_log (user_id, file_path, file_size) VALUES (%s, %s, %s)",
            (user_id, filepath, file_size),
        )

    def get_backup_history(self):
        return self.db.execute_query(
            """SELECT b.*, u.username
               FROM backup_log b
               JOIN users u ON b.user_id = u.user_id
               ORDER BY b.created_at DESC LIMIT 20""",
            dictionary=True,
        )
