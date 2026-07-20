from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTabWidget, QFrame, QLineEdit, QDoubleSpinBox, QSpinBox,
    QComboBox, QMessageBox, QFileDialog, QTextEdit, QFormLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
    QCheckBox, QDialog,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from inventory.services.user_service import UserService
from inventory.services.settings_service import SettingsService
from inventory.services.activity_service import ActivityService
from inventory.session import session_manager
from inventory.exceptions import ValidationError, AuthenticationError
from ui.dialogs.form_dialog import FormDialog, FormField


class UsersTab(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.service = UserService(db)
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        toolbar = QHBoxLayout()
        title = QLabel("User Management")
        title.setObjectName("sectionTitle")
        toolbar.addWidget(title)
        toolbar.addStretch()
        self.add_user_btn = QPushButton("+ Add User")
        self.add_user_btn.setCursor(Qt.PointingHandCursor)
        self.add_user_btn.clicked.connect(self._add_user)
        toolbar.addWidget(self.add_user_btn)
        layout.addLayout(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Username", "Email", "Full Name", "Role", "Active"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.doubleClicked.connect(self._edit_user)
        layout.addWidget(self.table)

    def refresh(self):
        try:
            users = self.service.get_all()
            self.table.setRowCount(len(users))
            for i, u in enumerate(users):
                self.table.setItem(i, 0, QTableWidgetItem(str(u["user_id"])))
                self.table.setItem(i, 1, QTableWidgetItem(u["username"]))
                self.table.setItem(i, 2, QTableWidgetItem(u.get("email", "")))
                self.table.setItem(i, 3, QTableWidgetItem(u.get("full_name", "")))
                self.table.setItem(i, 4, QTableWidgetItem(u["role"]))
                active = QTableWidgetItem("Yes" if u.get("is_active") else "No")
                active.setForeground(Qt.green if u.get("is_active") else Qt.red)
                self.table.setItem(i, 5, active)
        except Exception:
            pass

    def _add_user(self):
        fields = [
            FormField("username", "Username", "text", required=True, max_length=50),
            FormField("email", "Email", "text", required=True),
            FormField("password", "Password", "password", required=True),
            FormField("full_name", "Full Name", "text"),
            FormField("role", "Role", "combobox", items=[("admin", "Admin"), ("manager", "Manager"), ("staff", "Staff")]),
        ]
        dialog = FormDialog("Add User", fields, parent=self)
        if dialog.exec() == FormDialog.Accepted:
            data = dialog.get_data()
            try:
                self.service.create(**data)
                self.refresh()
                QMessageBox.information(self, "Success", "User added successfully!")
            except ValidationError as e:
                QMessageBox.warning(self, "Error", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add user: {e}")

    def _edit_user(self, index):
        row = index.row()
        user_id = int(self.table.item(row, 0).text())
        username = self.table.item(row, 1).text()

        if username == "admin":
            QMessageBox.information(self, "Info", "The admin account can be managed via the Profile tab.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Edit User: {username}")
        dialog.setMinimumWidth(400)
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        form = QFormLayout()
        role_combo = QComboBox()
        role_combo.addItems(["admin", "manager", "staff"])
        role_combo.setCurrentText(self.table.item(row, 4).text())
        form.addRow("Role:", role_combo)

        active_check = QCheckBox()
        active_check.setChecked(self.table.item(row, 5).text() == "Yes")
        form.addRow("Active:", active_check)

        layout.addLayout(form)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        reset_pwd_btn = QPushButton("Reset Password")
        reset_pwd_btn.clicked.connect(lambda: self._reset_password(user_id))
        btn_row.addWidget(reset_pwd_btn)

        delete_btn = QPushButton("Delete User")
        delete_btn.setStyleSheet("background-color: #F44336;")
        delete_btn.clicked.connect(lambda: self._delete_user(user_id))
        btn_row.addWidget(delete_btn)

        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(lambda: self._save_user(dialog, user_id, role_combo, active_check))
        btn_row.addWidget(save_btn)

        layout.addLayout(btn_row)
        dialog.exec()

    def _save_user(self, dialog, user_id, role_combo, active_check):
        try:
            self.service.update(
                user_id,
                role=role_combo.currentText(),
                is_active=active_check.isChecked(),
            )
            self.refresh()
            QMessageBox.information(dialog, "Success", "User updated!")
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(dialog, "Error", str(e))

    def _reset_password(self, user_id):
        from PySide6.QtWidgets import QInputDialog
        pwd, ok = QInputDialog.getText(self, "Reset Password", "New password:", echo=QLineEdit.Password)
        if ok and pwd:
            try:
                self.service.reset_password(user_id, pwd)
                QMessageBox.information(self, "Success", "Password reset successfully!")
            except ValidationError as e:
                QMessageBox.warning(self, "Error", str(e))

    def _delete_user(self, user_id):
        reply = QMessageBox.question(
            self, "Confirm Delete", "Delete this user? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            try:
                self.service.delete(user_id)
                self.refresh()
                QMessageBox.information(self, "Success", "User deleted.")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))


class CompanyTab(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.service = SettingsService(db)
        self._setup_ui()
        self._load()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        title = QLabel("Company Settings")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        form_frame = QFrame()
        form_frame.setObjectName("card")
        form = QFormLayout(form_frame)
        form.setSpacing(12)
        form.setContentsMargins(20, 20, 20, 20)

        self.name_input = QLineEdit()
        form.addRow("Company Name:", self.name_input)

        self.address_input = QTextEdit()
        self.address_input.setMaximumHeight(60)
        form.addRow("Address:", self.address_input)

        self.phone_input = QLineEdit()
        form.addRow("Phone:", self.phone_input)

        self.email_input = QLineEdit()
        form.addRow("Email:", self.email_input)

        self.tax_id_input = QLineEdit()
        form.addRow("Tax ID:", self.tax_id_input)

        self.currency_input = QLineEdit()
        self.currency_input.setMaxLength(5)
        self.currency_input.setFixedWidth(60)
        form.addRow("Currency Symbol:", self.currency_input)

        self.tax_rate_input = QDoubleSpinBox()
        self.tax_rate_input.setRange(0, 100)
        self.tax_rate_input.setDecimals(2)
        self.tax_rate_input.setSuffix(" %")
        form.addRow("Default Tax Rate:", self.tax_rate_input)

        layout.addWidget(form_frame)

        self.save_btn = QPushButton("Save Settings")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.setFixedWidth(200)
        self.save_btn.clicked.connect(self._save)
        layout.addWidget(self.save_btn)

        layout.addStretch()

    def _load(self):
        try:
            settings = self.service.get_company_settings()
            self.name_input.setText(settings.get("company_name", ""))
            self.address_input.setPlainText(settings.get("address", ""))
            self.phone_input.setText(settings.get("phone", ""))
            self.email_input.setText(settings.get("email", ""))
            self.tax_id_input.setText(settings.get("tax_id", ""))
            self.currency_input.setText(settings.get("currency_symbol", "$"))
            self.tax_rate_input.setValue(float(settings.get("tax_rate", 0) or 0))
        except Exception:
            pass

    def _save(self):
        try:
            self.service.update_company_settings(
                company_name=self.name_input.text(),
                address=self.address_input.toPlainText(),
                phone=self.phone_input.text(),
                email=self.email_input.text(),
                tax_id=self.tax_id_input.text(),
                currency_symbol=self.currency_input.text(),
                tax_rate=self.tax_rate_input.value(),
            )
            QMessageBox.information(self, "Success", "Company settings saved!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {e}")


class BackupTab(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.service = SettingsService(db)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        title = QLabel("Database Backup & Restore")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        backup_frame = QFrame()
        backup_frame.setObjectName("card")
        backup_layout = QVBoxLayout(backup_frame)
        backup_layout.setSpacing(12)
        backup_layout.setContentsMargins(20, 20, 20, 20)

        backup_label = QLabel(
            "Create a complete backup of the database.\n"
            "This uses mysqldump and saves a .sql file."
        )
        backup_label.setWordWrap(True)
        backup_layout.addWidget(backup_label)

        btn_row = QHBoxLayout()
        self.backup_btn = QPushButton("Create Backup")
        self.backup_btn.setCursor(Qt.PointingHandCursor)
        self.backup_btn.clicked.connect(self._backup)
        btn_row.addWidget(self.backup_btn)

        self.restore_btn = QPushButton("Restore from Backup")
        self.restore_btn.setCursor(Qt.PointingHandCursor)
        self.restore_btn.setStyleSheet("background-color: #FF9800;")
        self.restore_btn.clicked.connect(self._restore)
        btn_row.addWidget(self.restore_btn)

        btn_row.addStretch()
        backup_layout.addLayout(btn_row)
        layout.addWidget(backup_frame)

        history_frame = QFrame()
        history_frame.setObjectName("card")
        history_layout = QVBoxLayout(history_frame)
        history_layout.setSpacing(8)
        history_layout.setContentsMargins(20, 20, 20, 20)

        history_label = QLabel("Recent Backups")
        history_label.setStyleSheet("font-weight: 600;")
        history_layout.addWidget(history_label)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["Date", "User", "Size", "File"])
        self.history_table.horizontalHeader().setStretchLastSection(True)
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.setAlternatingRowColors(True)
        history_layout.addWidget(self.history_table)

        layout.addWidget(history_frame)

        self._load_history()

    def _backup(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save Backup",
            f"inventory_backup_{QDate.currentDate().toString('yyyyMMdd')}.sql",
            "SQL Files (*.sql)",
        )
        if filepath:
            try:
                file_size = self.service.backup_database(filepath)
                if session_manager.is_authenticated:
                    self.service.log_backup(
                        session_manager.current_user.user_id, filepath, file_size
                    )
                size_mb = file_size / (1024 * 1024)
                QMessageBox.information(
                    self, "Success",
                    f"Backup created successfully!\n"
                    f"Size: {size_mb:.2f} MB\n"
                    f"Location: {filepath}",
                )
                self._load_history()
            except Exception as e:
                QMessageBox.critical(self, "Backup Failed", str(e))

    def _restore(self):
        from PySide6.QtCore import QDate
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Select Backup File", "", "SQL Files (*.sql)"
        )
        if filepath:
            reply = QMessageBox.warning(
                self, "Confirm Restore",
                "RESTORING WILL OVERWRITE ALL DATA!\n\n"
                "All current data in the database will be replaced "
                "with the backup data.\n\n"
                "This cannot be undone. Continue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                try:
                    self.service.restore_database(filepath)
                    QMessageBox.information(self, "Success", "Database restored successfully!")
                except Exception as e:
                    QMessageBox.critical(self, "Restore Failed", str(e))

    def _load_history(self):
        try:
            backups = self.service.get_backup_history()
            self.history_table.setRowCount(len(backups))
            for i, b in enumerate(backups):
                self.history_table.setItem(i, 0, QTableWidgetItem(str(b.get("created_at", ""))))
                self.history_table.setItem(i, 1, QTableWidgetItem(b.get("username", "")))
                size_mb = int(b.get("file_size", 0)) / (1024 * 1024)
                self.history_table.setItem(i, 2, QTableWidgetItem(f"{size_mb:.1f} MB"))
                self.history_table.setItem(i, 3, QTableWidgetItem(b.get("file_path", "")))
        except Exception:
            pass


class ProfileTab(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.service = UserService(db)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        title = QLabel("My Profile")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        info_frame = QFrame()
        info_frame.setObjectName("card")
        info_form = QFormLayout(info_frame)
        info_form.setSpacing(12)
        info_form.setContentsMargins(20, 20, 20, 20)

        if session_manager.is_authenticated:
            user = session_manager.current_user
            info_form.addRow("Username:", QLabel(f"<b>{user.username}</b>"))
            info_form.addRow("Email:", QLabel(user.email))
            info_form.addRow("Full Name:", QLabel(user.full_name or "-"))
            info_form.addRow("Role:", QLabel(f"<b>{user.role.title()}</b>"))
        else:
            info_form.addRow("Status:", QLabel("Not logged in"))

        layout.addWidget(info_frame)

        pwd_frame = QGroupBox("Change Password")
        pwd_frame.setObjectName("card")
        pwd_form = QFormLayout(pwd_frame)
        pwd_form.setSpacing(12)
        pwd_form.setContentsMargins(20, 20, 20, 20)

        self.current_pwd = QLineEdit()
        self.current_pwd.setEchoMode(QLineEdit.Password)
        pwd_form.addRow("Current Password:", self.current_pwd)

        self.new_pwd = QLineEdit()
        self.new_pwd.setEchoMode(QLineEdit.Password)
        pwd_form.addRow("New Password:", self.new_pwd)

        self.confirm_pwd = QLineEdit()
        self.confirm_pwd.setEchoMode(QLineEdit.Password)
        pwd_form.addRow("Confirm New:", self.confirm_pwd)

        self.change_pwd_btn = QPushButton("Change Password")
        self.change_pwd_btn.setCursor(Qt.PointingHandCursor)
        self.change_pwd_btn.clicked.connect(self._change_password)
        pwd_form.addRow("", self.change_pwd_btn)

        layout.addWidget(pwd_frame)
        layout.addStretch()

    def _change_password(self):
        if not session_manager.is_authenticated:
            QMessageBox.warning(self, "Auth Required", "Please sign in first.")
            return

        current = self.current_pwd.text()
        new = self.new_pwd.text()
        confirm = self.confirm_pwd.text()

        if not current or not new:
            QMessageBox.warning(self, "Validation", "Please fill in all password fields.")
            return
        if new != confirm:
            QMessageBox.warning(self, "Validation", "New passwords do not match.")
            return
        if len(new) < 8:
            QMessageBox.warning(self, "Validation", "New password must be at least 8 characters.")
            return

        try:
            self.service.change_own_password(
                session_manager.current_user.user_id, current, new
            )
            QMessageBox.information(self, "Success", "Password changed successfully!")
            self.current_pwd.clear()
            self.new_pwd.clear()
            self.confirm_pwd.clear()
        except AuthenticationError as e:
            QMessageBox.warning(self, "Error", str(e))
        except ValidationError as e:
            QMessageBox.warning(self, "Validation", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to change password: {e}")


class SettingsPage(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Settings")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        self.users_tab = UsersTab(self.db)
        self.tabs.addTab(self.users_tab, "Users")

        self.company_tab = CompanyTab(self.db)
        self.tabs.addTab(self.company_tab, "Company")

        self.backup_tab = BackupTab(self.db)
        self.tabs.addTab(self.backup_tab, "Backup")

        self.profile_tab = ProfileTab(self.db)
        self.tabs.addTab(self.profile_tab, "Profile")

        layout.addWidget(self.tabs)
