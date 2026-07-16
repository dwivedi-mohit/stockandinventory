from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLabel, QLineEdit, QComboBox,
    QDoubleSpinBox, QSpinBox, QTextEdit, QCheckBox,
    QFrame, QWidget,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class FormField:
    def __init__(self, key, label, field_type="text", required=False, **kwargs):
        self.key = key
        self.label = label
        self.field_type = field_type
        self.required = required
        self.kwargs = kwargs
        self.widget = None

    def create_widget(self):
        if self.field_type == "text":
            w = QLineEdit()
            w.setPlaceholderText(self.kwargs.get("placeholder", ""))
            if "max_length" in self.kwargs:
                w.setMaxLength(self.kwargs["max_length"])
        elif self.field_type == "password":
            w = QLineEdit()
            w.setEchoMode(QLineEdit.Password)
            w.setPlaceholderText(self.kwargs.get("placeholder", ""))
        elif self.field_type == "integer":
            w = QSpinBox()
            w.setRange(self.kwargs.get("min", 0), self.kwargs.get("max", 999999))
            w.setValue(self.kwargs.get("default", 0))
        elif self.field_type == "decimal":
            w = QDoubleSpinBox()
            w.setRange(self.kwargs.get("min", 0), self.kwargs.get("max", 999999.99))
            w.setDecimals(2)
            w.setValue(self.kwargs.get("default", 0.00))
            w.setPrefix("$ " if self.kwargs.get("prefix") == "currency" else "")
        elif self.field_type == "combobox":
            w = QComboBox()
            w.setEditable(self.kwargs.get("editable", False))
            items = self.kwargs.get("items", [])
            if items:
                if isinstance(items[0], (list, tuple)):
                    for value, label in items:
                        w.addItem(label, value)
                else:
                    for item in items:
                        w.addItem(str(item), item)
            placeholder = self.kwargs.get("placeholder", "")
            if placeholder:
                w.setCurrentText("")
                w.setPlaceholderText(placeholder)
        elif self.field_type == "textarea":
            w = QTextEdit()
            w.setPlaceholderText(self.kwargs.get("placeholder", ""))
            w.setMaximumHeight(self.kwargs.get("height", 80))
        elif self.field_type == "checkbox":
            w = QCheckBox()
            w.setChecked(self.kwargs.get("default", False))
        else:
            w = QLineEdit()
        self.widget = w
        return w

    def get_value(self):
        if self.field_type == "text" or self.field_type == "password":
            return self.widget.text().strip() if hasattr(self.widget, 'text') else ""
        elif self.field_type == "integer":
            return self.widget.value()
        elif self.field_type == "decimal":
            return self.widget.value()
        elif self.field_type == "combobox":
            data = self.widget.currentData()
            return data if data is not None else self.widget.currentText()
        elif self.field_type == "textarea":
            return self.widget.toPlainText().strip()
        elif self.field_type == "checkbox":
            return self.widget.isChecked()
        return ""

    def set_value(self, value):
        if value is None:
            value = "" if self.field_type in ("text", "textarea") else 0
        if self.field_type in ("text", "password"):
            self.widget.setText(str(value))
        elif self.field_type == "integer":
            self.widget.setValue(int(value))
        elif self.field_type == "decimal":
            self.widget.setValue(float(value))
        elif self.field_type == "combobox":
            idx = self.widget.findData(value)
            if idx >= 0:
                self.widget.setCurrentIndex(idx)
            else:
                self.widget.setCurrentText(str(value))
        elif self.field_type == "textarea":
            self.widget.setPlainText(str(value))
        elif self.field_type == "checkbox":
            self.widget.setChecked(bool(value))

    def validate(self):
        if not self.required:
            return None
        val = self.get_value()
        if isinstance(val, str) and not val:
            return f"{self.label} is required."
        if isinstance(val, (int, float)) and val == 0 and self.field_type not in ("checkbox",):
            if self.kwargs.get("allow_zero", True):
                return None
            return f"{self.label} is required."
        return None


class FormDialog(QDialog):
    def __init__(self, title, fields, data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(500)
        self.setModal(True)
        self.setStyleSheet(self.parent().styleSheet() if parent else "")

        self.fields = fields
        self.result_data = {}

        self._setup_ui()
        if data:
            self._load_data(data)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title_label = QLabel(self.windowTitle())
        title_label.setObjectName("sectionTitle")
        layout.addWidget(title_label)

        form_container = QFrame()
        form_container.setObjectName("card")
        form_layout = QFormLayout(form_container)
        form_layout.setSpacing(12)
        form_layout.setContentsMargins(16, 16, 16, 16)
        form_layout.setLabelAlignment(Qt.AlignRight)

        for field in self.fields:
            widget = field.create_widget()
            label_text = field.label
            if field.required:
                label_text = f"{label_text} *"
            label = QLabel(label_text)
            label.setStyleSheet("font-weight: 600; font-size: 13px;")
            form_layout.addRow(label, widget)

        layout.addWidget(form_container)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet(
            "color: #F44336; font-size: 12px; padding: 4px;"
            "background-color: #FFEBEE; border-radius: 4px;"
        )
        self.error_label.setVisible(False)
        self.error_label.setWordWrap(True)
        layout.addWidget(self.error_label)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        self.save_btn = QPushButton("Save")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.clicked.connect(self._on_save)
        button_layout.addWidget(self.save_btn)

        layout.addLayout(button_layout)

    def _load_data(self, data):
        for field in self.fields:
            if field.key in data:
                field.set_value(data[field.key])

    def _on_save(self):
        errors = []
        for field in self.fields:
            error = field.validate()
            if error:
                errors.append(error)

        if errors:
            self.error_label.setText("• " + "\n• ".join(errors))
            self.error_label.setVisible(True)
            return

        self.error_label.setVisible(False)
        self.result_data = {}
        for field in self.fields:
            self.result_data[field.key] = field.get_value()
        self.accept()

    def get_data(self):
        return self.result_data
