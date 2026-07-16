from inventory.exceptions import ValidationError, NotFoundError
from inventory.services.activity_service import ActivityService
from inventory.session import session_manager


class CustomerService:
    def __init__(self, db):
        self.db = db
        self._activity = ActivityService(db)

    def _log(self, action, entity_id=None, details=None):
        if session_manager.is_authenticated:
            self._activity.log(
                user_id=session_manager.current_user.user_id,
                action=action,
                entity_type="customer",
                entity_id=entity_id,
                details=details,
            )

    def get_all(self, search=""):
        query = "SELECT * FROM customers WHERE 1=1"
        params = []
        if search:
            query += " AND (name LIKE %s OR email LIKE %s OR phone LIKE %s)"
            params.extend([f"%{search}%"] * 3)
        query += " ORDER BY name ASC"
        return self.db.execute_query(query, params, dictionary=True)

    def get_by_id(self, customer_id):
        result = self.db.execute_query(
            "SELECT * FROM customers WHERE customer_id = %s",
            (customer_id,), dictionary=True,
        )
        if not result:
            raise NotFoundError("Customer")
        return result[0]

    def create(self, name, email="", phone="", address=""):
        if not name or not name.strip():
            raise ValidationError("Customer name is required.", field="name")

        self.db.execute_update(
            """INSERT INTO customers (name, email, phone, address)
               VALUES (%s, %s, %s, %s)""",
            (name.strip(), email.strip(), phone.strip(), address.strip()),
        )
        result = self.db.execute_query(
            "SELECT customer_id FROM customers WHERE name = %s ORDER BY customer_id DESC LIMIT 1",
            (name.strip(),),
        )
        customer_id = result[0]["customer_id"] if isinstance(result[0], dict) else result[0][0]
        self._log("create", customer_id, {"name": name})
        return customer_id

    def update(self, customer_id, name, email="", phone="", address=""):
        self.get_by_id(customer_id)
        self.db.execute_update(
            "UPDATE customers SET name=%s, email=%s, phone=%s, address=%s WHERE customer_id=%s",
            (name.strip(), email.strip(), phone.strip(), address.strip(), customer_id),
        )
        self._log("update", customer_id, {"name": name})

    def delete(self, customer_id):
        customer = self.get_by_id(customer_id)
        self.db.execute_update(
            "DELETE FROM customers WHERE customer_id = %s", (customer_id,)
        )
        self._log("delete", customer_id, {"name": customer["name"]})

    def get_sale_summary(self, customer_id):
        return self.db.execute_query(
            """SELECT COUNT(*) as total_purchases,
                      COALESCE(SUM(s.grand_total), 0) as total_spent,
                      MAX(s.sale_date) as last_purchase_date,
                      COALESCE(AVG(s.grand_total), 0) as avg_order_value
               FROM sales s WHERE s.customer_id = %s""",
            (customer_id,), dictionary=True,
        )[0]

    def add_loyalty_points(self, customer_id, points):
        self.db.execute_update(
            "UPDATE customers SET loyalty_points = loyalty_points + %s WHERE customer_id = %s",
            (points, customer_id),
        )
