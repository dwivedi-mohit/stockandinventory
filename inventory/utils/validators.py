import re
from datetime import datetime


class Validators:
    @staticmethod
    def non_empty_string(value, field_name="Value"):
        if not value or not str(value).strip():
            return False, f"{field_name} cannot be empty."
        return True, str(value).strip()

    @staticmethod
    def positive_integer(value, field_name="Value"):
        try:
            num = int(value)
            if num < 0:
                return False, f"{field_name} must be a positive number."
            return True, num
        except (ValueError, TypeError):
            return False, f"{field_name} must be a valid integer."

    @staticmethod
    def positive_float(value, field_name="Value"):
        try:
            num = float(value)
            if num < 0:
                return False, f"{field_name} must be a positive number."
            return True, round(num, 2)
        except (ValueError, TypeError):
            return False, f"{field_name} must be a valid number."

    @staticmethod
    def email_format(value):
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, str(value)):
            return False, "Invalid email format."
        return True, str(value).strip()

    @staticmethod
    def phone_format(value):
        cleaned = re.sub(r"[\s\-\(\)\+]", "", str(value))
        if not cleaned.isdigit() or len(cleaned) < 7 or len(cleaned) > 15:
            return False, "Invalid phone number."
        return True, str(value).strip()

    @staticmethod
    def date_format(value):
        try:
            date = datetime.strptime(str(value), "%Y-%m-%d")
            return True, date.date()
        except (ValueError, TypeError):
            return False, "Invalid date format. Use YYYY-MM-DD."

    @staticmethod
    def password_strength(value):
        pwd = str(value)
        if len(pwd) < 8:
            return False, "Password must be at least 8 characters."
        if not re.search(r"[A-Z]", pwd):
            return False, "Password must contain at least one uppercase letter."
        if not re.search(r"[a-z]", pwd):
            return False, "Password must contain at least one lowercase letter."
        if not re.search(r"\d", pwd):
            return False, "Password must contain at least one digit."
        return True, pwd

    @staticmethod
    def username_format(value):
        name = str(value).strip()
        if len(name) < 3 or len(name) > 50:
            return False, "Username must be between 3 and 50 characters."
        if not re.match(r"^[a-zA-Z0-9_]+$", name):
            return False, "Username can only contain letters, numbers, and underscores."
        return True, name
