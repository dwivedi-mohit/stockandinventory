from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QMessageBox,
)
from PySide6.QtCore import Qt

from inventory.services.sale_service import SaleService
from inventory.session import session_manager
from ui.components.table_widget import DataTableView
from ui.dialogs.sale_dialog import SaleDialog


class SalesPage(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.service = SaleService(db)
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("💳 Sales")
        title.setObjectName("sectionTitle")
        header.addWidget(title)
        header.addStretch()

        self.new_sale_btn = QPushButton("➕ New Sale")
        self.new_sale_btn.setCursor(Qt.PointingHandCursor)
        self.new_sale_btn.clicked.connect(self._on_new_sale)
        header.addWidget(self.new_sale_btn)
        layout.addLayout(header)

        self.table = DataTableView(columns=[
            {"key": "sale_id", "header": "Invoice #", "width": 80, "type": "int"},
            {"key": "sale_date", "header": "Date", "width": 110},
            {"key": "customer_name", "header": "Customer", "width": 160},
            {"key": "item_count", "header": "Items", "width": 60, "type": "int"},
            {"key": "subtotal", "header": "Subtotal", "width": 100, "type": "decimal"},
            {"key": "discount", "header": "Disc", "width": 80, "type": "decimal"},
            {"key": "tax", "header": "Tax", "width": 70, "type": "decimal"},
            {"key": "grand_total", "header": "Total", "width": 110, "type": "decimal"},
            {"key": "payment_method", "header": "Payment", "width": 80},
            {"key": "user_name", "header": "Cashier", "width": 120},
        ])
        self.table.add_clicked.connect(self._on_new_sale)
        self.table.row_double_clicked.connect(self._on_view_sale)
        layout.addWidget(self.table)

    def refresh(self):
        search = self.table.get_search_text()
        try:
            data = self.service.get_all(search=search)
            self.table.set_data(data)
        except Exception:
            self.table.set_data([])

    def _on_new_sale(self):
        if not session_manager.is_authenticated:
            QMessageBox.warning(self, "Auth Required", "Please sign in first.")
            return

        dialog = SaleDialog(self.db, session_manager.current_user.user_id, parent=self)
        if dialog.exec() == SaleDialog.Accepted:
            self.refresh()

    def _on_view_sale(self, row):
        try:
            sale = self.service.get_by_id(row["sale_id"])
            items_text = "\n".join(
                "  • {} x{} @ ${:.2f}{}".format(
                    i['product_name'], i['quantity'], i['unit_price'],
                    f" (-${float(i['discount']):.2f})" if float(i['discount']) > 0 else ""
                )
                for i in sale.get("items", [])
            )
            details = (
                f"Invoice #{sale['sale_id']}\n"
                f"Date: {sale['sale_date']}\n"
                f"Customer: {sale.get('customer_name', 'Walk-in')}\n"
                f"Cashier: {sale['user_name']}\n"
                f"Payment: {sale['payment_method'].title()}\n\n"
                f"Items:\n{items_text}\n\n"
                f"Subtotal: ${float(sale['subtotal']):.2f}\n"
                f"Discount: ${float(sale['discount']):.2f}\n"
                f"Tax: ${float(sale['tax']):.2f}\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"TOTAL: ${float(sale['grand_total']):.2f}\n"
            )
            if sale.get("notes"):
                details += f"\nNotes: {sale['notes']}"

            msg = QMessageBox(self)
            msg.setWindowTitle(f"Invoice #{sale['sale_id']}")
            msg.setText(details)
            msg.setIcon(QMessageBox.Information)
            msg.addButton("Close", QMessageBox.ActionRole)
            msg.exec()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load sale: {e}")
