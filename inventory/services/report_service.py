from datetime import date, timedelta, datetime


class ReportService:
    def __init__(self, db):
        self.db = db

    def inventory_valuation(self):
        return self.db.execute_query(
            """SELECT p.product_id, p.name, p.sku, p.cost_price, p.selling_price,
                      p.stock_quantity, 
                      (p.stock_quantity * p.cost_price) as total_cost_value,
                      (p.stock_quantity * p.selling_price) as total_sale_value,
                      c.name as category_name
               FROM products p
               LEFT JOIN categories c ON p.category_id = c.category_id
               WHERE p.is_active = TRUE
               ORDER BY total_cost_value DESC""",
            dictionary=True,
        )

    def sales_report(self, start_date=None, end_date=None, group_by="daily"):
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()

        date_format = "%Y-%m-%d"
        if group_by == "monthly":
            date_format = "%Y-%m"
        elif group_by == "yearly":
            date_format = "%Y"

        return self.db.execute_query(
            """SELECT DATE_FORMAT(s.sale_date, %s) as period,
                      COUNT(DISTINCT s.sale_id) as order_count,
                      COUNT(si.item_id) as item_count,
                      COALESCE(SUM(s.subtotal), 0) as subtotal,
                      COALESCE(SUM(s.discount), 0) as total_discount,
                      COALESCE(SUM(s.tax), 0) as total_tax,
                      COALESCE(SUM(s.grand_total), 0) as revenue,
                      COALESCE(SUM(s.grand_total) / NULLIF(COUNT(DISTINCT s.sale_id), 0), 0) as avg_order_value
               FROM sales s
               LEFT JOIN sale_items si ON s.sale_id = si.sale_id
               WHERE s.sale_date BETWEEN %s AND %s
               GROUP BY period
               ORDER BY period ASC""",
            (date_format, start_date, end_date),
            dictionary=True,
        )

    def profit_loss(self, start_date=None, end_date=None):
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()

        return self.db.execute_query(
            """SELECT s.sale_id, s.sale_date,
                      si.product_id, p.name as product_name,
                      si.quantity, si.unit_price,
                      p.cost_price,
                      (si.unit_price - p.cost_price) as unit_profit,
                      ((si.quantity * si.unit_price) - (si.quantity * p.cost_price) - COALESCE(si.discount, 0)) as total_profit
               FROM sales s
               JOIN sale_items si ON s.sale_id = si.sale_id
               JOIN products p ON si.product_id = p.product_id
               WHERE s.sale_date BETWEEN %s AND %s
               ORDER BY s.sale_date DESC""",
            (start_date, end_date),
            dictionary=True,
        )

    def profit_loss_summary(self, start_date=None, end_date=None):
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()

        result = self.db.execute_query(
            """SELECT COUNT(DISTINCT s.sale_id) as total_orders,
                      COALESCE(SUM(si.quantity * si.unit_price), 0) as total_revenue,
                      COALESCE(SUM(si.quantity * p.cost_price), 0) as total_cogs,
                      COALESCE(SUM(si.discount), 0) as total_discount,
                      COALESCE(SUM(s.tax), 0) as total_tax,
                      COALESCE(SUM((si.quantity * si.unit_price) - (si.quantity * p.cost_price) - si.discount), 0) as gross_profit,
                      COALESCE(SUM(s.grand_total), 0) as net_revenue
               FROM sales s
               JOIN sale_items si ON s.sale_id = si.sale_id
               JOIN products p ON si.product_id = p.product_id
               WHERE s.sale_date BETWEEN %s AND %s""",
            (start_date, end_date),
            dictionary=True,
        )
        return result[0] if result else {}

    def low_stock(self, threshold=None):
        if threshold is None:
            return self.db.execute_query(
                """SELECT p.product_id, p.name, p.sku, p.stock_quantity, p.min_stock_level,
                          (p.min_stock_level - p.stock_quantity) as reorder_qty,
                          c.name as category_name, p.cost_price, p.selling_price
                   FROM products p
                   LEFT JOIN categories c ON p.category_id = c.category_id
                   WHERE p.is_active = TRUE AND p.stock_quantity <= p.min_stock_level
                   ORDER BY (p.min_stock_level - p.stock_quantity) DESC""",
                dictionary=True,
            )
        return self.db.execute_query(
            """SELECT p.product_id, p.name, p.sku, p.stock_quantity, p.min_stock_level,
                      (p.min_stock_level - p.stock_quantity) as reorder_qty,
                      c.name as category_name, p.cost_price, p.selling_price
               FROM products p
               LEFT JOIN categories c ON p.category_id = c.category_id
               WHERE p.is_active = TRUE AND p.stock_quantity < %s
               ORDER BY p.stock_quantity ASC""",
            (threshold,), dictionary=True,
        )

    def best_selling_products(self, start_date=None, end_date=None, limit=10):
        if not start_date:
            start_date = date.today() - timedelta(days=90)
        if not end_date:
            end_date = date.today()

        return self.db.execute_query(
            """SELECT p.product_id, p.name, p.sku, p.selling_price,
                      COUNT(DISTINCT s.sale_id) as order_count,
                      SUM(si.quantity) as total_quantity_sold,
                      SUM(si.quantity * si.unit_price) as total_revenue,
                      SUM(si.quantity * p.cost_price) as total_cost,
                      SUM((si.quantity * si.unit_price) - (si.quantity * p.cost_price) - COALESCE(si.discount, 0)) as total_profit
               FROM sale_items si
               JOIN products p ON si.product_id = p.product_id
               JOIN sales s ON si.sale_id = s.sale_id
               WHERE s.sale_date BETWEEN %s AND %s
               GROUP BY p.product_id, p.name, p.sku, p.selling_price
               ORDER BY total_quantity_sold DESC
               LIMIT %s""",
            (start_date, end_date, limit),
            dictionary=True,
        )

    def supplier_performance(self, start_date=None, end_date=None):
        if not start_date:
            start_date = date.today() - timedelta(days=365)
        if not end_date:
            end_date = date.today()

        return self.db.execute_query(
            """SELECT s.supplier_id, s.name as supplier_name, s.email, s.phone, s.city,
                      COUNT(DISTINCT p.purchase_id) as order_count,
                      COUNT(pi.item_id) as item_count,
                      COALESCE(SUM(p.total_amount), 0) as total_spent,
                      COALESCE(AVG(p.total_amount), 0) as avg_order_value,
                      MAX(p.purchase_date) as last_order_date,
                      COALESCE(SUM(CASE WHEN p.status = 'cancelled' THEN 1 ELSE 0 END), 0) as cancelled_orders
               FROM suppliers s
               LEFT JOIN purchases p ON s.supplier_id = p.supplier_id AND p.purchase_date BETWEEN %s AND %s
               LEFT JOIN purchase_items pi ON p.purchase_id = pi.purchase_id
               GROUP BY s.supplier_id, s.name, s.email, s.phone, s.city
               ORDER BY total_spent DESC""",
            (start_date, end_date),
            dictionary=True,
        )

    def category_summary(self):
        return self.db.execute_query(
            """SELECT c.category_id, c.name as category_name,
                      COUNT(DISTINCT p.product_id) as product_count,
                      COALESCE(SUM(p.stock_quantity), 0) as total_stock,
                      COALESCE(SUM(p.stock_quantity * p.cost_price), 0) as total_cost_value,
                      COALESCE(SUM(p.stock_quantity * p.selling_price), 0) as total_sale_value,
                      COUNT(DISTINCT si.sale_id) as times_sold,
                      COALESCE(SUM(si.quantity), 0) as units_sold
               FROM categories c
               LEFT JOIN products p ON c.category_id = p.category_id AND p.is_active = TRUE
               LEFT JOIN sale_items si ON p.product_id = si.product_id
               GROUP BY c.category_id, c.name
               ORDER BY total_cost_value DESC""",
            dictionary=True,
        )

    def get_dashboard_sales_chart(self, days=7):
        start_date = date.today() - timedelta(days=days)
        return self.db.execute_query(
            """SELECT DATE(sale_date) as date,
                      COUNT(*) as order_count,
                      COALESCE(SUM(grand_total), 0) as revenue
               FROM sales
               WHERE sale_date >= %s
               GROUP BY DATE(sale_date)
               ORDER BY date ASC""",
            (start_date,), dictionary=True,
        )
