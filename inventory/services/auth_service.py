from inventory.exceptions import AuthenticationError, ValidationError, NotFoundError
from inventory.utils.validators import Validators
from inventory.utils.password_utils import hash_password, verify_password
from inventory.session import session_manager


class AuthService:
    def __init__(self, db):
        self.db = db

    def register(self, username, email, password, full_name=""):
        is_valid, result = Validators.username_format(username)
        if not is_valid:
            raise ValidationError(result, field="username")

        is_valid, result = Validators.email_format(email)
        if not is_valid:
            raise ValidationError(result, field="email")

        is_valid, result = Validators.password_strength(password)
        if not is_valid:
            raise ValidationError(result, field="password")

        existing = self.db.execute_query(
            "SELECT user_id FROM users WHERE username = %s OR email = %s",
            (username, email),
        )
        if existing:
            raise ValidationError("Username or email already exists.", field="username")

        password_hash = hash_password(password)

        user_id = None
        cursor = None
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO users (username, email, password_hash, full_name, role)
                   VALUES (%s, %s, %s, %s, 'staff')""",
                (username, email, password_hash, full_name),
            )
            conn.commit()
            user_id = cursor.lastrowid
        except Exception:
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

        self._log_activity(user_id, "register", "user", user_id, {"username": username})
        return user_id

    def authenticate(self, username_or_email, password):
        """Verify credentials and create a user session on success."""
        if not username_or_email or not password:
            raise AuthenticationError("Username and password are required.")

        user = self.db.execute_query(
            """SELECT user_id, username, email, password_hash, full_name, role, is_active
               FROM users WHERE username = %s OR email = %s""",
            (username_or_email, username_or_email),
            dictionary=True,
        )

        if not user:
            raise AuthenticationError("Invalid username or password.")

        user = user[0]

        if not user["is_active"]:
            raise AuthenticationError("This account has been deactivated. Contact an administrator.")

        if not verify_password(password, user["password_hash"]):
            raise AuthenticationError("Invalid username or password.")

        self.db.execute_update(
            "UPDATE users SET last_login = NOW() WHERE user_id = %s",
            (user["user_id"],),
        )

        session_manager.login(
            user_id=user["user_id"],
            username=user["username"],
            email=user["email"],
            full_name=user["full_name"],
            role=user["role"],
        )

        self._log_activity(user["user_id"], "login", "user", user["user_id"], {})
        return session_manager.current_user

    def change_password(self, user_id, old_password, new_password):
        user = self.db.execute_query(
            "SELECT password_hash FROM users WHERE user_id = %s",
            (user_id,),
            dictionary=True,
        )
        if not user:
            raise NotFoundError("User")

        if not verify_password(old_password, user[0]["password_hash"]):
            raise AuthenticationError("Current password is incorrect.")

        is_valid, result = Validators.password_strength(new_password)
        if not is_valid:
            raise ValidationError(result, field="new_password")

        new_hash = hash_password(new_password)
        self.db.execute_update(
            "UPDATE users SET password_hash = %s WHERE user_id = %s",
            (new_hash, user_id),
        )

        self._log_activity(user_id, "change_password", "user", user_id, {})

    def seed_admin(self, username="admin", password="admin123", email="admin@inventory.local"):
        existing = self.db.execute_query(
            "SELECT user_id FROM users WHERE username = %s", (username,)
        )
        if existing:
            return existing[0]["user_id"] if isinstance(existing[0], dict) else existing[0][0]

        password_hash = hash_password(password)
        self.db.execute_update(
            """INSERT INTO users (username, email, password_hash, full_name, role, is_active)
               VALUES (%s, %s, %s, %s, 'admin', TRUE)""",
            (username, email, password_hash, "System Administrator"),
        )

        result = self.db.execute_query(
            "SELECT user_id FROM users WHERE username = %s", (username,)
        )
        return result[0]["user_id"] if isinstance(result[0], dict) else result[0][0]

    def _log_activity(self, user_id, action, entity_type, entity_id, details):
        try:
            self.db.execute_update(
                """INSERT INTO activity_log (user_id, action, entity_type, entity_id, details)
                   VALUES (%s, %s, %s, %s, %s)""",
                (user_id, action, entity_type, entity_id, str(details)),
            )
        except Exception:
            pass
