import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.execute_query.return_value = []
    db.execute_update.return_value = None
    db.get_connection.return_value = MagicMock()
    return db


@pytest.fixture
def mock_session_admin():
    with patch("inventory.session.session_manager") as mock:
        mock.is_authenticated = True
        user = MagicMock()
        user.user_id = 1
        user.role = "admin"
        mock.current_user = user
        yield mock


@pytest.fixture
def mock_session_staff():
    with patch("inventory.session.session_manager") as mock:
        mock.is_authenticated = True
        user = MagicMock()
        user.user_id = 2
        user.role = "staff"
        mock.current_user = user
        yield mock


@pytest.fixture
def basic_validator_test_cases():
    return {
        "username_cases": [
            ("john_doe", True),
            ("ab", False),
            ("a" * 51, False),
            ("john doe", False),
            ("", False),
        ],
        "email_cases": [
            ("test@example.com", True),
            ("invalid", False),
            ("@domain.com", False),
            ("user@.com", False),
            ("", False),
        ],
        "password_cases": [
            ("Abcdef1", False),
            ("abcdefgh1", False),
            ("ABCDEF1", False),
            ("Abcdef1!", True),
            ("Abcdefgh1", True),
            ("", False),
        ],
    }
