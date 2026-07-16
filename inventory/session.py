from dataclasses import dataclass
from typing import Optional, Callable


@dataclass
class UserSession:
    user_id: int
    username: str
    email: str
    full_name: str
    role: str

    @property
    def is_admin(self):
        return self.role == "admin"

    @property
    def is_manager(self):
        return self.role in ("admin", "manager")

    def has_permission(self, required_role: str) -> bool:
        role_hierarchy = {"admin": 3, "manager": 2, "staff": 1}
        user_level = role_hierarchy.get(self.role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        return user_level >= required_level


class SessionManager:
    def __init__(self):
        self._user: Optional[UserSession] = None
        self._listeners: list[Callable] = []

    def on_change(self, callback: Callable):
        self._listeners.append(callback)

    def _notify(self):
        for cb in self._listeners:
            try:
                cb()
            except Exception:
                pass

    def login(self, user_id: int, username: str, email: str, full_name: str, role: str):
        self._user = UserSession(
            user_id=user_id,
            username=username,
            email=email,
            full_name=full_name,
            role=role,
        )
        self._notify()

    def logout(self):
        self._user = None
        self._notify()

    @property
    def is_authenticated(self) -> bool:
        return self._user is not None

    @property
    def current_user(self) -> Optional[UserSession]:
        return self._user

    def check_permission(self, required_role: str) -> bool:
        if not self._user:
            return False
        return self._user.has_permission(required_role)


session_manager = SessionManager()
