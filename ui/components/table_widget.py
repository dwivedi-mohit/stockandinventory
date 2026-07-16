from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QTableView, QHeaderView, QLabel, QFrame, QSizePolicy,
)
from PySide6.QtCore import Qt, QSortFilterProxyModel, QAbstractTableModel, QModelIndex, Signal
from PySide6.QtGui import QColor, QFont


class PandasTableModel(QAbstractTableModel):
    def __init__(self, data=None, columns=None):
        super().__init__()
        self._data = data or []
        self._columns = columns or []

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._columns)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._data)):
            return None
        row = self._data[index.row()]
        col_key = self._columns[index.column()]["key"]
        value = row.get(col_key, "")

        if role == Qt.DisplayRole:
            if value is None:
                return ""
            if isinstance(value, float):
                return f"{value:.2f}"
            return str(value)

        if role == Qt.TextAlignmentRole:
            col_type = self._columns[index.column()].get("type", "string")
            if col_type in ("decimal", "int"):
                return Qt.AlignRight | Qt.AlignVCenter
            return Qt.AlignLeft | Qt.AlignVCenter

        if role == Qt.ForegroundRole:
            if col_key == "stock_quantity":
                min_stock = row.get("min_stock_level", 10)
                if isinstance(value, (int, float)) and value <= min_stock:
                    return QColor("#F44336")
            if col_key == "is_active" and not value:
                return QColor("#9E9E9E")

        if role == Qt.FontRole:
            if col_key in ("name", "product_name", "supplier_name"):
                font = QFont()
                font.setWeight(QFont.Medium)
                return font

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if 0 <= section < len(self._columns):
                return self._columns[section]["header"]
        return None

    def get_row(self, row):
        if 0 <= row < len(self._data):
            return self._data[row]
        return None

    def set_data(self, data):
        self.beginResetModel()
        self._data = data
        self.endResetModel()

    def sort(self, column, order=Qt.AscendingOrder):
        if not (0 <= column < len(self._columns)):
            return
        col_key = self._columns[column]["key"]

        self.beginResetModel()
        reverse = order == Qt.DescendingOrder
        self._data.sort(key=lambda r: (r.get(col_key) is None, r.get(col_key, "")), reverse=reverse)
        self.endResetModel()


class DataTableView(QFrame):
    row_double_clicked = Signal(dict)
    add_clicked = Signal()

    def __init__(self, columns=None, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self._columns = columns or []
        self._model = PandasTableModel(columns=self._columns)
        self._search_timer = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(0, 0, 0, 0)

        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 0)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search...")
        self.search_input.setMinimumWidth(280)
        self.search_input.textChanged.connect(self._on_search_changed)
        search_layout.addWidget(self.search_input)

        toolbar.addLayout(search_layout)
        toolbar.addStretch()

        self.add_button = QPushButton("➕ Add New")
        self.add_button.setCursor(Qt.PointingHandCursor)
        self.add_button.clicked.connect(self.add_clicked.emit)
        toolbar.addWidget(self.add_button)

        layout.addLayout(toolbar)

        self.table = QTableView()
        self.table.setModel(self._model)
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setSelectionMode(QTableView.SingleSelection)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionsClickable(True)
        self.table.horizontalHeader().setHighlightSections(False)
        self.table.setMouseTracking(True)
        self.table.doubleClicked.connect(self._on_row_double_clicked)

        table_font = QFont()
        table_font.setPointSize(12)
        self.table.setFont(table_font)
        self.table.verticalHeader().setDefaultSectionSize(40)

        layout.addWidget(self.table)

        self.status_bar = QHBoxLayout()
        self.status_bar.setContentsMargins(0, 0, 0, 0)
        self.row_count_label = QLabel("0 rows")
        self.row_count_label.setStyleSheet("color: #888; font-size: 12px;")
        self.status_bar.addWidget(self.row_count_label)
        self.status_bar.addStretch()
        layout.addLayout(self.status_bar)

    def _on_search_changed(self, text):
        if self._search_timer:
            self._search_timer.stop()
        from PySide6.QtCore import QTimer
        self._search_timer = QTimer.singleShot(300, lambda: self._apply_search(text))

    def _apply_search(self, text):
        self.filter_text = text
        self._update_row_count()

    def _on_row_double_clicked(self, index):
        row = self._model.get_row(index.row())
        if row:
            self.row_double_clicked.emit(row)

    def set_columns(self, columns):
        self._columns = columns
        self._model = PandasTableModel(columns=self._columns)
        self.table.setModel(self._model)
        self.table.setSortingEnabled(True)

    def set_data(self, data):
        self._model.set_data(data)
        self._resize_columns()
        self._update_row_count()

    def _resize_columns(self):
        header = self.table.horizontalHeader()
        for i, col in enumerate(self._columns):
            width = col.get("width", 100)
            if width == -1:
                header.setSectionResizeMode(i, QHeaderView.Stretch)
            else:
                header.setSectionResizeMode(i, QHeaderView.Interactive)
                header.resizeSection(i, width)

    def _update_row_count(self):
        count = self._model.rowCount()
        self.row_count_label.setText(f"{count} row{'s' if count != 1 else ''}")

    def get_search_text(self):
        return self.search_input.text()

    def get_selected_row(self):
        indexes = self.table.selectionModel().selectedRows()
        if indexes:
            return self._model.get_row(indexes[0].row())
        return None

    def refresh(self, data):
        self.set_data(data)
