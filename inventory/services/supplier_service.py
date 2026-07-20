from inventory.exceptions import ValidationError, NotFoundError
from inventory.services.base_service import BaseService


class SupplierService(BaseService):
    def __init__(self, db):
        super().__init__(db, "supplier")

    def get_all(self, search=""):
        query = "SELECT * FROM suppliers WHERE 1=1"
        params = []
        if search:
            query += " AND (name LIKE %s OR email LIKE %s OR phone LIKE %s OR city LIKE %s)"
            params.extend([f"%{search}%"] * 4)
        query += " ORDER BY name ASC"
        return self.db.execute_query(query, params, dictionary=True)

    def get_by_id(self, supplier_id):
        result = self.db.execute_query(
            "SELECT * FROM suppliers WHERE supplier_id = %s",
            (supplier_id,), dictionary=True,
        )
        if not result:
            raise NotFoundError("Supplier")
        return result[0]

    def create(self, name, contact_person="", email="", phone="", address="", city=""):
        if not name or not name.strip():
            raise ValidationError("Supplier name is required.", field="name")

        self.db.execute_update(
            """INSERT INTO suppliers (name, contact_person, email, phone, address, city)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (name.strip(), contact_person.strip(), email.strip(),
             phone.strip(), address.strip(), city.strip()),
        )
        result = self.db.execute_query(
            "SELECT supplier_id FROM suppliers WHERE name = %s ORDER BY supplier_id DESC LIMIT 1",
            (name.strip(),),
        )
        supplier_id = result[0]["supplier_id"] if isinstance(result[0], dict) else result[0][0]
        self._log("create", supplier_id, {"name": name})
        return supplier_id

    def update(self, supplier_id, name, contact_person="", email="", phone="",
               address="", city="", is_active=True):
        self.get_by_id(supplier_id)
        self.db.execute_update(
            """UPDATE suppliers SET name=%s, contact_person=%s, email=%s, phone=%s,
               address=%s, city=%s, is_active=%s WHERE supplier_id=%s""",
            (name.strip(), contact_person.strip(), email.strip(), phone.strip(),
             address.strip(), city.strip(), is_active, supplier_id),
        )
        self._log("update", supplier_id, {"name": name})

    def delete(self, supplier_id):
        supplier = self.get_by_id(supplier_id)
        self.db.execute_update(
            "DELETE FROM suppliers WHERE supplier_id = %s", (supplier_id,)
        )
        self._log("delete", supplier_id, {"name": supplier["name"]})

    def get_purchase_summary(self, supplier_id):
        return self.db.execute_query(
            """SELECT COUNT(*) as total_purchases,
                      COALESCE(SUM(p.total_amount), 0) as total_spent,
                      MAX(p.purchase_date) as last_purchase_date
               FROM purchases p WHERE p.supplier_id = %s""",
            (supplier_id,), dictionary=True,
        )[0]
