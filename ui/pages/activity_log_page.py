from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QSpinBox, QFrame,
)
from PySide6.QtCore import Qt, QTimer

from inventory.services.activity_service import ActivityService
from ui.components.table_widget import DataTableView


class ActivityLogPage(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.service = ActivityService(db)
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("📋 Activity Log")
        title.setObjectName("sectionTitle")
        header.addWidget(title)
        header.addStretch()

        header.addWidget(QLabel("Days:"))
        self.days_spin = QSpinBox()
        self.days_spin.setRange(1, 365)
        self.days_spin.setValue(7)
        self.days_spin.setFixedWidth(70)
        self.days_spin.valueChanged.connect(self.refresh)
        header.addWidget(self.days_spin)

        header.addWidget(QLabel("Action:"))
        self.action_combo = QComboBox()
        self.action_combo.addItem("All", "")
        self.action_combo.currentIndexChanged.connect(self.refresh)
        header.addWidget(self.action_combo)

        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        self.refresh_btn.clicked.connect(self.refresh)
        header.addWidget(self.refresh_btn)

        layout.addLayout(header)

        self.table = DataTableView(columns=[
            {"key": "created_at", "header": "Timestamp", "width": 160},
            {"key": "username", "header": "User", "width": 120},
            {"key": "action", "header": "Action", "width": 120},
            {"key": "entity_type", "header": "Entity", "width": 100},
            {"key": "entity_id", "header": "ID", "width": 60, "type": "int"},
            {"key": "details", "header": "Details", "width": 300},
        ])
        layout.addWidget(self.table)

        QTimer.singleShot(500, self._load_action_types)

    def _load_action_types(self):
        try:
            actions = self.service.get_action_types()
            for action in actions:
                self.action_combo.addItem(action, action)
        except Exception:
            pass

    def refresh(self):
        try:
            days = self.days_spin.value()
            action = self.action_combo.currentData() or None
            data = self.service.get_all(days=days, action=action)
            self.table.set_data(data)
        except Exception:
            self.table.set_data([])
