from inventory.exceptions import ValidationError, NotFoundError
from inventory.services.activity_service import ActivityService
from inventory.session import session_manager


class ProductService:
    def __init__(self, db):
        self.db = db
        self._activity = ActivityService(db)

    def _log(self, action, entity_id=None, details=None):
        if session_manager.is_authenticated:
            self._activity.log(
                user_id=session_manager.current_user.user_id,
                action=action,
                entity_type="product",
                entity_id=entity_id,
                details=details,
            )

    def get_all(self, search="", category_id=None, low_stock=False):
        query = """SELECT p.product_id, p.name, p.sku, p.barcode,
                          c.name as category_name, p.cost_price, p.selling_price,
                          p.stock_quantity, p.min_stock_level, p.is_active
                   FROM products p
                   LEFT JOIN categories c ON p.category_id = c.category_id
                   WHERE 1=1"""
        params = []

        if search:
            query += " AND (p.name LIKE %s OR p.sku LIKE %s OR p.barcode LIKE %s)"
            params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

        if category_id:
            query += " AND p.category_id = %s"
            params.append(category_id)

        if low_stock:
            query += " AND p.stock_quantity <= p.min_stock_level"

        query += " ORDER BY p.product_id DESC"

        return self.db.execute_query(query, params, dictionary=True)

    def get_by_id(self, product_id):
        result = self.db.execute_query(
            """SELECT p.*, c.name as category_name
               FROM products p
               LEFT JOIN categories c ON p.category_id = c.category_id
               WHERE p.product_id = %s""",
            (product_id,),
            dictionary=True,
        )
        if not result:
            raise NotFoundError("Product")
        return result[0]

    def create(self, name, sku, selling_price, cost_price=0, category_id=None,
               stock_quantity=0, min_stock_level=10, barcode="", description=""):
        existing = self.db.execute_query(
            "SELECT product_id FROM products WHERE sku = %s", (sku,)
        )
        if existing:
            raise ValidationError(f"A product with SKU '{sku}' already exists.", field="sku")

        existing = self.db.execute_query(
            "SELECT product_id FROM products WHERE barcode = %s AND barcode != ''",
            (barcode,),
        )
        if barcode and existing:
            raise ValidationError(f"A product with barcode '{barcode}' already exists.", field="barcode")

        self.db.execute_update(
            """INSERT INTO products (name, sku, barcode, category_id, cost_price,
                                     selling_price, stock_quantity, min_stock_level, description)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (name, sku, barcode, category_id, cost_price,
             selling_price, stock_quantity, min_stock_level, description),
        )

        result = self.db.execute_query(
            "SELECT product_id FROM products WHERE sku = %s", (sku,)
        )
        product_id = result[0]["product_id"] if isinstance(result[0], dict) else result[0][0]
        self._log("create", product_id, {"name": name, "sku": sku})
        return product_id

    def update(self, product_id, name, selling_price, cost_price=None,
               category_id=None, min_stock_level=10, barcode="", description="",
               is_active=True):
        product = self.get_by_id(product_id)

        self.db.execute_update(
            """UPDATE products SET name=%s, selling_price=%s, cost_price=%s,
               category_id=%s, min_stock_level=%s, barcode=%s, description=%s,
               is_active=%s
               WHERE product_id=%s""",
            (name, selling_price, cost_price if cost_price is not None else product["cost_price"],
             category_id, min_stock_level, barcode, description, is_active, product_id),
        )
        self._log("update", product_id, {"name": name})

    def delete(self, product_id):
        product = self.get_by_id(product_id)
        self.db.execute_update("DELETE FROM products WHERE product_id = %s", (product_id,))
        self._log("delete", product_id, {"name": product["name"]})

    def update_stock(self, product_id, quantity):
        self.db.execute_update(
            "UPDATE products SET stock_quantity = stock_quantity + %s WHERE product_id = %s",
            (quantity, product_id),
        )

    def get_low_stock(self):
        return self.db.execute_query(
            """SELECT p.product_id, p.name, p.sku, p.stock_quantity, p.min_stock_level
               FROM products p WHERE p.stock_quantity <= p.min_stock_level
               ORDER BY (p.min_stock_level - p.stock_quantity) DESC""",
            dictionary=True,
        )

    def get_dashboard_stats(self):
        total = self.db.execute_query(
            "SELECT COUNT(*) as count, COALESCE(SUM(stock_quantity), 0) as total_stock, "
            "COALESCE(SUM(stock_quantity * cost_price), 0) as total_value "
            "FROM products", dictionary=True
        )
        low_stock = self.db.execute_query(
            "SELECT COUNT(*) as count FROM products WHERE stock_quantity <= min_stock_level",
            dictionary=True
        )
        categories = self.db.execute_query(
            "SELECT COUNT(*) as count FROM categories", dictionary=True
        )
        stats = total[0] if total else {"count": 0, "total_stock": 0, "total_value": 0}
        stats["low_stock_count"] = low_stock[0]["count"] if low_stock else 0
        stats["category_count"] = categories[0]["count"] if categories else 0
        return stats

    def generate_sku(self, category_id=None):
        prefix = "PRD"
        if category_id:
            cat = self.db.execute_query(
                "SELECT name FROM categories WHERE category_id = %s", (category_id,)
            )
            if cat:
                prefix = cat[0]["name"][:3].upper() if isinstance(cat[0], dict) else cat[0][:3].upper()
        result = self.db.execute_query(
            "SELECT COUNT(*) as c FROM products WHERE sku LIKE %s", (f"{prefix}-%",)
        )
        count = result[0]["c"] if isinstance(result[0], dict) else result[0][0]
        return f"{prefix}-{count + 1:04d}"
