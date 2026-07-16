from datetime import date, timedelta


class ActivityService:
    def __init__(self, db):
        self.db = db

    def get_all(self, limit=200, user_id=None, action=None, days=None):
        query = """SELECT a.*, u.username, u.full_name
                   FROM activity_log a
                   JOIN users u ON a.user_id = u.user_id
                   WHERE 1=1"""
        params = []

        if user_id:
            query += " AND a.user_id = %s"
            params.append(user_id)

        if action:
            query += " AND a.action = %s"
            params.append(action)

        if days:
            from datetime import datetime, timedelta
            cutoff = datetime.now() - timedelta(days=days)
            query += " AND a.created_at >= %s"
            params.append(cutoff)

        query += " ORDER BY a.created_at DESC LIMIT %s"
        params.append(limit)

        return self.db.execute_query(query, params, dictionary=True)

    def log(self, user_id, action, entity_type, entity_id=None, details=None, ip_address=None):
        try:
            self.db.execute_update(
                """INSERT INTO activity_log (user_id, action, entity_type, entity_id, details, ip_address)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (user_id, action, entity_type, entity_id, str(details or {}), ip_address),
            )
        except Exception:
            pass

    def get_action_types(self):
        result = self.db.execute_query(
            "SELECT DISTINCT action FROM activity_log ORDER BY action ASC"
        )
        return [r["action"] if isinstance(r, dict) else r[0] for r in result]

    def get_recent(self, limit=10):
        return self.get_all(limit=limit)
