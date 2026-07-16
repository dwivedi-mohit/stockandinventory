from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QSpinBox, QDoubleSpinBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QDateEdit, QTextEdit, QMessageBox,
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont

from inventory.services.product_service import ProductService
from inventory.services.customer_service import CustomerService


class SaleDialog(QDialog):
    def __init__(self, db, user_id, parent=None):
        super().__init__(parent)
        self.db = db
        self.user_id = user_id
        self.product_service = ProductService(db)
        self.customer_service = CustomerService(db)
        self._items = []
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        self.setWindowTitle("New Sale")
        self.setMinimumSize(750, 650)
        self.setModal(True)
        if self.parent():
            self.setStyleSheet(self.parent().styleSheet())

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("💳 New Sale Invoice")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        form_frame = QFrame()
        form_frame.setObjectName("card")
        form = QVBoxLayout(form_frame)
        form.setSpacing(12)
        form.setContentsMargins(16, 16, 16, 16)

        top_row = QHBoxLayout()
        top_row.addWidget(QLabel("Customer:"))
        self.customer_combo = QComboBox()
        self.customer_combo.setMinimumWidth(250)
        self.customer_combo.addItem("-- Walk-in Customer --", None)
        top_row.addWidget(self.customer_combo)
        top_row.addStretch()
        top_row.addWidget(QLabel("Date:"))
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        top_row.addWidget(self.date_edit)
        form.addLayout(top_row)

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
        self.qty_spin.setRange(1, 99999)
        self.qty_spin.setValue(1)
        self.qty_spin.setFixedWidth(70)
        item_row.addWidget(self.qty_spin)

        item_row.addWidget(QLabel("Price:"))
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0, 999999.99)
        self.price_spin.setDecimals(2)
        self.price_spin.setPrefix("$ ")
        self.price_spin.setFixedWidth(110)
        item_row.addWidget(self.price_spin)

        item_row.addWidget(QLabel("Disc:"))
        self.discount_spin = QDoubleSpinBox()
        self.discount_spin.setRange(0, 999999.99)
        self.discount_spin.setDecimals(2)
        self.discount_spin.setPrefix("$ ")
        self.discount_spin.setFixedWidth(100)
        self.discount_spin.setValue(0)
        item_row.addWidget(self.discount_spin)

        self.add_item_btn = QPushButton("➕ Add")
        self.add_item_btn.setCursor(Qt.PointingHandCursor)
        self.add_item_btn.clicked.connect(self._add_item)
        item_row.addWidget(self.add_item_btn)
        item_row.addStretch()
        add_item_layout.addLayout(item_row)

        self.stock_info = QLabel("")
        self.stock_info.setStyleSheet("color: #888; font-size: 11px;")
        add_item_layout.addWidget(self.stock_info)

        form.addWidget(add_item_frame)

        self.items_table = QTableWidget()
        self.items_table.setColumnCount(6)
        self.items_table.setHorizontalHeaderLabels(
            ["Product", "Qty", "Unit Price", "Discount", "Total", ""]
        )
        self.items_table.horizontalHeader().setStretchLastSection(False)
        self.items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.items_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.items_table.verticalHeader().setVisible(False)
        self.items_table.setAlternatingRowColors(True)
        self.items_table.setMinimumHeight(150)
        form.addWidget(self.items_table)

        form.addSpacing(8)

        payment_row = QHBoxLayout()
        payment_row.addWidget(QLabel("Payment:"))
        self.payment_combo = QComboBox()
        self.payment_combo.addItems(["cash", "card", "transfer"])
        payment_row.addWidget(self.payment_combo)

        payment_row.addSpacing(20)
        payment_row.addWidget(QLabel("Discount:"))
        self.invoice_discount = QDoubleSpinBox()
        self.invoice_discount.setRange(0, 999999.99)
        self.invoice_discount.setDecimals(2)
        self.invoice_discount.setPrefix("$ ")
        self.invoice_discount.setValue(0)
        self.invoice_discount.setFixedWidth(110)
        self.invoice_discount.valueChanged.connect(self._update_totals)
        payment_row.addWidget(self.invoice_discount)

        payment_row.addWidget(QLabel("Tax:"))
        self.tax_spin = QDoubleSpinBox()
        self.tax_spin.setRange(0, 100)
        self.tax_spin.setDecimals(2)
        self.tax_spin.setSuffix(" %")
        self.tax_spin.setValue(0)
        self.tax_spin.setFixedWidth(90)
        self.tax_spin.valueChanged.connect(self._update_totals)
        payment_row.addWidget(self.tax_spin)

        payment_row.addStretch()
        payment_row.addWidget(QLabel("Subtotal:"))
        self.subtotal_label = QLabel("$0.00")
        self.subtotal_label.setStyleSheet("font-size: 14px;")
        payment_row.addWidget(self.subtotal_label)

        payment_row.addSpacing(10)
        payment_row.addWidget(QLabel("Total:"))
        self.total_label = QLabel("$0.00")
        self.total_label.setObjectName("sectionTitle")
        payment_row.addWidget(self.total_label)
        form.addLayout(payment_row)

        notes_row = QHBoxLayout()
        notes_row.addWidget(QLabel("Notes:"))
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(50)
        self.notes_input.setMaximumWidth(300)
        self.notes_input.setPlaceholderText("Optional notes...")
        notes_row.addWidget(self.notes_input)
        notes_row.addStretch()
        form.addLayout(notes_row)

        layout.addWidget(form_frame)

        button_row = QHBoxLayout()
        button_row.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        button_row.addWidget(cancel_btn)
        self.save_btn = QPushButton("✅ Complete Sale")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.clicked.connect(self._on_save)
        button_row.addWidget(self.save_btn)
        layout.addLayout(button_row)

    def _load_data(self):
        customers = self.customer_service.get_all()
        for c in customers:
            self.customer_combo.addItem(
                f"{c['name']} ({c.get('email', '')})", c["customer_id"]
            )

        products = self.product_service.get_all(search="")
        for p in products:
            if p.get("is_active"):
                self.product_combo.addItem(
                    f"{p['name']} [{p['sku']}] (Stock: {p['stock_quantity']})",
                    p["product_id"],
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
                self.price_spin.setValue(float(p.get("selling_price", 0) or 0))
                stock = int(p.get("stock_quantity", 0))
                self.qty_spin.setMaximum(max(stock, 0))
                self.stock_info.setText(f"Available stock: {stock}")
                if stock <= 10:
                    self.stock_info.setStyleSheet("color: #F44336; font-size: 11px; font-weight: bold;")
                else:
                    self.stock_info.setStyleSheet("color: #888; font-size: 11px;")
            except Exception:
                pass

    def _add_item(self):
        product_id = self.product_combo.currentData()
        if not product_id:
            return
        product_name = self.product_combo.currentText().split(" [")[0]
        qty = self.qty_spin.value()
        price = self.price_spin.value()
        discount = self.discount_spin.value()

        if qty <= 0:
            return
        if price <= 0:
            QMessageBox.warning(self, "Validation", "Price must be greater than 0.")
            return

        total = (qty * price) - discount
        self._items.append({
            "product_id": product_id,
            "product_name": product_name,
            "quantity": qty,
            "unit_price": price,
            "discount": discount,
            "total": total,
        })
        self._refresh_items_table()
        self.qty_spin.setValue(1)
        self.discount_spin.setValue(0)

    def _refresh_items_table(self):
        self.items_table.setRowCount(len(self._items))
        subtotal = 0
        for i, item in enumerate(self._items):
            self.items_table.setItem(i, 0, QTableWidgetItem(item["product_name"]))
            self.items_table.setItem(i, 1, QTableWidgetItem(str(item["quantity"])))
            self.items_table.setItem(i, 2, QTableWidgetItem(f"${item['unit_price']:.2f}"))
            self.items_table.setItem(i, 3, QTableWidgetItem(f"${item['discount']:.2f}"))
            self.items_table.setItem(i, 4, QTableWidgetItem(f"${item['total']:.2f}"))
            subtotal += item["total"]

            remove_btn = QPushButton("✕")
            remove_btn.setFixedSize(30, 30)
            remove_btn.setStyleSheet("background-color: #F44336; color: white; border-radius: 4px;")
            remove_btn.clicked.connect(lambda checked, idx=i: self._remove_item(idx))
            self.items_table.setCellWidget(i, 5, remove_btn)

        self._subtotal = subtotal
        self._update_totals()

    def _update_totals(self):
        subtotal = getattr(self, "_subtotal", 0)
        discount = self.invoice_discount.value()
        tax_pct = self.tax_spin.value()
        tax_amount = subtotal * (tax_pct / 100)
        grand_total = subtotal - discount + tax_amount

        self.subtotal_label.setText(f"${subtotal:.2f}")
        self.total_label.setText(f"${grand_total:.2f}")
        self._grand_total = grand_total
        self._tax_amount = tax_amount

    def _remove_item(self, idx):
        if 0 <= idx < len(self._items):
            del self._items[idx]
            self._refresh_items_table()

    def _on_save(self):
        if not self._items:
            QMessageBox.warning(self, "Validation", "Please add at least one item.")
            return

        customer_id = self.customer_combo.currentData()
        sale_date = self.date_edit.date().toPython()
        payment_method = self.payment_combo.currentText()
        notes = self.notes_input.toPlainText().strip()

        from inventory.services.sale_service import SaleService
        service = SaleService(self.db)
        try:
            subtotal = getattr(self, "_subtotal", 0)
            discount = self.invoice_discount.value()
            tax = getattr(self, "_tax_amount", 0)

            sale_id = service.create(
                user_id=self.user_id,
                items=self._items,
                customer_id=customer_id,
                discount=discount,
                tax=tax,
                payment_method=payment_method,
                sale_date=sale_date,
                notes=notes,
            )
            QMessageBox.information(
                self, "Success",
                f"✅ Sale #{sale_id} completed successfully!\n"
                f"Total: ${getattr(self, '_grand_total', 0):.2f}\n"
                f"Stock has been updated."
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to complete sale: {e}")

    def get_result(self):
        return True
