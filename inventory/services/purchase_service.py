from datetime import date
from inventory.exceptions import ValidationError, NotFoundError
from inventory.services.activity_service import ActivityService
from inventory.session import session_manager


class PurchaseService:
    def __init__(self, db):
        self.db = db
        self._activity = ActivityService(db)

    def _log(self, action, entity_id=None, details=None):
        if session_manager.is_authenticated:
            self._activity.log(
                user_id=session_manager.current_user.user_id,
                action=action,
                entity_type="purchase",
                entity_id=entity_id,
                details=details,
            )

    def get_all(self, search=""):
        query = """SELECT p.purchase_id, p.purchase_date, p.total_amount, p.status,
                          s.name as supplier_name, u.username as user_name,
                          COUNT(pi.item_id) as item_count
                   FROM purchases p
                   JOIN suppliers s ON p.supplier_id = s.supplier_id
                   JOIN users u ON p.user_id = u.user_id
                   LEFT JOIN purchase_items pi ON p.purchase_id = pi.purchase_id
                   WHERE 1=1"""
        params = []
        if search:
            query += " AND (s.name LIKE %s OR p.purchase_id LIKE %s)"
            params.extend([f"%{search}%", f"%{search}%"])
        query += " GROUP BY p.purchase_id ORDER BY p.purchase_id DESC"
        return self.db.execute_query(query, params, dictionary=True)

    def get_by_id(self, purchase_id):
        purchase = self.db.execute_query(
            """SELECT p.*, s.name as supplier_name, s.supplier_id, u.username as user_name
               FROM purchases p
               JOIN suppliers s ON p.supplier_id = s.supplier_id
               JOIN users u ON p.user_id = u.user_id
               WHERE p.purchase_id = %s""",
            (purchase_id,), dictionary=True,
        )
        if not purchase:
            raise NotFoundError("Purchase")
        purchase = purchase[0]

        items = self.db.execute_query(
            """SELECT pi.*, pr.name as product_name, pr.sku
               FROM purchase_items pi
               JOIN products pr ON pi.product_id = pr.product_id
               WHERE pi.purchase_id = %s""",
            (purchase_id,), dictionary=True,
        )
        purchase["items"] = items
        return purchase

    def create(self, supplier_id, user_id, items, purchase_date=None, notes=""):
        if not items:
            raise ValidationError("Purchase must have at least one item.")

        if purchase_date is None:
            purchase_date = date.today()

        total_amount = sum(
            (float(item.get("unit_cost", 0)) * int(item.get("quantity", 0)))
            for item in items
        )

        conn = None
        cursor = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.start_transaction()

            cursor.execute(
                """INSERT INTO purchases (supplier_id, user_id, purchase_date, total_amount, status, notes)
                   VALUES (%s, %s, %s, %s, 'received', %s)""",
                (supplier_id, user_id, purchase_date, total_amount, notes),
            )
            purchase_id = cursor.lastrowid

            for item in items:
                cursor.execute(
                    """INSERT INTO purchase_items (purchase_id, product_id, quantity, unit_cost)
                       VALUES (%s, %s, %s, %s)""",
                    (purchase_id, item["product_id"], item["quantity"], item["unit_cost"]),
                )
                cursor.execute(
                    "UPDATE products SET stock_quantity = stock_quantity + %s WHERE product_id = %s",
                    (item["quantity"], item["product_id"]),
                )

            conn.commit()
            self._log("create", purchase_id, {
                "supplier_id": supplier_id,
                "total_amount": total_amount,
                "item_count": len(items),
            })
            return purchase_id

        except Exception:
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

    def cancel(self, purchase_id):
        purchase = self.get_by_id(purchase_id)
        if purchase["status"] == "cancelled":
            raise ValidationError("Purchase is already cancelled.")

        conn = None
        cursor = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.start_transaction()

            for item in purchase.get("items", []):
                cursor.execute(
                    "UPDATE products SET stock_quantity = stock_quantity - %s WHERE product_id = %s",
                    (item["quantity"], item["product_id"]),
                )

            cursor.execute(
                "UPDATE purchases SET status = 'cancelled' WHERE purchase_id = %s",
                (purchase_id,),
            )

            conn.commit()
            self._log("cancel", purchase_id, {
                "supplier_id": purchase.get("supplier_id"),
                "total_amount": purchase.get("total_amount"),
            })

        except Exception:
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

    def get_dashboard_stats(self):
        result = self.db.execute_query(
            "SELECT COUNT(*) as count, COALESCE(SUM(total_amount), 0) as total "
            "FROM purchases WHERE status = 'received'",
            dictionary=True,
        )
        return result[0] if result else {"count": 0, "total": 0}
