from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QStatusBar,
    QMenuBar, QMenu, QMessageBox, QFrame, QApplication,
    QSizePolicy, QSpacerItem,
)
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QAction, QFont, QIcon

from inventory.config import APP_CONFIG
from inventory.database import DatabaseManager
from inventory.session import session_manager
from inventory.services.auth_service import AuthService
from ui.theme import theme_manager
from ui.pages.login_page import LoginPage
from ui.pages.dashboard_page import DashboardPage
from ui.pages.products_page import ProductsPage
from ui.pages.suppliers_page import SuppliersPage
from ui.pages.customers_page import CustomersPage
from ui.pages.purchases_page import PurchasesPage
from ui.pages.sales_page import SalesPage
from ui.pages.reports_page import ReportsPage
from ui.pages.activity_log_page import ActivityLogPage
from ui.pages.settings_page import SettingsPage


SIDEBAR_EXPANDED_WIDTH = 240
SIDEBAR_COLLAPSED_WIDTH = 64


class SidebarButton(QPushButton):
    def __init__(self, text, icon_text="", parent=None):
        super().__init__(parent)
        self._full_text = text
        self._icon_text = icon_text
        self.setObjectName("sidebarButton")
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        if icon_text:
            self.setText(f"  {icon_text}  {text}")
        else:
            self.setText(f"    {text}")
        self.setMinimumHeight(44)

    def set_collapsed(self, collapsed: bool):
        if collapsed:
            self.setText(f"  {self._icon_text}  " if self._icon_text else "")
        else:
            if self._icon_text:
                self.setText(f"  {self._icon_text}  {self._full_text}")
            else:
                self.setText(f"    {self._full_text}")


class MainWindow(QMainWindow):
    def __init__(self, db: DatabaseManager):
        super().__init__()
        self.db = db
        self.auth_service = AuthService(db)
        self.sidebar_expanded = True
        self._current_page_index = 0
        self._setup_ui()
        self._setup_menu()
        self._setup_status_bar()
        self._show_auth()

    def _setup_ui(self):
        self.setWindowTitle(APP_CONFIG["title"])
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.root_stack = QStackedWidget(central_widget)
        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(self.root_stack)

        self.auth_stack = QStackedWidget()
        self.login_page = LoginPage(self.db)
        self.auth_stack.addWidget(self.login_page)

        self.main_app = self._build_main_app()

        self.root_stack.addWidget(self.auth_stack)
        self.root_stack.addWidget(self.main_app)

    def _build_main_app(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(SIDEBAR_EXPANDED_WIDTH)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(8, 12, 8, 12)
        sidebar_layout.setSpacing(4)

        logo_label = QLabel("IMS")
        logo_label.setObjectName("titleLabel")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setMinimumHeight(50)
        sidebar_layout.addWidget(logo_label)
        sidebar_layout.addSpacing(16)

        self.sidebar_buttons = []
        nav_items = [
            ("Dashboard", ""),
            ("Products", ""),
            ("Suppliers", ""),
            ("Customers", ""),
            ("Purchases", ""),
            ("Sales", ""),
            ("Reports", ""),
            ("Activity Log", ""),
            ("Settings", ""),
        ]

        for text, icon in nav_items:
            btn = SidebarButton(text, icon)
            btn.clicked.connect(lambda checked, t=text: self._on_navigate(t))
            sidebar_layout.addWidget(btn)
            self.sidebar_buttons.append(btn)

        sidebar_layout.addStretch()

        self.user_frame = QFrame()
        self.user_frame.setObjectName("card")
        user_layout = QVBoxLayout(self.user_frame)
        user_layout.setContentsMargins(8, 8, 8, 8)

        self.user_label = QLabel("Not logged in")
        self.user_label.setAlignment(Qt.AlignCenter)
        self.user_label.setWordWrap(True)
        user_layout.addWidget(self.user_label)

        self.logout_btn = QPushButton("Sign Out")
        self.logout_btn.setObjectName("sidebarButton")
        self.logout_btn.setMinimumHeight(36)
        self.logout_btn.clicked.connect(self._on_logout)
        user_layout.addWidget(self.logout_btn)

        sidebar_layout.addWidget(self.user_frame)

        layout.addWidget(self.sidebar)

        self.content_stack = QStackedWidget()
        layout.addWidget(self.content_stack, 1)

        self._setup_real_pages()

        return widget

    def _setup_real_pages(self):
        self.dashboard_page = DashboardPage(self.db)
        self.products_page = ProductsPage(self.db)
        self.suppliers_page = SuppliersPage(self.db)
        self.customers_page = CustomersPage(self.db)
        self.purchases_page = PurchasesPage(self.db)
        self.sales_page = SalesPage(self.db)
        self.reports_page = ReportsPage(self.db)
        self.activity_log_page = ActivityLogPage(self.db)
        self.settings_page = SettingsPage(self.db)

        self.content_stack.addWidget(self.dashboard_page)
        self.content_stack.addWidget(self.products_page)
        self.content_stack.addWidget(self.suppliers_page)
        self.content_stack.addWidget(self.customers_page)
        self.content_stack.addWidget(self.purchases_page)
        self.content_stack.addWidget(self.sales_page)
        self.content_stack.addWidget(self.reports_page)
        self.content_stack.addWidget(self.activity_log_page)
        self.content_stack.addWidget(self.settings_page)

    def _setup_menu(self):
        self.menubar = self.menuBar()

        file_menu = self.menubar.addMenu("File")
        self.exit_action = QAction("Exit", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.triggered.connect(self.close)
        file_menu.addAction(self.exit_action)

        view_menu = self.menubar.addMenu("View")
        self.toggle_sidebar_action = QAction("Toggle Sidebar", self)
        self.toggle_sidebar_action.setShortcut("Ctrl+B")
        self.toggle_sidebar_action.triggered.connect(self._toggle_sidebar)
        view_menu.addAction(self.toggle_sidebar_action)

        self.toggle_theme_action = QAction("Toggle Theme", self)
        self.toggle_theme_action.setShortcut("Ctrl+T")
        self.toggle_theme_action.triggered.connect(self._toggle_theme)
        view_menu.addAction(self.toggle_theme_action)

        help_menu = self.menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

        self.logout_action = QAction("Sign Out", self)
        self.logout_action.setShortcut("Ctrl+Shift+Q")
        self.logout_action.triggered.connect(self._on_logout)
        file_menu.addAction(self.logout_action)

        self.menubar.setVisible(False)

    def _setup_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("Ready")
        self.db_status_label = QLabel("")
        self.status_bar.addWidget(self.status_label, 1)
        self.status_bar.addPermanentWidget(self.db_status_label)
        self.status_bar.setVisible(False)

        self._update_db_status()

    def _update_db_status(self):
        connected = self.db.test_connection()
        if connected:
            self.db_status_label.setText("● Database Connected")
            self.db_status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        else:
            self.db_status_label.setText("● Database Disconnected")
            self.db_status_label.setStyleSheet("color: #F44336; font-weight: bold;")

    def _show_auth(self):
        self.root_stack.setCurrentIndex(0)
        self.auth_stack.setCurrentIndex(0)
        self.menubar.setVisible(False)
        self.status_bar.setVisible(False)

        self.login_page.login_successful.connect(self._on_login_success)

        self.auth_stack.currentChanged.connect(self._on_auth_page_changed)

    def _on_auth_page_changed(self, index):
        if index == 0:
            self.login_page.reset()

    def _on_login_success(self, user_data):
        self.root_stack.setCurrentIndex(1)
        self.menubar.setVisible(True)
        self.status_bar.setVisible(True)

        user_name = user_data.get("full_name") or user_data.get("username", "")
        role = user_data.get("role", "").title()
        self.user_label.setText(f"{user_name}\n{role}")
        self.status_label.setText(f"Welcome, {user_name}")

        self._apply_rbac(user_data.get("role", "staff"))
        self.content_stack.setCurrentIndex(0)
        if self.sidebar_buttons:
            self.sidebar_buttons[0].setChecked(True)

    def _apply_rbac(self, role):
        is_admin = role == "admin"
        show_advanced = role in ("admin", "manager")
        for i, btn in enumerate(self.sidebar_buttons):
            label = btn._full_text
            if label in ("Activity Log", "Settings"):
                btn.setVisible(is_admin)
            elif label in ("Reports",):
                btn.setVisible(show_advanced)
            else:
                btn.setVisible(True)
        self.settings_page.setVisible(is_admin)

    def _on_logout(self):
        reply = QMessageBox.question(
            self, "Sign Out",
            "Are you sure you want to sign out?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            session_manager.logout()
            self.root_stack.setCurrentIndex(0)
            self.auth_stack.setCurrentIndex(0)
            self.menubar.setVisible(False)
            self.status_bar.setVisible(False)
            self.login_page.reset()
            for btn in self.sidebar_buttons:
                btn.setVisible(True)

    def _on_navigate(self, page_name):
        page_map = {
            "Dashboard": 0, "Products": 1, "Suppliers": 2,
            "Customers": 3, "Purchases": 4, "Sales": 5,
            "Reports": 6, "Activity Log": 7, "Settings": 8,
        }
        index = page_map.get(page_name, 0)

        for i, btn in enumerate(self.sidebar_buttons):
            btn.setChecked(i == index)

        self.content_stack.setCurrentIndex(index)
        self._current_page_index = index
        self.status_label.setText(f"{page_name}")

    def _toggle_sidebar(self):
        self.sidebar_expanded = not self.sidebar_expanded
        target_width = (
            SIDEBAR_EXPANDED_WIDTH if self.sidebar_expanded else SIDEBAR_COLLAPSED_WIDTH
        )

        self.anim1 = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.anim1.setDuration(200)
        self.anim1.setStartValue(self.sidebar.width())
        self.anim1.setEndValue(target_width)
        self.anim1.setEasingCurve(QEasingCurve.OutCubic)
        self.anim1.finished.connect(self._on_sidebar_animation_done)
        self.anim1.start()

        self.anim2 = QPropertyAnimation(self.sidebar, b"maximumWidth")
        self.anim2.setDuration(200)
        self.anim2.setStartValue(self.sidebar.width())
        self.anim2.setEndValue(target_width)
        self.anim2.setEasingCurve(QEasingCurve.OutCubic)
        self.anim2.start()

        for btn in self.sidebar_buttons:
            btn.set_collapsed(not self.sidebar_expanded)

    def _on_sidebar_animation_done(self):
        self.sidebar.setFixedWidth(self.sidebar.width())

    def _toggle_theme(self):
        theme_manager.toggle()
        theme_manager.apply(QApplication.instance())
        self.status_label.setText(f"Theme: {theme_manager.current_theme.title()}")

    def _show_about(self):
        QMessageBox.about(
            self,
            f"About {APP_CONFIG['title']}",
            f"<h3>{APP_CONFIG['title']}</h3>"
            f"<p>Version {APP_CONFIG['version']}</p>"
            f"<p>Built with PySide6 and MySQL</p>"
            f"<p>&copy; {APP_CONFIG['company']}</p>"
        )

    def closeEvent(self, event):
        self.db.close()
        event.accept()
