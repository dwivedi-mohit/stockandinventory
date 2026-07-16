import pytest
from inventory.utils.validators import Validators


class TestValidators:
    def test_username_format_valid(self):
        is_valid, val = Validators.username_format("john_doe")
        assert is_valid is True
        assert val == "john_doe"
        is_valid, val = Validators.username_format("user123")
        assert is_valid is True

    def test_username_format_too_short(self):
        result, msg = Validators.username_format("ab")
        assert result is False
        assert "3" in msg

    def test_username_format_too_long(self):
        result, msg = Validators.username_format("a" * 51)
        assert result is False
        assert "50" in msg

    def test_username_format_invalid_chars(self):
        result, msg = Validators.username_format("user name")
        assert result is False

    def test_email_format_valid(self):
        is_valid, val = Validators.email_format("test@example.com")
        assert is_valid is True
        assert val == "test@example.com"

    def test_email_format_invalid(self):
        assert Validators.email_format("notanemail")[0] is False
        assert Validators.email_format("@domain.com")[0] is False
        assert Validators.email_format("")[0] is False

    def test_password_strength_valid(self):
        is_valid, val = Validators.password_strength("Abcdef1!")
        assert is_valid is True
        assert val == "Abcdef1!"

    def test_password_strength_too_short(self):
        result, msg = Validators.password_strength("Ab1!")
        assert result is False

    def test_password_strength_no_uppercase(self):
        result, msg = Validators.password_strength("abcdefgh1")
        assert result is False

    def test_password_strength_no_digit(self):
        result, msg = Validators.password_strength("Abcdefgh!")
        assert result is False

    def test_min_password_length(self):
        result, msg = Validators.password_strength("a" * 7)
        assert result is False
        assert "8" in msg

    def test_whitespace_trimming(self):
        result, _ = Validators.username_format("  valid_user  ")
        assert result is True
