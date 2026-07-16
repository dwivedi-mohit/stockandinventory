import os
from datetime import date, timedelta
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QDateEdit, QFrame, QFileDialog, QMessageBox,
    QProgressBar, QSizePolicy,
)
from PySide6.QtCore import Qt, QDate, QTimer
from PySide6.QtGui import QFont

from inventory.services.report_service import ReportService
from inventory.services.export_service import ExportService
from ui.components.table_widget import DataTableView


REPORT_TYPES = [
    ("Inventory Valuation", "inventory_valuation"),
    ("Sales Report", "sales_report"),
    ("Profit & Loss", "profit_loss"),
    ("Low Stock Report", "low_stock"),
    ("Best Selling Products", "best_selling"),
    ("Supplier Performance", "supplier_performance"),
    ("Category Summary", "category_summary"),
]

REPORT_HEADERS = {
    "inventory_valuation": ["product_id", "name", "sku", "category_name",
                            "cost_price", "selling_price", "stock_quantity",
                            "total_cost_value", "total_sale_value"],
    "sales_report": ["period", "order_count", "item_count", "subtotal",
                     "total_discount", "total_tax", "revenue", "avg_order_value"],
    "profit_loss": ["sale_id", "sale_date", "product_name", "quantity",
                    "unit_price", "cost_price", "unit_profit", "total_profit"],
    "low_stock": ["product_id", "name", "sku", "category_name",
                  "stock_quantity", "min_stock_level", "reorder_qty",
                  "cost_price", "selling_price"],
    "best_selling": ["product_id", "name", "sku", "order_count",
                     "total_quantity_sold", "total_revenue", "total_cost", "total_profit"],
    "supplier_performance": ["supplier_id", "supplier_name", "email", "phone", "city",
                             "order_count", "item_count", "total_spent",
                             "avg_order_value", "last_order_date", "cancelled_orders"],
    "category_summary": ["category_id", "category_name", "product_count",
                         "total_stock", "total_cost_value", "total_sale_value",
                         "times_sold", "units_sold"],
}

REPORT_DISPLAY_HEADERS = {
    "inventory_valuation": [
        {"key": "product_id", "header": "ID", "width": 50, "type": "int"},
        {"key": "name", "header": "Product", "width": 180},
        {"key": "sku", "header": "SKU", "width": 90},
        {"key": "category_name", "header": "Category", "width": 100},
        {"key": "cost_price", "header": "Cost", "width": 80, "type": "decimal"},
        {"key": "selling_price", "header": "Sell Price", "width": 80, "type": "decimal"},
        {"key": "stock_quantity", "header": "Stock", "width": 60, "type": "int"},
        {"key": "total_cost_value", "header": "Cost Value", "width": 100, "type": "decimal"},
        {"key": "total_sale_value", "header": "Sale Value", "width": 100, "type": "decimal"},
    ],
    "sales_report": [
        {"key": "period", "header": "Period", "width": 100},
        {"key": "order_count", "header": "Orders", "width": 70, "type": "int"},
        {"key": "item_count", "header": "Items", "width": 60, "type": "int"},
        {"key": "subtotal", "header": "Subtotal", "width": 90, "type": "decimal"},
        {"key": "total_discount", "header": "Discount", "width": 80, "type": "decimal"},
        {"key": "total_tax", "header": "Tax", "width": 70, "type": "decimal"},
        {"key": "revenue", "header": "Revenue", "width": 100, "type": "decimal"},
        {"key": "avg_order_value", "header": "Avg Order", "width": 90, "type": "decimal"},
    ],
    "profit_loss": [
        {"key": "sale_id", "header": "Sale #", "width": 60, "type": "int"},
        {"key": "sale_date", "header": "Date", "width": 90},
        {"key": "product_name", "header": "Product", "width": 180},
        {"key": "quantity", "header": "Qty", "width": 50, "type": "int"},
        {"key": "unit_price", "header": "Price", "width": 80, "type": "decimal"},
        {"key": "cost_price", "header": "Cost", "width": 80, "type": "decimal"},
        {"key": "unit_profit", "header": "Unit Profit", "width": 90, "type": "decimal"},
        {"key": "total_profit", "header": "Total Profit", "width": 100, "type": "decimal"},
    ],
    "low_stock": [
        {"key": "product_id", "header": "ID", "width": 50, "type": "int"},
        {"key": "name", "header": "Product", "width": 180},
        {"key": "sku", "header": "SKU", "width": 90},
        {"key": "category_name", "header": "Category", "width": 100},
        {"key": "stock_quantity", "header": "Stock", "width": 60, "type": "int"},
        {"key": "min_stock_level", "header": "Min", "width": 50, "type": "int"},
        {"key": "reorder_qty", "header": "Reorder", "width": 70, "type": "int"},
        {"key": "cost_price", "header": "Cost", "width": 80, "type": "decimal"},
        {"key": "selling_price", "header": "Price", "width": 80, "type": "decimal"},
    ],
    "best_selling": [
        {"key": "product_id", "header": "ID", "width": 50, "type": "int"},
        {"key": "name", "header": "Product", "width": 180},
        {"key": "sku", "header": "SKU", "width": 90},
        {"key": "order_count", "header": "Orders", "width": 70, "type": "int"},
        {"key": "total_quantity_sold", "header": "Qty Sold", "width": 80, "type": "int"},
        {"key": "total_revenue", "header": "Revenue", "width": 100, "type": "decimal"},
        {"key": "total_cost", "header": "Cost", "width": 90, "type": "decimal"},
        {"key": "total_profit", "header": "Profit", "width": 100, "type": "decimal"},
    ],
    "supplier_performance": [
        {"key": "supplier_id", "header": "ID", "width": 50, "type": "int"},
        {"key": "supplier_name", "header": "Supplier", "width": 160},
        {"key": "email", "header": "Email", "width": 160},
        {"key": "phone", "header": "Phone", "width": 110},
        {"key": "city", "header": "City", "width": 90},
        {"key": "order_count", "header": "Orders", "width": 70, "type": "int"},
        {"key": "total_spent", "header": "Total Spent", "width": 100, "type": "decimal"},
        {"key": "avg_order_value", "header": "Avg Order", "width": 90, "type": "decimal"},
        {"key": "last_order_date", "header": "Last Order", "width": 90},
        {"key": "cancelled_orders", "header": "Cancelled", "width": 80, "type": "int"},
    ],
    "category_summary": [
        {"key": "category_id", "header": "ID", "width": 50, "type": "int"},
        {"key": "category_name", "header": "Category", "width": 140},
        {"key": "product_count", "header": "Products", "width": 70, "type": "int"},
        {"key": "total_stock", "header": "Stock", "width": 70, "type": "int"},
        {"key": "total_cost_value", "header": "Cost Value", "width": 100, "type": "decimal"},
        {"key": "total_sale_value", "header": "Sale Value", "width": 100, "type": "decimal"},
        {"key": "units_sold", "header": "Units Sold", "width": 80, "type": "int"},
    ],
}


class ReportsPage(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.service = ReportService(db)
        self.export_service = ExportService(db)
        self._current_data = []
        self._current_headers = []
        self._current_report_key = ""
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("📈 Reports & Analytics")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        controls_frame = QFrame()
        controls_frame.setObjectName("card")
        controls = QVBoxLayout(controls_frame)
        controls.setSpacing(12)
        controls.setContentsMargins(16, 16, 16, 16)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Report Type:"))
        self.report_combo = QComboBox()
        self.report_combo.setMinimumWidth(200)
        for label, key in REPORT_TYPES:
            self.report_combo.addItem(label, key)
        self.report_combo.currentIndexChanged.connect(self._on_report_type_changed)
        row1.addWidget(self.report_combo)

        row1.addSpacing(20)
        row1.addWidget(QLabel("From:"))
        self.start_date = QDateEdit(QDate.currentDate().addDays(-30))
        self.start_date.setCalendarPopup(True)
        row1.addWidget(self.start_date)

        row1.addWidget(QLabel("To:"))
        self.end_date = QDateEdit(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        row1.addWidget(self.end_date)

        row1.addSpacing(10)
        row1.addWidget(QLabel("Group:"))
        self.group_combo = QComboBox()
        self.group_combo.addItems(["daily", "monthly", "yearly"])
        self.group_combo.setVisible(False)
        row1.addWidget(self.group_combo)

        row1.addStretch()
        self.generate_btn = QPushButton("🔄 Generate")
        self.generate_btn.setCursor(Qt.PointingHandCursor)
        self.generate_btn.clicked.connect(self._generate_report)
        row1.addWidget(self.generate_btn)

        controls.addLayout(row1)

        export_row = QHBoxLayout()
        export_row.addWidget(QLabel("Export:"))

        self.pdf_btn = QPushButton("📄 PDF")
        self.pdf_btn.setCursor(Qt.PointingHandCursor)
        self.pdf_btn.clicked.connect(lambda: self._export("pdf"))
        self.pdf_btn.setEnabled(False)
        export_row.addWidget(self.pdf_btn)

        self.excel_btn = QPushButton("📊 Excel")
        self.excel_btn.setCursor(Qt.PointingHandCursor)
        self.excel_btn.clicked.connect(lambda: self._export("excel"))
        self.excel_btn.setEnabled(False)
        export_row.addWidget(self.excel_btn)

        self.csv_btn = QPushButton("📃 CSV")
        self.csv_btn.setCursor(Qt.PointingHandCursor)
        self.csv_btn.clicked.connect(lambda: self._export("csv"))
        self.csv_btn.setEnabled(False)
        export_row.addWidget(self.csv_btn)

        export_row.addStretch()
        self.summary_label = QLabel("")
        self.summary_label.setStyleSheet("font-weight: 600; font-size: 13px;")
        export_row.addWidget(self.summary_label)
        controls.addLayout(export_row)

        layout.addWidget(controls_frame)

        self.table = DataTableView()
        layout.addWidget(self.table)

        self._on_report_type_changed()

    def _on_report_type_changed(self):
        key = self.report_combo.currentData()
        needs_dates = key in ("sales_report", "profit_loss", "best_selling", "supplier_performance")
        controls_frame = self.layout().itemAt(0).widget()
        for label in controls_frame.findChildren(QLabel):
            if label.text() in ("From:", "To:"):
                label.setVisible(needs_dates)
        self.start_date.setVisible(needs_dates)
        self.end_date.setVisible(needs_dates)

        is_sales = key == "sales_report"
        self.group_combo.setVisible(is_sales)

    def refresh(self):
        pass

    def _generate_report(self):
        key = self.report_combo.currentData()
        self._current_report_key = key

        try:
            start = self.start_date.date().toPython()
            end = self.end_date.date().toPython()
        except Exception:
            start = date.today() - timedelta(days=30)
            end = date.today()

        self.generate_btn.setEnabled(False)
        self.generate_btn.setText("Generating...")

        QTimer.singleShot(100, lambda: self._do_generate(key, start, end))

    def _do_generate(self, key, start, end):
        try:
            data = []
            headers = REPORT_HEADERS.get(key, [])
            display_headers = REPORT_DISPLAY_HEADERS.get(key, [])

            if key == "inventory_valuation":
                data = self.service.inventory_valuation()
            elif key == "sales_report":
                group = self.group_combo.currentText()
                data = self.service.sales_report(start, end, group)
            elif key == "profit_loss":
                data = self.service.profit_loss(start, end)
            elif key == "low_stock":
                data = self.service.low_stock()
            elif key == "best_selling":
                data = self.service.best_selling_products(start, end)
            elif key == "supplier_performance":
                data = self.service.supplier_performance(start, end)
            elif key == "category_summary":
                data = self.service.category_summary()

            self._current_data = data
            self._current_headers = headers

            self.table.set_columns(display_headers)
            self.table.set_data(data)

            self._update_summary(key, data)
            self.pdf_btn.setEnabled(bool(data))
            self.excel_btn.setEnabled(bool(data))
            self.csv_btn.setEnabled(bool(data))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {e}")
            self._current_data = []
            self._current_headers = []
            self.table.set_data([])

        finally:
            self.generate_btn.setEnabled(True)
            self.generate_btn.setText("🔄 Generate")

    def _update_summary(self, key, data):
        if not data:
            self.summary_label.setText("No data found")
            return

        count = len(data)
        if key == "inventory_valuation":
            total_value = sum(float(r.get("total_cost_value", 0) or 0) for r in data)
            self.summary_label.setText(f"{count} products | Total Value: ${total_value:,.2f}")
        elif key == "sales_report":
            revenue = sum(float(r.get("revenue", 0) or 0) for r in data)
            orders = sum(int(r.get("order_count", 0) or 0) for r in data)
            self.summary_label.setText(f"{count} periods | {orders} orders | Revenue: ${revenue:,.2f}")
        elif key == "profit_loss":
            total_profit = sum(float(r.get("total_profit", 0) or 0) for r in data)
            self.summary_label.setText(f"{count} transactions | Total Profit: ${total_profit:,.2f}")
        elif key == "low_stock":
            self.summary_label.setText(f"⚠️ {count} products below minimum stock level")
        elif key == "best_selling":
            total_rev = sum(float(r.get("total_revenue", 0) or 0) for r in data)
            self.summary_label.setText(f"Top {count} products | Revenue: ${total_rev:,.2f}")
        elif key == "supplier_performance":
            total = sum(float(r.get("total_spent", 0) or 0) for r in data)
            self.summary_label.setText(f"{count} suppliers | Total Spent: ${total:,.2f}")
        elif key == "category_summary":
            self.summary_label.setText(f"{count} categories")
        else:
            self.summary_label.setText(f"{count} rows")

    def _export(self, fmt):
        if not self._current_data:
            QMessageBox.warning(self, "No Data", "Generate a report first.")
            return

        key = self._current_report_key
        report_name = next((label for label, k in REPORT_TYPES if k == key), key)
        headers = self._current_headers
        display_names = [h["header"] for h in REPORT_DISPLAY_HEADERS.get(key, [])]

        export_data = []
        for row in self._current_data:
            export_row = {}
            for h in headers:
                export_row[h] = row.get(h, "")
            export_data.append(export_row)

        if fmt == "pdf":
            filepath, _ = QFileDialog.getSaveFileName(
                self, f"Export {report_name} as PDF",
                f"{report_name}_{date.today()}.pdf",
                "PDF Files (*.pdf)",
            )
            if filepath:
                try:
                    self.export_service.to_pdf(
                        export_data, display_names, filepath,
                        title=report_name,
                        subtitle=f"Generated: {date.today()}",
                    )
                    QMessageBox.information(self, "Success", f"✅ PDF exported to:\n{filepath}")
                except Exception as e:
                    QMessageBox.critical(self, "Export Error", f"Failed to export PDF: {e}")

        elif fmt == "excel":
            filepath, _ = QFileDialog.getSaveFileName(
                self, f"Export {report_name} as Excel",
                f"{report_name}_{date.today()}.xlsx",
                "Excel Files (*.xlsx)",
            )
            if filepath:
                try:
                    self.export_service.to_excel(
                        export_data, display_names, filepath,
                        title=report_name,
                    )
                    QMessageBox.information(self, "Success", f"✅ Excel exported to:\n{filepath}")
                except Exception as e:
                    QMessageBox.critical(self, "Export Error", f"Failed to export Excel: {e}")

        elif fmt == "csv":
            filepath, _ = QFileDialog.getSaveFileName(
                self, f"Export {report_name} as CSV",
                f"{report_name}_{date.today()}.csv",
                "CSV Files (*.csv)",
            )
            if filepath:
                try:
                    self.export_service.to_csv(
                        export_data, display_names, filepath,
                    )
                    QMessageBox.information(self, "Success", f"✅ CSV exported to:\n{filepath}")
                except Exception as e:
                    QMessageBox.critical(self, "Export Error", f"Failed to export CSV: {e}")
