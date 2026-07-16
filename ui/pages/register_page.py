from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QSpacerItem, QSizePolicy, QProgressBar,
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont

from inventory.services.auth_service import AuthService
from inventory.exceptions import ValidationError, DatabaseConnectionError


class RegisterPage(QWidget):
    registration_successful = Signal()
    switch_to_login = Signal()

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.auth_service = AuthService(db)
        self._setup_ui()

    def _setup_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setAlignment(Qt.AlignCenter)

        scroll_container = QFrame()
        scroll_container.setObjectName("card")
        scroll_container.setFixedWidth(440)
        card_layout = QVBoxLayout(scroll_container)
        card_layout.setContentsMargins(40, 32, 40, 32)
        card_layout.setSpacing(12)

        icon_label = QLabel("📦")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_font = QFont()
        icon_font.setPointSize(40)
        icon_label.setFont(icon_font)
        card_layout.addWidget(icon_label)

        title = QLabel("Create Account")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title)

        subtitle = QLabel("Register a new account to get started")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #888; font-size: 13px; margin-bottom: 4px;")
        card_layout.addWidget(subtitle)

        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet(
            "color: #F44336; font-size: 12px; padding: 4px;"
            "background-color: #FFEBEE; border-radius: 4px;"
        )
        self.error_label.setVisible(False)
        self.error_label.setWordWrap(True)
        card_layout.addWidget(self.error_label)

        self.success_label = QLabel("")
        self.success_label.setAlignment(Qt.AlignCenter)
        self.success_label.setStyleSheet(
            "color: #4CAF50; font-size: 12px; padding: 4px;"
            "background-color: #E8F5E9; border-radius: 4px;"
        )
        self.success_label.setVisible(False)
        self.success_label.setWordWrap(True)
        card_layout.addWidget(self.success_label)

        fields = [
            ("Full Name", "full_name", "Enter your full name", False),
            ("Username *", "username", "Choose a username (3-50 chars)", False),
            ("Email *", "email", "Enter your email address", False),
            ("Password *", "password", "Min 8 chars, 1 uppercase, 1 digit", True),
            ("Confirm Password *", "confirm_password", "Re-enter your password", True),
        ]

        self.inputs = {}
        for label_text, key, placeholder, is_password in fields:
            lbl = QLabel(label_text)
            lbl.setStyleSheet("font-weight: 600; font-size: 12px;")
            card_layout.addWidget(lbl)

            inp = QLineEdit()
            inp.setPlaceholderText(placeholder)
            if is_password:
                inp.setEchoMode(QLineEdit.Password)
            inp.returnPressed.connect(self._on_register)
            card_layout.addWidget(inp)
            self.inputs[key] = inp

        password_strength_label = QLabel("Password Strength")
        password_strength_label.setStyleSheet("font-size: 11px; color: #888;")
        password_strength_label.setVisible(False)
        card_layout.addWidget(password_strength_label)

        self.strength_bar = QProgressBar()
        self.strength_bar.setRange(0, 100)
        self.strength_bar.setValue(0)
        self.strength_bar.setFixedHeight(6)
        self.strength_bar.setTextVisible(False)
        self.strength_bar.setVisible(False)
        card_layout.addWidget(self.strength_bar)

        self.inputs["password"].textChanged.connect(self._update_strength)

        card_layout.addSpacing(8)

        self.register_button = QPushButton("Create Account")
        self.register_button.setCursor(Qt.PointingHandCursor)
        self.register_button.setMinimumHeight(44)
        self.register_button.clicked.connect(self._on_register)
        card_layout.addWidget(self.register_button)

        login_layout = QHBoxLayout()
        login_layout.setAlignment(Qt.AlignCenter)
        login_text = QLabel("Already have an account?")
        login_text.setStyleSheet("color: #888; font-size: 13px;")
        login_layout.addWidget(login_text)

        login_link = QPushButton("Sign In")
        login_link.setCursor(Qt.PointingHandCursor)
        login_link.setFlat(True)
        login_link.setStyleSheet(
            "color: #1A73E8; font-weight: 600; font-size: 13px;"
            "background: transparent; text-decoration: underline;"
        )
        login_link.clicked.connect(self.switch_to_login.emit)
        login_layout.addWidget(login_link)
        card_layout.addLayout(login_layout)

        outer_layout.addWidget(scroll_container)

    def _update_strength(self, text):
        if not text:
            self.strength_bar.setVisible(False)
            return
        self.strength_bar.setVisible(True)

        score = 0
        if len(text) >= 8:
            score += 25
        if any(c.isupper() for c in text):
            score += 25
        if any(c.islower() for c in text):
            score += 15
        if any(c.isdigit() for c in text):
            score += 20
        if any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?`~" for c in text):
            score += 15

        self.strength_bar.setValue(score)
        if score < 30:
            self.strength_bar.setStyleSheet(
                "QProgressBar::chunk { background-color: #F44336; border-radius: 3px; }"
            )
        elif score < 60:
            self.strength_bar.setStyleSheet(
                "QProgressBar::chunk { background-color: #FF9800; border-radius: 3px; }"
            )
        elif score < 85:
            self.strength_bar.setStyleSheet(
                "QProgressBar::chunk { background-color: #4CAF50; border-radius: 3px; }"
            )
        else:
            self.strength_bar.setStyleSheet(
                "QProgressBar::chunk { background-color: #2196F3; border-radius: 3px; }"
            )

    def _show_error(self, message):
        self.success_label.setVisible(False)
        self.error_label.setText(message)
        self.error_label.setVisible(True)
        QTimer.singleShot(5000, lambda: self.error_label.setVisible(False))

    def _show_success(self, message):
        self.error_label.setVisible(False)
        self.success_label.setText(message)
        self.success_label.setVisible(True)

    def _on_register(self):
        username = self.inputs["username"].text().strip()
        email = self.inputs["email"].text().strip()
        password = self.inputs["password"].text()
        confirm = self.inputs["confirm_password"].text()
        full_name = self.inputs["full_name"].text().strip()

        if password != confirm:
            self._show_error("Passwords do not match.")
            return

        if not username or not email or not password:
            self._show_error("Please fill in all required fields (*).")
            return

        self.register_button.setEnabled(False)
        self.register_button.setText("Creating Account...")

        QTimer.singleShot(100, lambda: self._do_register(
            username, email, password, full_name
        ))

    def _do_register(self, username, email, password, full_name):
        try:
            self.auth_service.register(username, email, password, full_name)
            self._show_success(
                "✅ Account created successfully! You can now sign in."
            )
            self.register_button.setText("Success! Redirecting...")
            QTimer.singleShot(2000, self.registration_successful.emit)
        except ValidationError as e:
            self._show_error(str(e))
            if e.field and e.field in self.inputs:
                self.inputs[e.field].setFocus()
        except DatabaseConnectionError as e:
            self._show_error(f"Database error: {e}")
        except Exception as e:
            self._show_error(f"An unexpected error occurred: {e}")
        finally:
            self.register_button.setEnabled(True)
            if self.register_button.text() != "Success! Redirecting...":
                self.register_button.setText("Create Account")

    def reset(self):
        for inp in self.inputs.values():
            inp.clear()
        self.error_label.setVisible(False)
        self.success_label.setVisible(False)
        self.strength_bar.setVisible(False)
        self.strength_bar.setValue(0)
        self.register_button.setEnabled(True)
        self.register_button.setText("Create Account")
