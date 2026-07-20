from nicegui import app, ui
from inventory.services.auth_service import AuthService
from inventory.database import DatabaseManager

_db_instance = None


def get_db():
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager()
    return _db_instance


class WebAuth:
    @staticmethod
    def login(username_or_email: str, password: str):
        db = get_db()
        auth = AuthService(db)
        user = auth.authenticate(username_or_email, password)
        app.storage.user.update({
            'authenticated': True,
            'user_id': user.user_id,
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role,
        })
        return user

    @staticmethod
    def logout():
        app.storage.user.clear()
        ui.navigate.to('/login')

    @staticmethod
    def current_user():
        if not app.storage.user.get('authenticated'):
            return None
        return app.storage.user

    @staticmethod
    def is_authenticated():
        return app.storage.user.get('authenticated', False)

    @staticmethod
    def has_permission(required_role: str):
        if not WebAuth.is_authenticated():
            return False
        role_hierarchy = {'admin': 3, 'manager': 2, 'staff': 1}
        user_level = role_hierarchy.get(app.storage.user.get('role', ''), 0)
        required_level = role_hierarchy.get(required_role, 0)
        return user_level >= required_level
