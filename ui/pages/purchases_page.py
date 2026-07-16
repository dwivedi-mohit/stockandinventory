from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QMessageBox, QFrame,
)
from PySide6.QtCore import Qt

from inventory.services.purchase_service import PurchaseService
from inventory.session import session_manager
from ui.components.table_widget import DataTableView
from ui.dialogs.purchase_dialog import PurchaseDialog


class PurchasesPage(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.service = PurchaseService(db)
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("🛒 Purchases")
        title.setObjectName("sectionTitle")
        header.addWidget(title)
        header.addStretch()

        self.new_purchase_btn = QPushButton("➕ New Purchase")
        self.new_purchase_btn.setCursor(Qt.PointingHandCursor)
        self.new_purchase_btn.clicked.connect(self._on_new_purchase)
        header.addWidget(self.new_purchase_btn)
        layout.addLayout(header)

        self.table = DataTableView(columns=[
            {"key": "purchase_id", "header": "ID", "width": 60, "type": "int"},
            {"key": "purchase_date", "header": "Date", "width": 110},
            {"key": "supplier_name", "header": "Supplier", "width": 180},
            {"key": "item_count", "header": "Items", "width": 60, "type": "int"},
            {"key": "total_amount", "header": "Total", "width": 110, "type": "decimal"},
            {"key": "status", "header": "Status", "width": 90},
            {"key": "user_name", "header": "Created By", "width": 130},
        ])
        self.table.add_clicked.connect(self._on_new_purchase)
        self.table.row_double_clicked.connect(self._on_view_purchase)
        layout.addWidget(self.table)

    def refresh(self):
        search = self.table.get_search_text()
        try:
            data = self.service.get_all(search=search)
            self.table.set_data(data)
        except Exception:
            self.table.set_data([])

    def _on_new_purchase(self):
        if not session_manager.is_authenticated:
            QMessageBox.warning(self, "Auth Required", "Please sign in first.")
            return

        dialog = PurchaseDialog(self.db, session_manager.current_user.user_id, parent=self)
        if dialog.exec() == PurchaseDialog.Accepted:
            self.refresh()

    def _on_view_purchase(self, row):
        try:
            purchase = self.service.get_by_id(row["purchase_id"])
            items_text = "\n".join(
                f"  • {i['product_name']} x{i['quantity']} @ ${i['unit_cost']:.2f} = ${i['quantity'] * i['unit_cost']:.2f}"
                for i in purchase.get("items", [])
            )
            details = (
                f"Purchase #{purchase['purchase_id']}\n"
                f"Date: {purchase['purchase_date']}\n"
                f"Supplier: {purchase['supplier_name']}\n"
                f"Status: {purchase['status'].title()}\n"
                f"Created by: {purchase['user_name']}\n\n"
                f"Items:\n{items_text}\n\n"
                f"Total Amount: ${float(purchase['total_amount']):.2f}\n"
            )
            if purchase.get("notes"):
                details += f"\nNotes: {purchase['notes']}"

            msg = QMessageBox(self)
            msg.setWindowTitle(f"Purchase #{purchase['purchase_id']}")
            msg.setText(details)
            msg.setIcon(QMessageBox.Information)

            if purchase["status"] != "cancelled":
                cancel_btn = msg.addButton("Cancel Purchase", QMessageBox.ActionRole)
                cancel_btn.clicked.connect(lambda: self._cancel_purchase(purchase["purchase_id"]))

            msg.addButton("Close", QMessageBox.ActionRole)
            msg.exec()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load purchase: {e}")

    def _cancel_purchase(self, purchase_id):
        reply = QMessageBox.question(
            self, "Confirm Cancel",
            "Cancel this purchase? Stock will be reduced accordingly.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            try:
                self.service.cancel(purchase_id)
                self.refresh()
                QMessageBox.information(self, "Success", "✅ Purchase cancelled.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to cancel: {e}")
