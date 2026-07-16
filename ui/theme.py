from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt


LIGHT_QSS = """
QMainWindow, QWidget {
    background-color: #F5F6FA;
    color: #2C3E50;
}

QMenuBar {
    background-color: #FFFFFF;
    border-bottom: 1px solid #E0E0E0;
    padding: 2px;
    font-size: 13px;
}

QMenuBar::item:selected {
    background-color: #E8F0FE;
    border-radius: 4px;
}

QMenu {
    background-color: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 6px;
    padding: 4px;
}

QMenu::item {
    padding: 6px 24px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #E8F0FE;
    color: #1A73E8;
}

QStatusBar {
    background-color: #FFFFFF;
    border-top: 1px solid #E0E0E0;
    color: #5F6368;
    font-size: 12px;
    padding: 2px 10px;
}

QPushButton {
    background-color: #1A73E8;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    font-size: 13px;
    font-weight: 500;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #1557B0;
}

QPushButton:pressed {
    background-color: #0D47A1;
}

QPushButton:disabled {
    background-color: #CCCCCC;
    color: #888888;
}

QPushButton#sidebarButton {
    background-color: transparent;
    color: #5F6368;
    border: none;
    border-radius: 8px;
    padding: 12px 16px;
    text-align: left;
    font-size: 14px;
    font-weight: 400;
}

QPushButton#sidebarButton:hover {
    background-color: #E8F0FE;
    color: #1A73E8;
}

QPushButton#sidebarButton:checked {
    background-color: #E8F0FE;
    color: #1A73E8;
    font-weight: 600;
    border-left: 3px solid #1A73E8;
}

QLineEdit {
    background-color: #FFFFFF;
    border: 1px solid #DADCE0;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    color: #2C3E50;
}

QLineEdit:focus {
    border: 2px solid #1A73E8;
    padding: 7px 11px;
}

QLineEdit:disabled {
    background-color: #F1F3F4;
    color: #80868B;
}

QTextEdit, QPlainTextEdit {
    background-color: #FFFFFF;
    border: 1px solid #DADCE0;
    border-radius: 6px;
    padding: 8px;
    font-size: 13px;
    color: #2C3E50;
}

QTextEdit:focus, QPlainTextEdit:focus {
    border: 2px solid #1A73E8;
}

QComboBox {
    background-color: #FFFFFF;
    border: 1px solid #DADCE0;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    color: #2C3E50;
    min-height: 20px;
}

QComboBox:focus {
    border: 2px solid #1A73E8;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: none;
    width: 0;
}

QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 6px;
    selection-background-color: #E8F0FE;
    selection-color: #1A73E8;
    padding: 4px;
}

QSpinBox, QDoubleSpinBox {
    background-color: #FFFFFF;
    border: 1px solid #DADCE0;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    color: #2C3E50;
    min-height: 20px;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border: 2px solid #1A73E8;
}

QDateEdit {
    background-color: #FFFFFF;
    border: 1px solid #DADCE0;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    color: #2C3E50;
    min-height: 20px;
}

QTableView {
    background-color: #FFFFFF;
    alternate-background-color: #F8F9FA;
    border: 1px solid #E0E0E0;
    border-radius: 8px;
    font-size: 13px;
    color: #2C3E50;
    selection-background-color: #E8F0FE;
    selection-color: #1A73E8;
    gridline-color: #E8EAED;
}

QTableView::item {
    padding: 8px 12px;
    border-bottom: 1px solid #F0F0F0;
}

QTableView::item:selected {
    background-color: #E8F0FE;
    color: #1A73E8;
}

QHeaderView::section {
    background-color: #F8F9FA;
    color: #5F6368;
    padding: 10px 12px;
    border: none;
    border-bottom: 2px solid #E0E0E0;
    font-weight: 600;
    font-size: 12px;
    text-transform: uppercase;
}

QHeaderView::section:hover {
    background-color: #E8EAED;
}

QScrollBar:vertical {
    background-color: transparent;
    width: 8px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #C4C7CC;
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #A8ABB0;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background-color: transparent;
    height: 8px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background-color: #C4C7CC;
    border-radius: 4px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #A8ABB0;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

QLabel {
    color: #2C3E50;
    font-size: 13px;
}

QLabel#titleLabel {
    font-size: 24px;
    font-weight: 700;
    color: #1A73E8;
}

QLabel#sectionTitle {
    font-size: 18px;
    font-weight: 600;
    color: #2C3E50;
}

QLabel#cardValue {
    font-size: 28px;
    font-weight: 700;
    color: #2C3E50;
}

QLabel#cardLabel {
    font-size: 12px;
    font-weight: 500;
    color: #5F6368;
}

QGroupBox {
    background-color: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 10px;
    margin-top: 12px;
    padding: 16px;
    padding-top: 24px;
    font-size: 13px;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 4px 12px;
    background-color: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 4px;
    color: #1A73E8;
}

QTabWidget::pane {
    background-color: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 8px;
    padding: 16px;
}

QTabBar::tab {
    background-color: #F1F3F4;
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    margin-right: 4px;
    font-size: 13px;
    color: #5F6368;
}

QTabBar::tab:selected {
    background-color: #1A73E8;
    color: white;
    font-weight: 500;
}

QTabBar::tab:hover:!selected {
    background-color: #E8EAED;
}

QCheckBox {
    font-size: 13px;
    color: #2C3E50;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #DADCE0;
    border-radius: 3px;
}

QCheckBox::indicator:checked {
    background-color: #1A73E8;
    border-color: #1A73E8;
}

QRadioButton {
    font-size: 13px;
    color: #2C3E50;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #DADCE0;
    border-radius: 10px;
}

QRadioButton::indicator:checked {
    background-color: #1A73E8;
    border-color: #1A73E8;
}

QProgressBar {
    background-color: #E8EAED;
    border: none;
    border-radius: 4px;
    height: 8px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #1A73E8;
    border-radius: 4px;
}

QDialog {
    background-color: #F5F6FA;
}

QFrame#card {
    background-color: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 12px;
    padding: 16px;
}

QFrame#sidebar {
    background-color: #FFFFFF;
    border-right: 1px solid #E0E0E0;
}

QFrame#statCard {
    background-color: #FFFFFF;
    border: 1px solid #E8EAED;
    border-radius: 12px;
    padding: 20px;
}
"""

DARK_QSS = """
QMainWindow, QWidget {
    background-color: #1E1E2E;
    color: #CDD6F4;
}

QMenuBar {
    background-color: #181825;
    border-bottom: 1px solid #313244;
    padding: 2px;
    font-size: 13px;
    color: #CDD6F4;
}

QMenuBar::item:selected {
    background-color: #45475A;
    border-radius: 4px;
}

QMenu {
    background-color: #181825;
    border: 1px solid #313244;
    border-radius: 6px;
    padding: 4px;
    color: #CDD6F4;
}

QMenu::item {
    padding: 6px 24px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #45475A;
    color: #89B4FA;
}

QStatusBar {
    background-color: #181825;
    border-top: 1px solid #313244;
    color: #A6ADC8;
    font-size: 12px;
    padding: 2px 10px;
}

QPushButton {
    background-color: #89B4FA;
    color: #1E1E2E;
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    font-size: 13px;
    font-weight: 500;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #74C7EC;
}

QPushButton:pressed {
    background-color: #89DCEB;
}

QPushButton:disabled {
    background-color: #313244;
    color: #585B70;
}

QPushButton#sidebarButton {
    background-color: transparent;
    color: #A6ADC8;
    border: none;
    border-radius: 8px;
    padding: 12px 16px;
    text-align: left;
    font-size: 14px;
    font-weight: 400;
}

QPushButton#sidebarButton:hover {
    background-color: #313244;
    color: #89B4FA;
}

QPushButton#sidebarButton:checked {
    background-color: #313244;
    color: #89B4FA;
    font-weight: 600;
    border-left: 3px solid #89B4FA;
}

QLineEdit {
    background-color: #313244;
    border: 1px solid #45475A;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    color: #CDD6F4;
}

QLineEdit:focus {
    border: 2px solid #89B4FA;
    padding: 7px 11px;
}

QLineEdit:disabled {
    background-color: #181825;
    color: #585B70;
}

QTextEdit, QPlainTextEdit {
    background-color: #313244;
    border: 1px solid #45475A;
    border-radius: 6px;
    padding: 8px;
    font-size: 13px;
    color: #CDD6F4;
}

QTextEdit:focus, QPlainTextEdit:focus {
    border: 2px solid #89B4FA;
}

QComboBox {
    background-color: #313244;
    border: 1px solid #45475A;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    color: #CDD6F4;
    min-height: 20px;
}

QComboBox:focus {
    border: 2px solid #89B4FA;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox QAbstractItemView {
    background-color: #313244;
    border: 1px solid #45475A;
    border-radius: 6px;
    selection-background-color: #45475A;
    selection-color: #89B4FA;
    padding: 4px;
    color: #CDD6F4;
}

QSpinBox, QDoubleSpinBox {
    background-color: #313244;
    border: 1px solid #45475A;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    color: #CDD6F4;
    min-height: 20px;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border: 2px solid #89B4FA;
}

QDateEdit {
    background-color: #313244;
    border: 1px solid #45475A;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    color: #CDD6F4;
    min-height: 20px;
}

QTableView {
    background-color: #1E1E2E;
    alternate-background-color: #181825;
    border: 1px solid #313244;
    border-radius: 8px;
    font-size: 13px;
    color: #CDD6F4;
    selection-background-color: #45475A;
    selection-color: #89B4FA;
    gridline-color: #313244;
}

QTableView::item {
    padding: 8px 12px;
    border-bottom: 1px solid #313244;
}

QTableView::item:selected {
    background-color: #45475A;
    color: #89B4FA;
}

QHeaderView::section {
    background-color: #181825;
    color: #A6ADC8;
    padding: 10px 12px;
    border: none;
    border-bottom: 2px solid #313244;
    font-weight: 600;
    font-size: 12px;
}

QHeaderView::section:hover {
    background-color: #313244;
}

QScrollBar:vertical {
    background-color: transparent;
    width: 8px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #45475A;
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #585B70;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background-color: transparent;
    height: 8px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background-color: #45475A;
    border-radius: 4px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #585B70;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

QLabel {
    color: #CDD6F4;
    font-size: 13px;
}

QLabel#titleLabel {
    font-size: 24px;
    font-weight: 700;
    color: #89B4FA;
}

QLabel#sectionTitle {
    font-size: 18px;
    font-weight: 600;
    color: #CDD6F4;
}

QLabel#cardValue {
    font-size: 28px;
    font-weight: 700;
    color: #CDD6F4;
}

QLabel#cardLabel {
    font-size: 12px;
    font-weight: 500;
    color: #A6ADC8;
}

QGroupBox {
    background-color: #181825;
    border: 1px solid #313244;
    border-radius: 10px;
    margin-top: 12px;
    padding: 16px;
    padding-top: 24px;
    font-size: 13px;
    font-weight: 600;
    color: #CDD6F4;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 4px 12px;
    background-color: #181825;
    border: 1px solid #313244;
    border-radius: 4px;
    color: #89B4FA;
}

QTabWidget::pane {
    background-color: #1E1E2E;
    border: 1px solid #313244;
    border-radius: 8px;
    padding: 16px;
}

QTabBar::tab {
    background-color: #313244;
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    margin-right: 4px;
    font-size: 13px;
    color: #A6ADC8;
}

QTabBar::tab:selected {
    background-color: #89B4FA;
    color: #1E1E2E;
    font-weight: 500;
}

QTabBar::tab:hover:!selected {
    background-color: #45475A;
}

QCheckBox {
    font-size: 13px;
    color: #CDD6F4;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #45475A;
    border-radius: 3px;
}

QCheckBox::indicator:checked {
    background-color: #89B4FA;
    border-color: #89B4FA;
}

QRadioButton {
    font-size: 13px;
    color: #CDD6F4;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #45475A;
    border-radius: 10px;
}

QRadioButton::indicator:checked {
    background-color: #89B4FA;
    border-color: #89B4FA;
}

QProgressBar {
    background-color: #313244;
    border: none;
    border-radius: 4px;
    height: 8px;
    text-align: center;
    color: #CDD6F4;
}

QProgressBar::chunk {
    background-color: #89B4FA;
    border-radius: 4px;
}

QDialog {
    background-color: #1E1E2E;
}

QFrame#card {
    background-color: #181825;
    border: 1px solid #313244;
    border-radius: 12px;
    padding: 16px;
}

QFrame#sidebar {
    background-color: #181825;
    border-right: 1px solid #313244;
}

QFrame#statCard {
    background-color: #181825;
    border: 1px solid #313244;
    border-radius: 12px;
    padding: 20px;
}
"""


class ThemeManager:
    def __init__(self):
        self._current_theme = "light"

    @property
    def current_theme(self):
        return self._current_theme

    @property
    def is_dark(self):
        return self._current_theme == "dark"

    def toggle(self):
        if self._current_theme == "light":
            self._current_theme = "dark"
        else:
            self._current_theme = "light"

    def set_theme(self, theme):
        if theme in ("light", "dark"):
            self._current_theme = theme

    def get_stylesheet(self):
        return DARK_QSS if self._current_theme == "dark" else LIGHT_QSS

    def apply(self, app):
        app.setStyleSheet(self.get_stylesheet())

    def get_palette(self):
        palette = QPalette()
        if self._current_theme == "dark":
            palette.setColor(QPalette.Window, QColor("#1E1E2E"))
            palette.setColor(QPalette.WindowText, QColor("#CDD6F4"))
            palette.setColor(QPalette.Base, QColor("#313244"))
            palette.setColor(QPalette.Text, QColor("#CDD6F4"))
            palette.setColor(QPalette.Button, QColor("#313244"))
            palette.setColor(QPalette.ButtonText, QColor("#CDD6F4"))
            palette.setColor(QPalette.Highlight, QColor("#89B4FA"))
            palette.setColor(QPalette.HighlightedText, QColor("#1E1E2E"))
        else:
            palette.setColor(QPalette.Window, QColor("#F5F6FA"))
            palette.setColor(QPalette.WindowText, QColor("#2C3E50"))
            palette.setColor(QPalette.Base, QColor("#FFFFFF"))
            palette.setColor(QPalette.Text, QColor("#2C3E50"))
            palette.setColor(QPalette.Button, QColor("#FFFFFF"))
            palette.setColor(QPalette.ButtonText, QColor("#2C3E50"))
            palette.setColor(QPalette.Highlight, QColor("#1A73E8"))
            palette.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
        return palette


theme_manager = ThemeManager()
