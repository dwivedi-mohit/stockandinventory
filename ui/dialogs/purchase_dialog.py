from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QSpinBox, QDoubleSpinBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QDateEdit, QTextEdit, QMessageBox,
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont

from inventory.services.product_service import ProductService
from inventory.services.supplier_service import SupplierService


class PurchaseDialog(QDialog):
    def __init__(self, db, user_id, parent=None):
        super().__init__(parent)
        self.db = db
        self.user_id = user_id
        self.product_service = ProductService(db)
        self.supplier_service = SupplierService(db)
        self._items = []
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        self.setWindowTitle("New Purchase Order")
        self.setMinimumSize(700, 600)
        self.setModal(True)
        if self.parent():
            self.setStyleSheet(self.parent().styleSheet())

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("New Purchase Order")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        form_frame = QFrame()
        form_frame.setObjectName("card")
        form = QVBoxLayout(form_frame)
        form.setSpacing(12)
        form.setContentsMargins(16, 16, 16, 16)

        supplier_row = QHBoxLayout()
        supplier_row.addWidget(QLabel("Supplier:"))
        self.supplier_combo = QComboBox()
        self.supplier_combo.setMinimumWidth(250)
        supplier_row.addWidget(self.supplier_combo)
        supplier_row.addStretch()
        supplier_row.addWidget(QLabel("Date:"))
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        supplier_row.addWidget(self.date_edit)
        form.addLayout(supplier_row)

        add_item_frame = QFrame()
        add_item_frame.setObjectName("card")
        add_item_layout = QVBoxLayout(add_item_frame)
        add_item_layout.setSpacing(8)
        add_item_layout.setContentsMargins(12, 12, 12, 12)

        add_label = QLabel("Add Items")
        add_label.setStyleSheet("font-weight: 600;")
        add_item_layout.addWidget(add_label)

        item_row = QHBoxLayout()
        item_row.addWidget(QLabel("Product:"))
        self.product_combo = QComboBox()
        self.product_combo.setMinimumWidth(200)
        item_row.addWidget(self.product_combo)

        item_row.addWidget(QLabel("Qty:"))
        self.qty_spin = QSpinBox()
        self.qty_spin.setRange(1, 999999)
        self.qty_spin.setValue(1)
        self.qty_spin.setFixedWidth(80)
        item_row.addWidget(self.qty_spin)

        item_row.addWidget(QLabel("Cost:"))
        self.cost_spin = QDoubleSpinBox()
        self.cost_spin.setRange(0, 999999.99)
        self.cost_spin.setDecimals(2)
        self.cost_spin.setPrefix("$ ")
        self.cost_spin.setFixedWidth(120)
        item_row.addWidget(self.cost_spin)

        self.add_item_btn = QPushButton("+ Add")
        self.add_item_btn.setCursor(Qt.PointingHandCursor)
        self.add_item_btn.clicked.connect(self._add_item)
        item_row.addWidget(self.add_item_btn)
        item_row.addStretch()
        add_item_layout.addLayout(item_row)

        form.addWidget(add_item_frame)

        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels(["Product", "Qty", "Unit Cost", "Total", ""])
        self.items_table.horizontalHeader().setStretchLastSection(False)
        self.items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.items_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.items_table.verticalHeader().setVisible(False)
        self.items_table.setAlternatingRowColors(True)
        self.items_table.setMinimumHeight(150)
        form.addWidget(self.items_table)

        form.addSpacing(8)

        totals_row = QHBoxLayout()
        totals_row.addStretch()
        totals_row.addWidget(QLabel("Notes:"))
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(60)
        self.notes_input.setMaximumWidth(250)
        self.notes_input.setPlaceholderText("Optional notes...")
        totals_row.addWidget(self.notes_input)
        totals_row.addSpacing(20)
        totals_row.addWidget(QLabel("Total:"))
        self.total_label = QLabel("$0.00")
        self.total_label.setObjectName("sectionTitle")
        totals_row.addWidget(self.total_label)
        form.addLayout(totals_row)

        layout.addWidget(form_frame)

        button_row = QHBoxLayout()
        button_row.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        button_row.addWidget(cancel_btn)
        self.save_btn = QPushButton("Record Purchase")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.clicked.connect(self._on_save)
        button_row.addWidget(self.save_btn)
        layout.addLayout(button_row)

    def _load_data(self):
        suppliers = self.supplier_service.get_all()
        self.supplier_combo.clear()
        for s in suppliers:
            self.supplier_combo.addItem(
                f"{s['name']} ({s.get('city', '')})", s["supplier_id"]
            )

        products = self.product_service.get_all()
        self.product_combo.clear()
        for p in products:
            if p.get("is_active"):
                self.product_combo.addItem(
                    f"{p['name']} [{p['sku']}]", p["product_id"]
                )

        self.product_combo.currentIndexChanged.connect(self._on_product_changed)
        if products:
            self._on_product_changed()

    def _on_product_changed(self):
        idx = self.product_combo.currentIndex()
        if idx < 0:
            return
        product_id = self.product_combo.currentData()
        if product_id:
            try:
                p = self.product_service.get_by_id(product_id)
                self.cost_spin.setValue(float(p.get("cost_price", 0) or 0))
            except Exception:
                pass

    def _add_item(self):
        product_id = self.product_combo.currentData()
        if not product_id:
            return
        product_name = self.product_combo.currentText().split(" [")[0]
        qty = self.qty_spin.value()
        cost = self.cost_spin.value()

        if qty <= 0:
            return
        if cost <= 0:
            reply = QMessageBox.question(
                self, "Zero Cost",
                f"Unit cost is $0.00 for '{product_name}'. Continue?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.No:
                return

        self._items.append({
            "product_id": product_id,
            "product_name": product_name,
            "quantity": qty,
            "unit_cost": cost,
            "total": qty * cost,
        })
        self._refresh_items_table()
        self.qty_spin.setValue(1)

    def _refresh_items_table(self):
        self.items_table.setRowCount(len(self._items))
        total = 0
        for i, item in enumerate(self._items):
            self.items_table.setItem(i, 0, QTableWidgetItem(item["product_name"]))
            self.items_table.setItem(i, 1, QTableWidgetItem(str(item["quantity"])))
            self.items_table.setItem(i, 2, QTableWidgetItem(f"${item['unit_cost']:.2f}"))

            item_total = item["total"]
            self.items_table.setItem(i, 3, QTableWidgetItem(f"${item_total:.2f}"))
            total += item_total

            remove_btn = QPushButton("✕")
            remove_btn.setFixedSize(30, 30)
            remove_btn.setStyleSheet("background-color: #F44336; color: white; border-radius: 4px;")
            remove_btn.clicked.connect(lambda checked, idx=i: self._remove_item(idx))
            self.items_table.setCellWidget(i, 4, remove_btn)

        self.total_label.setText(f"${total:.2f}")

    def _remove_item(self, idx):
        if 0 <= idx < len(self._items):
            del self._items[idx]
            self._refresh_items_table()

    def _on_save(self):
        if self.supplier_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Validation", "Please select a supplier.")
            return
        if not self._items:
            QMessageBox.warning(self, "Validation", "Please add at least one item.")
            return

        supplier_id = self.supplier_combo.currentData()
        purchase_date = self.date_edit.date().toPython()
        notes = self.notes_input.toPlainText().strip()

        from inventory.services.purchase_service import PurchaseService
        service = PurchaseService(self.db)
        try:
            purchase_id = service.create(
                supplier_id=supplier_id,
                user_id=self.user_id,
                items=self._items,
                purchase_date=purchase_date,
                notes=notes,
            )
            QMessageBox.information(
                self, "Success",
                f"Purchase #{purchase_id} recorded successfully!\n"
                f"Stock has been updated."
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to record purchase: {e}")

    def get_result(self):
        return True
