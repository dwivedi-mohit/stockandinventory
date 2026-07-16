from datetime import date
from inventory.exceptions import ValidationError, NotFoundError, InsufficientStockError
from inventory.services.activity_service import ActivityService
from inventory.session import session_manager


class SaleService:
    def __init__(self, db):
        self.db = db
        self._activity = ActivityService(db)

    def _log(self, action, entity_id=None, details=None):
        if session_manager.is_authenticated:
            self._activity.log(
                user_id=session_manager.current_user.user_id,
                action=action,
                entity_type="sale",
                entity_id=entity_id,
                details=details,
            )

    def get_all(self, search=""):
        query = """SELECT s.sale_id, s.sale_date, s.subtotal, s.discount, s.tax,
                          s.grand_total, s.payment_method,
                          c.name as customer_name, u.username as user_name,
                          COUNT(si.item_id) as item_count
                   FROM sales s
                   LEFT JOIN customers c ON s.customer_id = c.customer_id
                   JOIN users u ON s.user_id = u.user_id
                   LEFT JOIN sale_items si ON s.sale_id = si.sale_id
                   WHERE 1=1"""
        params = []
        if search:
            query += " AND (c.name LIKE %s OR s.sale_id LIKE %s)"
            params.extend([f"%{search}%", f"%{search}%"])
        query += " GROUP BY s.sale_id ORDER BY s.sale_id DESC"
        return self.db.execute_query(query, params, dictionary=True)

    def get_by_id(self, sale_id):
        sale = self.db.execute_query(
            """SELECT s.*, c.name as customer_name, u.username as user_name
               FROM sales s
               LEFT JOIN customers c ON s.customer_id = c.customer_id
               JOIN users u ON s.user_id = u.user_id
               WHERE s.sale_id = %s""",
            (sale_id,), dictionary=True,
        )
        if not sale:
            raise NotFoundError("Sale")
        sale = sale[0]

        items = self.db.execute_query(
            """SELECT si.*, pr.name as product_name, pr.sku
               FROM sale_items si
               JOIN products pr ON si.product_id = pr.product_id
               WHERE si.sale_id = %s""",
            (sale_id,), dictionary=True,
        )
        sale["items"] = items
        return sale

    def create(self, user_id, items, customer_id=None, discount=0, tax=0,
               payment_method="cash", sale_date=None, notes=""):
        if not items:
            raise ValidationError("Sale must have at least one item.")

        if sale_date is None:
            sale_date = date.today()

        subtotal = 0.0
        validated_items = []

        for item in items:
            product_id = item["product_id"]
            quantity = int(item.get("quantity", 0))
            unit_price = float(item.get("unit_price", 0))
            item_discount = float(item.get("discount", 0))

            product = self.db.execute_query(
                "SELECT product_id, name, stock_quantity, selling_price FROM products WHERE product_id = %s",
                (product_id,), dictionary=True,
            )
            if not product or not product[0]:
                raise NotFoundError(f"Product ID {product_id}")
            product = product[0]

            if quantity > product["stock_quantity"]:
                raise InsufficientStockError(
                    product_name=product["name"],
                    available=product["stock_quantity"],
                    requested=quantity,
                )

            line_total = (quantity * unit_price) - item_discount
            subtotal += line_total

            validated_items.append({
                "product_id": product_id,
                "quantity": quantity,
                "unit_price": unit_price,
                "discount": item_discount,
                "total_price": line_total,
            })

        grand_total = subtotal - discount + tax

        conn = None
        cursor = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.start_transaction()

            cursor.execute(
                """INSERT INTO sales (customer_id, user_id, sale_date, subtotal, discount, tax,
                                      grand_total, payment_method, notes)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (customer_id, user_id, sale_date, subtotal, discount, tax, grand_total, payment_method, notes),
            )
            sale_id = cursor.lastrowid

            for item in validated_items:
                cursor.execute(
                    """INSERT INTO sale_items (sale_id, product_id, quantity, unit_price, discount)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (sale_id, item["product_id"], item["quantity"], item["unit_price"], item["discount"]),
                )
                cursor.execute(
                    "UPDATE products SET stock_quantity = stock_quantity - %s WHERE product_id = %s",
                    (item["quantity"], item["product_id"]),
                )

            if customer_id:
                points = int(grand_total / 10)
                cursor.execute(
                    "UPDATE customers SET loyalty_points = loyalty_points + %s WHERE customer_id = %s",
                    (points, customer_id),
                )

            conn.commit()
            self._log("create", sale_id, {
                "customer_id": customer_id,
                "grand_total": grand_total,
                "item_count": len(items),
                "payment_method": payment_method,
            })
            return sale_id

        except Exception:
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

    def process_return(self, sale_id, product_id, quantity, reason=""):
        sale = self.get_by_id(sale_id)

        item_found = None
        for item in sale.get("items", []):
            if item["product_id"] == product_id:
                item_found = item
                break

        if not item_found:
            raise NotFoundError("Sale item")

        if quantity > item_found["quantity"]:
            raise ValidationError(
                f"Cannot return more than {item_found['quantity']} units (sold quantity)."
            )

        conn = None
        cursor = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.start_transaction()

            cursor.execute(
                """INSERT INTO returns (sale_id, product_id, quantity, reason, return_date)
                   VALUES (%s, %s, %s, %s, CURDATE())""",
                (sale_id, product_id, quantity, reason),
            )

            cursor.execute(
                "UPDATE products SET stock_quantity = stock_quantity + %s WHERE product_id = %s",
                (quantity, product_id),
            )

            conn.commit()
            self._log("return", sale_id, {
                "product_id": product_id,
                "quantity": quantity,
                "reason": reason,
            })
            return cursor.lastrowid

        except Exception:
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

    def get_dashboard_stats(self):
        result = self.db.execute_query(
            "SELECT COUNT(*) as count, COALESCE(SUM(grand_total), 0) as total "
            "FROM sales",
            dictionary=True,
        )
        return result[0] if result else {"count": 0, "total": 0}
