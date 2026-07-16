from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox, QLabel
from PySide6.QtCore import Qt

from inventory.services.supplier_service import SupplierService
from inventory.exceptions import ValidationError, NotFoundError
from inventory.session import session_manager
from ui.components.table_widget import DataTableView
from ui.dialogs.form_dialog import FormDialog, FormField


class SuppliersPage(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.service = SupplierService(db)
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("👥 Suppliers")
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
            {"key": "supplier_id", "header": "ID", "width": 60, "type": "int"},
            {"key": "name", "header": "Company Name", "width": 180},
            {"key": "contact_person", "header": "Contact Person", "width": 140},
            {"key": "email", "header": "Email", "width": 180},
            {"key": "phone", "header": "Phone", "width": 130},
            {"key": "city", "header": "City", "width": 120},
            {"key": "is_active", "header": "Active", "width": 70},
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
            FormField("name", "Company Name", "text", required=True,
                      placeholder="e.g., Tech Supplies Inc.", max_length=255),
            FormField("contact_person", "Contact Person", "text",
                      placeholder="Full name of contact"),
            FormField("email", "Email", "text", placeholder="contact@company.com"),
            FormField("phone", "Phone", "text", placeholder="+1-555-0100"),
            FormField("address", "Address", "textarea", placeholder="Street address"),
            FormField("city", "City", "text", placeholder="City name"),
        ]

        dialog = FormDialog("Add Supplier", fields, parent=self)
        if dialog.exec() == FormDialog.Accepted:
            data = dialog.get_data()
            try:
                self.service.create(**data)
                self.refresh()
                QMessageBox.information(self, "Success", "✅ Supplier added successfully!")
            except ValidationError as e:
                QMessageBox.warning(self, "Validation Error", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add supplier: {e}")

    def _on_edit(self, row):
        fields = [
            FormField("name", "Company Name", "text", required=True, max_length=255),
            FormField("contact_person", "Contact Person", "text"),
            FormField("email", "Email", "text"),
            FormField("phone", "Phone", "text"),
            FormField("address", "Address", "textarea"),
            FormField("city", "City", "text"),
        ]

        edit_data = {
            "name": row.get("name", ""),
            "contact_person": row.get("contact_person", ""),
            "email": row.get("email", ""),
            "phone": row.get("phone", ""),
            "address": row.get("address", ""),
            "city": row.get("city", ""),
        }

        dialog = FormDialog(
            f"Edit Supplier: {row.get('name', '')}",
            fields, data=edit_data, parent=self,
        )
        if dialog.exec() == FormDialog.Accepted:
            data = dialog.get_data()
            try:
                self.service.update(row["supplier_id"], **data)
                self.refresh()
                QMessageBox.information(self, "Success", "✅ Supplier updated successfully!")
            except ValidationError as e:
                QMessageBox.warning(self, "Validation Error", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update supplier: {e}")

    def _on_delete(self):
        row = self.table.get_selected_row()
        if not row:
            QMessageBox.warning(self, "No Selection", "Please select a supplier to delete.")
            return
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete supplier '{row.get('name', '')}'?\nThis cannot be undone.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            try:
                self.service.delete(row["supplier_id"])
                self.refresh()
                QMessageBox.information(self, "Success", "✅ Supplier deleted.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete: {e}")
