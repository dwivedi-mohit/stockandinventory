from passlib.hash import bcrypt
from inventory.exceptions import ValidationError, NotFoundError, AuthenticationError
from inventory.utils.validators import Validators
from inventory.config import PASSWORD_HASH_ROUNDS
from inventory.services.activity_service import ActivityService
from inventory.session import session_manager


class UserService:
    def __init__(self, db):
        self.db = db
        self._activity = ActivityService(db)

    def _log(self, action, entity_id=None, details=None):
        if session_manager.is_authenticated:
            self._activity.log(
                user_id=session_manager.current_user.user_id,
                action=action,
                entity_type="user",
                entity_id=entity_id,
                details=details,
            )

    def get_all(self):
        return self.db.execute_query(
            """SELECT user_id, username, email, full_name, role, is_active, last_login, created_at
               FROM users ORDER BY username ASC""",
            dictionary=True,
        )

    def get_by_id(self, user_id):
        result = self.db.execute_query(
            "SELECT user_id, username, email, full_name, role, is_active, last_login, created_at "
            "FROM users WHERE user_id = %s",
            (user_id,), dictionary=True,
        )
        if not result:
            raise NotFoundError("User")
        return result[0]

    def create(self, username, email, password, full_name="", role="staff"):
        existing = self.db.execute_query(
            "SELECT user_id FROM users WHERE username = %s OR email = %s",
            (username, email),
        )
        if existing:
            raise ValidationError("Username or email already exists.")

        is_valid, msg = Validators.password_strength(password)
        if not is_valid:
            raise ValidationError(msg)

        password_hash = bcrypt.using(rounds=PASSWORD_HASH_ROUNDS).hash(password)
        self.db.execute_update(
            """INSERT INTO users (username, email, password_hash, full_name, role, is_active)
               VALUES (%s, %s, %s, %s, %s, TRUE)""",
            (username, email, password_hash, full_name, role),
        )
        self._log("create_user", None, {"username": username, "role": role})

    def update(self, user_id, full_name="", role="staff", is_active=True):
        self.get_by_id(user_id)
        self.db.execute_update(
            "UPDATE users SET full_name=%s, role=%s, is_active=%s WHERE user_id=%s",
            (full_name, role, is_active, user_id),
        )
        self._log("update_user", user_id, {"role": role, "is_active": is_active})

    def delete(self, user_id):
        user = self.get_by_id(user_id)
        if user["username"] == "admin":
            raise ValidationError("Cannot delete the primary admin account.")
        self.db.execute_update("DELETE FROM users WHERE user_id = %s", (user_id,))
        self._log("delete_user", user_id, {"username": user["username"]})

    def reset_password(self, user_id, new_password):
        self.get_by_id(user_id)
        is_valid, msg = Validators.password_strength(new_password)
        if not is_valid:
            raise ValidationError(msg)

        password_hash = bcrypt.using(rounds=PASSWORD_HASH_ROUNDS).hash(new_password)
        self.db.execute_update(
            "UPDATE users SET password_hash = %s WHERE user_id = %s",
            (password_hash, user_id),
        )
        self._log("reset_password", user_id)

    def change_own_password(self, user_id, current_password, new_password):
        user = self.db.execute_query(
            "SELECT password_hash FROM users WHERE user_id = %s",
            (user_id,), dictionary=True,
        )
        if not user:
            raise NotFoundError("User")

        if not bcrypt.verify(current_password, user[0]["password_hash"]):
            raise AuthenticationError("Current password is incorrect.")

        is_valid, msg = Validators.password_strength(new_password)
        if not is_valid:
            raise ValidationError(msg)

        password_hash = bcrypt.using(rounds=PASSWORD_HASH_ROUNDS).hash(new_password)
        self.db.execute_update(
            "UPDATE users SET password_hash = %s WHERE user_id = %s",
            (password_hash, user_id),
        )
        self._log("change_password", user_id)
