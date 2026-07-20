from inventory.services.activity_service import ActivityService
from inventory.session import session_manager


class BaseService:
    def __init__(self, db, entity_type=""):
        self.db = db
        self._entity_type = entity_type
        self._activity = ActivityService(db)

    def _log(self, action, entity_id=None, details=None):
        if not session_manager.is_authenticated:
            return
        self._activity.log(
            user_id=session_manager.current_user.user_id,
            action=action,
            entity_type=self._entity_type,
            entity_id=entity_id,
            details=details,
        )
