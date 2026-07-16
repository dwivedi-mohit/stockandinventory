from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QSizePolicy, QGridLayout,
)
from PySide6.QtCore import Qt, QTimer, QEasingCurve, QMargins
from PySide6.QtGui import QFont, QColor
from PySide6.QtCharts import (
    QChart, QChartView, QBarSeries, QBarSet,
    QBarCategoryAxis, QValueAxis, QPieSeries,
)

from inventory.services.product_service import ProductService


class AnimatedMetricCard(QFrame):
    def __init__(self, title, icon, value=0, suffix="", color="#1A73E8", parent=None):
        super().__init__(parent)
        self.setObjectName("statCard")
        self.setMinimumHeight(120)
        self._target_value = 0
        self._current_value = 0
        self._suffix = suffix
        self._color = color
        self._anim_step = 0
        self._timer = QTimer()
        self._timer.timeout.connect(self._animate_step)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(4)

        header = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_font = QFont()
        icon_font.setPointSize(20)
        icon_label.setFont(icon_font)
        header.addWidget(icon_label)
        header.addStretch()
        layout.addLayout(header)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("cardLabel")
        layout.addWidget(self.title_label)

        self.value_label = QLabel("0")
        self.value_label.setObjectName("cardValue")
        val_font = QFont()
        val_font.setPointSize(28)
        val_font.setWeight(QFont.Bold)
        self.value_label.setFont(val_font)
        self.value_label.setStyleSheet(f"color: {color};")
        layout.addWidget(self.value_label)

    def set_value(self, value, animate=True):
        self._target_value = int(value) if isinstance(value, (int, float)) else 0
        if animate and self._current_value != self._target_value:
            self._anim_step = 0
            self._start_value = self._current_value
            self._timer.start(16)
        else:
            self._current_value = self._target_value
            self.value_label.setText(f"{self._current_value:,}{self._suffix}")

    def _animate_step(self):
        self._anim_step += 1
        progress = min(self._anim_step / 50, 1.0)
        eased = 1 - pow(1 - progress, 3)
        self._current_value = int(
            self._start_value + (self._target_value - self._start_value) * eased
        )
        self.value_label.setText(f"{self._current_value:,}{self._suffix}")
        if progress >= 1.0:
            self._timer.stop()
            self._current_value = self._target_value
            self.value_label.setText(f"{self._current_value:,}{self._suffix}")


class DashboardPage(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.service = ProductService(db)
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        header_row = QHBoxLayout()
        title = QLabel("📊 Dashboard")
        title.setObjectName("sectionTitle")
        header_row.addWidget(title)

        self.refresh_btn = QLabel("")
        self.refresh_btn.setStyleSheet("color: #888; font-size: 12px;")
        header_row.addWidget(self.refresh_btn)
        header_row.addStretch()

        layout.addLayout(header_row)

        cards_grid = QGridLayout()
        cards_grid.setSpacing(16)

        self.product_card = AnimatedMetricCard("Total Products", "📦", color="#1A73E8")
        cards_grid.addWidget(self.product_card, 0, 0)

        self.stock_card = AnimatedMetricCard("Total Items in Stock", "📊", color="#4CAF50")
        cards_grid.addWidget(self.stock_card, 0, 1)

        self.value_card = AnimatedMetricCard("Inventory Value", "💰", suffix="$", color="#FF9800")
        cards_grid.addWidget(self.value_card, 0, 2)

        self.low_stock_card = AnimatedMetricCard("Low Stock Alerts", "⚠️", color="#F44336")
        cards_grid.addWidget(self.low_stock_card, 0, 3)

        layout.addLayout(cards_grid)

        charts_row = QHBoxLayout()
        charts_row.setSpacing(16)

        self.stock_chart_frame = QFrame()
        self.stock_chart_frame.setObjectName("card")
        stock_chart_layout = QVBoxLayout(self.stock_chart_frame)
        stock_chart_label = QLabel("📦 Stock by Product")
        stock_chart_label.setObjectName("cardLabel")
        stock_chart_layout.addWidget(stock_chart_label)

        self.stock_chart_view = self._create_chart_view()
        stock_chart_layout.addWidget(self.stock_chart_view)
        charts_row.addWidget(self.stock_chart_frame)

        self.value_chart_frame = QFrame()
        self.value_chart_frame.setObjectName("card")
        value_chart_layout = QVBoxLayout(self.value_chart_frame)
        value_chart_label = QLabel("💰 Inventory Value by Product")
        value_chart_label.setObjectName("cardLabel")
        value_chart_layout.addWidget(value_chart_label)

        self.value_chart_view = self._create_chart_view()
        value_chart_layout.addWidget(self.value_chart_view)
        charts_row.addWidget(self.value_chart_frame)

        layout.addLayout(charts_row)

    def _create_chart_view(self):
        chart = QChart()
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setBackgroundBrush(Qt.transparent)
        chart.setMargins(QMargins(0, 0, 0, 0))
        chart.legend().setVisible(False)
        chart_view = QChartView(chart)
        chart_view.setRenderHint(chart_view.renderHint())
        chart_view.setMinimumHeight(250)
        return chart_view

    def refresh(self):
        try:
            stats = self.service.get_dashboard_stats()
            self.product_card.set_value(stats.get("count", 0))
            self.stock_card.set_value(stats.get("total_stock", 0))
            self.value_card.set_value(int(stats.get("total_value", 0)))
            self.low_stock_card.set_value(stats.get("low_stock_count", 0))
            self._update_charts()
            self.refresh_btn.setText("Auto-refreshing every 30s")
        except Exception:
            pass

    def _update_charts(self):
        try:
            products = self.service.get_all()
            self._update_bar_chart(
                self.stock_chart_view,
                "Stock Quantity",
                [(p["name"][:12], float(p["stock_quantity"])) for p in products[:12]
                 if float(p["stock_quantity"]) > 0],
            )
            self._update_bar_chart(
                self.value_chart_view,
                "Inventory Value",
                [(p["name"][:12], float(p["stock_quantity"] * p["cost_price"])) for p in products[:12]
                 if float(p["stock_quantity"] * p["cost_price"]) > 0],
            )
        except Exception:
            pass

    def _update_bar_chart(self, chart_view, title, data):
        chart = chart_view.chart()
        chart.removeAllSeries()
        for axis in chart.axes():
            chart.removeAxis(axis)
        if not data:
            return

        series = QBarSeries()
        bar_set = QBarSet(title)
        bar_set.setColor(QColor("#1A73E8"))
        categories = []
        for name, value in data:
            bar_set.append(value)
            categories.append(name)

        series.append(bar_set)
        chart.addSeries(series)

        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        axis_x.setLabelsAngle(-45)
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setRange(0, max([v for _, v in data]) * 1.1 if data else 1)
        axis_y.setLabelFormat("%.0f")
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
