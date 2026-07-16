from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox, QLabel
from PySide6.QtCore import Qt

from inventory.services.product_service import ProductService
from inventory.services.category_service import CategoryService
from inventory.exceptions import ValidationError, NotFoundError
from inventory.session import session_manager
from ui.components.table_widget import DataTableView
from ui.dialogs.form_dialog import FormDialog, FormField


class ProductsPage(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.service = ProductService(db)
        self.category_service = CategoryService(db)
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("📦 Products")
        title.setObjectName("sectionTitle")
        header.addWidget(title)
        header.addStretch()

        self.delete_btn = QPushButton("🗑 Delete")
        self.delete_btn.setCursor(Qt.PointingHandCursor)
        self.delete_btn.setStyleSheet("background-color: #F44336;")
        self.delete_btn.clicked.connect(self._on_delete)
        self.delete_btn.setVisible(session_manager.is_authenticated and session_manager.current_user.role == "admin")
        header.addWidget(self.delete_btn)

        layout.addLayout(header)

        self.table = DataTableView(columns=[
            {"key": "product_id", "header": "ID", "width": 60, "type": "int"},
            {"key": "name", "header": "Product Name", "width": 200},
            {"key": "sku", "header": "SKU", "width": 100},
            {"key": "category_name", "header": "Category", "width": 120},
            {"key": "cost_price", "header": "Cost", "width": 90, "type": "decimal"},
            {"key": "selling_price", "header": "Selling Price", "width": 110, "type": "decimal"},
            {"key": "stock_quantity", "header": "Stock", "width": 80, "type": "int"},
            {"key": "min_stock_level", "header": "Min Stock", "width": 80, "type": "int"},
            {"key": "is_active", "header": "Active", "width": 60},
        ])
        self.table.add_clicked.connect(self._on_add)
        self.table.row_double_clicked.connect(self._on_edit)
        layout.addWidget(self.table)

    def refresh(self):
        search = self.table.get_search_text()
        try:
            data = self.service.get_all(search=search)
            self.table.set_data(data)
        except Exception as e:
            self.table.set_data([])

    def _on_add(self):
        cat = self.category_service.get_all()
        cat_items = [(c["category_id"], c["name"]) for c in cat]
        cat_items.insert(0, (None, "-- No Category --"))

        fields = [
            FormField("name", "Product Name", "text", required=True,
                      placeholder="Enter product name", max_length=255),
            FormField("sku", "SKU", "text", required=True,
                      placeholder="Auto-generated or enter manually"),
            FormField("barcode", "Barcode", "text", placeholder="EAN-13 barcode"),
            FormField("category_id", "Category", "combobox", items=cat_items),
            FormField("cost_price", "Cost Price", "decimal", default=0.00,
                      kwargs={"prefix": "currency"}),
            FormField("selling_price", "Selling Price", "decimal", required=True,
                      default=0.00, kwargs={"prefix": "currency"}),
            FormField("stock_quantity", "Initial Stock", "integer", default=0),
            FormField("min_stock_level", "Min Stock Level", "integer", default=10),
            FormField("description", "Description", "textarea",
                      placeholder="Optional product description"),
        ]

        dialog = FormDialog("Add Product", fields, parent=self)
        if dialog.exec() == FormDialog.Accepted:
            data = dialog.get_data()
            try:
                if not data.get("sku"):
                    data["sku"] = self.service.generate_sku(
                        data.get("category_id")
                    )
                self.service.create(**data)
                self.refresh()
                QMessageBox.information(self, "Success", "✅ Product added successfully!")
            except ValidationError as e:
                QMessageBox.warning(self, "Validation Error", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add product: {e}")

    def _on_edit(self, row):
        cat = self.category_service.get_all()
        cat_items = [(c["category_id"], c["name"]) for c in cat]
        cat_items.insert(0, (None, "-- No Category --"))

        fields = [
            FormField("name", "Product Name", "text", required=True,
                      placeholder="Enter product name", max_length=255),
            FormField("sku", "SKU", "text", required=True),
            FormField("barcode", "Barcode", "text"),
            FormField("category_id", "Category", "combobox", items=cat_items),
            FormField("cost_price", "Cost Price", "decimal"),
            FormField("selling_price", "Selling Price", "decimal", required=True),
            FormField("min_stock_level", "Min Stock Level", "integer"),
            FormField("description", "Description", "textarea"),
        ]

        edit_data = {
            "name": row.get("name", ""),
            "sku": row.get("sku", ""),
            "barcode": row.get("barcode", ""),
            "category_id": row.get("category_id"),
            "cost_price": float(row.get("cost_price", 0) or 0),
            "selling_price": float(row.get("selling_price", 0) or 0),
            "min_stock_level": int(row.get("min_stock_level", 10)),
            "description": "",
        }

        dialog = FormDialog(
            f"Edit Product: {row.get('name', '')}",
            fields, data=edit_data, parent=self,
        )

        if dialog.exec() == FormDialog.Accepted:
            data = dialog.get_data()
            try:
                self.service.update(row["product_id"], **data)
                self.refresh()
                QMessageBox.information(self, "Success", "✅ Product updated successfully!")
            except ValidationError as e:
                QMessageBox.warning(self, "Validation Error", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update product: {e}")

    def _on_delete(self):
        row = self.table.get_selected_row()
        if not row:
            QMessageBox.warning(self, "No Selection", "Please select a product to delete.")
            return
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete product '{row.get('name', '')}'?\nThis cannot be undone.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            try:
                self.service.delete(row["product_id"])
                self.refresh()
                QMessageBox.information(self, "Success", "✅ Product deleted.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete: {e}")
