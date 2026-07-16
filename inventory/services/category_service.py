from inventory.exceptions import ValidationError, NotFoundError
from inventory.services.activity_service import ActivityService
from inventory.session import session_manager


class CategoryService:
    def __init__(self, db):
        self.db = db
        self._activity = ActivityService(db)

    def _log(self, action, entity_id=None, details=None):
        if session_manager.is_authenticated:
            self._activity.log(
                user_id=session_manager.current_user.user_id,
                action=action,
                entity_type="category",
                entity_id=entity_id,
                details=details,
            )

    def get_all(self):
        return self.db.execute_query(
            """SELECT c.*, (SELECT COUNT(*) FROM products p WHERE p.category_id = c.category_id) as product_count
               FROM categories c ORDER BY c.name ASC""",
            dictionary=True,
        )

    def get_by_id(self, category_id):
        result = self.db.execute_query(
            "SELECT * FROM categories WHERE category_id = %s",
            (category_id,), dictionary=True,
        )
        if not result:
            raise NotFoundError("Category")
        return result[0]

    def create(self, name, description="", parent_id=None):
        if not name or not name.strip():
            raise ValidationError("Category name is required.", field="name")

        existing = self.db.execute_query(
            "SELECT category_id FROM categories WHERE name = %s", (name.strip(),)
        )
        if existing:
            raise ValidationError(f"Category '{name}' already exists.", field="name")

        self.db.execute_update(
            "INSERT INTO categories (name, description, parent_id) VALUES (%s, %s, %s)",
            (name.strip(), description.strip(), parent_id),
        )
        result = self.db.execute_query(
            "SELECT category_id FROM categories WHERE name = %s ORDER BY category_id DESC LIMIT 1",
            (name.strip(),),
        )
        category_id = result[0]["category_id"] if isinstance(result[0], dict) else result[0][0]
        self._log("create", category_id, {"name": name})
        return category_id

    def update(self, category_id, name, description="", parent_id=None):
        self.get_by_id(category_id)
        self.db.execute_update(
            "UPDATE categories SET name=%s, description=%s, parent_id=%s WHERE category_id=%s",
            (name.strip(), description.strip(), parent_id, category_id),
        )
        self._log("update", category_id, {"name": name})

    def delete(self, category_id):
        category = self.get_by_id(category_id)
        self.db.execute_query(
            "UPDATE products SET category_id = NULL WHERE category_id = %s",
            (category_id,),
        )
        self.db.execute_update(
            "DELETE FROM categories WHERE category_id = %s", (category_id,)
        )
        self._log("delete", category_id, {"name": category["name"]})
