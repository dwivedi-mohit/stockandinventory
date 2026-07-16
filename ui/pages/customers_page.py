from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox, QLabel
from PySide6.QtCore import Qt

from inventory.services.customer_service import CustomerService
from inventory.exceptions import ValidationError, NotFoundError
from inventory.session import session_manager
from ui.components.table_widget import DataTableView
from ui.dialogs.form_dialog import FormDialog, FormField


class CustomersPage(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.service = CustomerService(db)
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("👤 Customers")
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
            {"key": "customer_id", "header": "ID", "width": 60, "type": "int"},
            {"key": "name", "header": "Customer Name", "width": 200},
            {"key": "email", "header": "Email", "width": 200},
            {"key": "phone", "header": "Phone", "width": 140},
            {"key": "loyalty_points", "header": "Loyalty Pts", "width": 100, "type": "int"},
        ])
        self.table.add_clicked.connect(self._on_add)
        self.table.row_double_clicked.connect(self._on_edit)
        layout.addWidget(self.table)

    def refresh(self):
        search = self.table.get_search_text()
        try:
            data = self.service.get_all(search=search)
            self.table.set_data(data)
        except Exception:
            self.table.set_data([])

    def _on_add(self):
        fields = [
            FormField("name", "Customer Name", "text", required=True,
                      placeholder="e.g., John Doe", max_length=255),
            FormField("email", "Email", "text", placeholder="customer@email.com"),
            FormField("phone", "Phone", "text", placeholder="+1-555-1001"),
            FormField("address", "Address", "textarea", placeholder="Street address"),
        ]

        dialog = FormDialog("Add Customer", fields, parent=self)
        if dialog.exec() == FormDialog.Accepted:
            data = dialog.get_data()
            try:
                self.service.create(**data)
                self.refresh()
                QMessageBox.information(self, "Success", "✅ Customer added successfully!")
            except ValidationError as e:
                QMessageBox.warning(self, "Validation Error", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add customer: {e}")

    def _on_edit(self, row):
        fields = [
            FormField("name", "Customer Name", "text", required=True, max_length=255),
            FormField("email", "Email", "text"),
            FormField("phone", "Phone", "text"),
            FormField("address", "Address", "textarea"),
        ]

        edit_data = {
            "name": row.get("name", ""),
            "email": row.get("email", ""),
            "phone": row.get("phone", ""),
            "address": row.get("address", ""),
        }

        dialog = FormDialog(
            f"Edit Customer: {row.get('name', '')}",
            fields, data=edit_data, parent=self,
        )
        if dialog.exec() == FormDialog.Accepted:
            data = dialog.get_data()
            try:
                self.service.update(row["customer_id"], **data)
                self.refresh()
                QMessageBox.information(self, "Success", "✅ Customer updated successfully!")
            except ValidationError as e:
                QMessageBox.warning(self, "Validation Error", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update customer: {e}")

    def _on_delete(self):
        row = self.table.get_selected_row()
        if not row:
            QMessageBox.warning(self, "No Selection", "Please select a customer to delete.")
            return
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete customer '{row.get('name', '')}'?\nThis cannot be undone.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            try:
                self.service.delete(row["customer_id"])
                self.refresh()
                QMessageBox.information(self, "Success", "✅ Customer deleted.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete: {e}")
