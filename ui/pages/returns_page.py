from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QMessageBox, QComboBox, QSpinBox, QTextEdit, QFrame,
)
from PySide6.QtCore import Qt

from inventory.services.sale_service import SaleService
from inventory.services.product_service import ProductService
from ui.components.table_widget import DataTableView


class ReturnsPage(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.sale_service = SaleService(db)
        self.product_service = ProductService(db)
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("↩️ Returns & Refunds")
        title.setObjectName("sectionTitle")
        header.addWidget(title)
        header.addStretch()

        self.new_return_btn = QPushButton("➕ Process Return")
        self.new_return_btn.setCursor(Qt.PointingHandCursor)
        self.new_return_btn.clicked.connect(self._on_process_return)
        header.addWidget(self.new_return_btn)
        layout.addLayout(header)

        self.table = DataTableView(columns=[
            {"key": "return_id", "header": "Return #", "width": 80, "type": "int"},
            {"key": "return_date", "header": "Date", "width": 110},
            {"key": "sale_id", "header": "Invoice #", "width": 80, "type": "int"},
            {"key": "product_name", "header": "Product", "width": 200},
            {"key": "quantity", "header": "Qty", "width": 60, "type": "int"},
            {"key": "reason", "header": "Reason", "width": 250},
        ])
        layout.addWidget(self.table)

    def refresh(self):
        try:
            search = self.table.get_search_text()
            query = """SELECT r.*, pr.name as product_name
                       FROM returns r
                       JOIN products pr ON r.product_id = pr.product_id
                       WHERE 1=1"""
            params = []
            if search:
                query += " AND (pr.name LIKE %s OR r.reason LIKE %s OR r.return_id LIKE %s)"
                params.extend([f"%{search}%"] * 3)
            query += " ORDER BY r.return_id DESC"
            data = self.db.execute_query(query, params, dictionary=True)
            self.table.set_data(data)
        except Exception:
            self.table.set_data([])

    def _on_process_return(self):
        from PySide6.QtWidgets import QDialog, QVBoxLayout

        dialog = QDialog(self)
        dialog.setWindowTitle("Process Return")
        dialog.setMinimumWidth(450)
        dialog.setModal(True)
        dialog.setStyleSheet(self.styleSheet())

        layout = QVBoxLayout(dialog)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Process Return")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        info_label = QLabel(
            "Enter the Invoice # and Product to process a return.\n"
            "Stock will be restored automatically."
        )
        info_label.setStyleSheet("color: #888; font-size: 12px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        form_frame = QFrame()
        form_frame.setObjectName("card")
        form = QVBoxLayout(form_frame)
        form.setSpacing(8)

        sale_row = QHBoxLayout()
        sale_row.addWidget(QLabel("Invoice #:"))
        sale_input = QSpinBox()
        sale_input.setRange(1, 999999)
        sale_input.setFixedWidth(120)
        sale_row.addWidget(sale_input)
        sale_row.addStretch()
        form.addLayout(sale_row)

        product_row = QHBoxLayout()
        product_row.addWidget(QLabel("Product:"))
        product_combo = QComboBox()
        product_combo.setMinimumWidth(250)
        product_row.addWidget(product_combo)
        product_row.addStretch()
        form.addLayout(product_row)

        qty_row = QHBoxLayout()
        qty_row.addWidget(QLabel("Quantity:"))
        qty_input = QSpinBox()
        qty_input.setRange(1, 99999)
        qty_input.setFixedWidth(100)
        qty_row.addWidget(qty_input)
        qty_row.addStretch()
        form.addLayout(qty_row)

        reason_row = QHBoxLayout()
        reason_row.addWidget(QLabel("Reason:"))
        reason_input = QTextEdit()
        reason_input.setMaximumHeight(60)
        reason_input.setMinimumWidth(250)
        reason_input.setPlaceholderText("e.g., Defective, Wrong item, Customer return")
        reason_row.addWidget(reason_input)
        form.addLayout(reason_row)

        layout.addWidget(form_frame)

        button_row = QHBoxLayout()
        button_row.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(dialog.reject)
        button_row.addWidget(cancel_btn)
        process_btn = QPushButton("✅ Process Return")
        process_btn.setCursor(Qt.PointingHandCursor)
        process_btn.clicked.connect(lambda: self._do_return(
            dialog, sale_input.value(), product_combo.currentData(),
            qty_input.value(), reason_input.toPlainText().strip()
        ))
        button_row.addWidget(process_btn)
        layout.addLayout(button_row)

        products = self.product_service.get_all()
        product_combo.clear()
        for p in products:
            product_combo.addItem(f"{p['name']} [{p['sku']}]", p["product_id"])

        dialog.exec()

    def _do_return(self, dialog, sale_id, product_id, quantity, reason):
        if not sale_id or not product_id:
            QMessageBox.warning(dialog, "Validation", "Please enter Invoice # and select a product.")
            return
        if quantity <= 0:
            QMessageBox.warning(dialog, "Validation", "Quantity must be greater than 0.")
            return

        try:
            self.sale_service.process_return(
                sale_id=sale_id,
                product_id=product_id,
                quantity=quantity,
                reason=reason or "Customer return",
            )
            QMessageBox.information(
                dialog, "Success",
                "✅ Return processed successfully!\nStock has been restored."
            )
            dialog.accept()
            self.refresh()
        except Exception as e:
            QMessageBox.critical(dialog, "Error", f"Failed to process return: {e}")
