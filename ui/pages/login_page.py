from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QSpacerItem, QSizePolicy,
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, Signal
from PySide6.QtGui import QFont

from inventory.services.auth_service import AuthService
from inventory.exceptions import AuthenticationError, DatabaseConnectionError


class LoginPage(QWidget):
    login_successful = Signal(dict)
    switch_to_register = Signal()

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.auth_service = AuthService(db)
        self._setup_ui()

    def _setup_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("card")
        card.setFixedWidth(420)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(16)

        icon_label = QLabel("📦")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_font = QFont()
        icon_font.setPointSize(48)
        icon_label.setFont(icon_font)
        card_layout.addWidget(icon_label)

        title = QLabel("Inventory Management System")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title)

        subtitle = QLabel("Sign in to your account")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #888; font-size: 14px; margin-bottom: 8px;")
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

        card_layout.addSpacing(8)

        username_label = QLabel("Username or Email")
        username_label.setStyleSheet("font-weight: 600; font-size: 13px;")
        card_layout.addWidget(username_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username or email")
        self.username_input.returnPressed.connect(self._on_login)
        card_layout.addWidget(self.username_input)

        password_label = QLabel("Password")
        password_label.setStyleSheet("font-weight: 600; font-size: 13px;")
        card_layout.addWidget(password_label)

        password_layout = QHBoxLayout()
        password_layout.setContentsMargins(0, 0, 0, 0)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.returnPressed.connect(self._on_login)
        password_layout.addWidget(self.password_input)

        self.toggle_btn = QPushButton("👁")
        self.toggle_btn.setFixedWidth(40)
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.clicked.connect(self._toggle_password)
        self.toggle_btn.setStyleSheet("background: transparent; font-size: 16px; padding: 4px;")
        password_layout.addWidget(self.toggle_btn)
        card_layout.addLayout(password_layout)

        card_layout.addSpacing(8)

        self.login_button = QPushButton("Sign In")
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.setMinimumHeight(44)
        self.login_button.clicked.connect(self._on_login)
        card_layout.addWidget(self.login_button)

        register_layout = QHBoxLayout()
        register_layout.setAlignment(Qt.AlignCenter)
        register_text = QLabel("Don't have an account?")
        register_text.setStyleSheet("color: #888; font-size: 13px;")
        register_layout.addWidget(register_text)

        register_link = QPushButton("Sign Up")
        register_link.setCursor(Qt.PointingHandCursor)
        register_link.setFlat(True)
        register_link.setStyleSheet(
            "color: #1A73E8; font-weight: 600; font-size: 13px;"
            "background: transparent; text-decoration: underline;"
        )
        register_link.clicked.connect(self.switch_to_register.emit)
        register_layout.addWidget(register_link)
        card_layout.addLayout(register_layout)

        outer_layout.addWidget(card)

    def _toggle_password(self):
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_btn.setText("🙈")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_btn.setText("👁")

    def _show_error(self, message):
        self.error_label.setText(message)
        self.error_label.setVisible(True)
        QTimer.singleShot(5000, lambda: self.error_label.setVisible(False))

    def _on_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            self._show_error("Please enter both username and password.")
            return

        self.login_button.setEnabled(False)
        self.login_button.setText("Signing in...")

        QTimer.singleShot(100, self._do_login)

    def _do_login(self):
        try:
            username = self.username_input.text().strip()
            password = self.password_input.text()
            user = self.auth_service.authenticate(username, password)
            self.login_successful.emit({
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
            })
        except (AuthenticationError, DatabaseConnectionError) as e:
            self._show_error(str(e))
        except Exception as e:
            self._show_error(f"An unexpected error occurred: {e}")
        finally:
            self.login_button.setEnabled(True)
            self.login_button.setText("Sign In")
            self.password_input.clear()

    def reset(self):
        self.username_input.clear()
        self.password_input.clear()
        self.error_label.setVisible(False)
        self.login_button.setEnabled(True)
        self.login_button.setText("Sign In")
