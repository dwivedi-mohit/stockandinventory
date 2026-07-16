import pytest
from unittest.mock import MagicMock, patch

from inventory.services.auth_service import AuthService
from inventory.services.product_service import ProductService
from inventory.services.category_service import CategoryService
from inventory.services.supplier_service import SupplierService
from inventory.services.customer_service import CustomerService
from inventory.services.purchase_service import PurchaseService
from inventory.services.sale_service import SaleService
from inventory.services.user_service import UserService
from inventory.services.settings_service import SettingsService
from inventory.services.activity_service import ActivityService
from inventory.exceptions import (
    ValidationError, NotFoundError, AuthenticationError,
    InsufficientStockError,
)


class TestCategoryService:
    def test_create_valid(self, mock_db):
        mock_db.execute_query.side_effect = [[], [{"category_id": 1}]]
        svc = CategoryService(mock_db)
        cat_id = svc.create("Test Category")
        assert cat_id == 1
        mock_db.execute_update.assert_called_once()

    def test_create_duplicate(self, mock_db):
        mock_db.execute_query.return_value = [{"category_id": 1}]
        svc = CategoryService(mock_db)
        with pytest.raises(ValidationError):
            svc.create("Test Category")

    def test_create_empty_name(self, mock_db):
        svc = CategoryService(mock_db)
        with pytest.raises(ValidationError):
            svc.create("")

    def test_get_all(self, mock_db):
        mock_db.execute_query.return_value = [{"category_id": 1, "name": "Cat1"}]
        svc = CategoryService(mock_db)
        result = svc.get_all()
        assert len(result) == 1
        assert result[0]["name"] == "Cat1"

    def test_get_by_id_found(self, mock_db):
        mock_db.execute_query.return_value = [{"category_id": 1, "name": "Cat1"}]
        svc = CategoryService(mock_db)
        result = svc.get_by_id(1)
        assert result["category_id"] == 1

    def test_get_by_id_not_found(self, mock_db):
        mock_db.execute_query.return_value = []
        svc = CategoryService(mock_db)
        with pytest.raises(NotFoundError):
            svc.get_by_id(999)

    def test_delete(self, mock_db):
        mock_db.execute_query.return_value = [{"category_id": 1, "name": "Cat1"}]
        svc = CategoryService(mock_db)
        svc.delete(1)
        assert mock_db.execute_update.call_count == 1

    def test_update(self, mock_db):
        mock_db.execute_query.return_value = [{"category_id": 1, "name": "Cat1"}]
        svc = CategoryService(mock_db)
        svc.update(1, "Updated Name")
        mock_db.execute_update.assert_called_once()


class TestProductService:
    def test_create_valid(self, mock_db):
        mock_db.execute_query.side_effect = [[], [], [{"product_id": 1}]]
        svc = ProductService(mock_db)
        pid = svc.create("Test Product", "SKU-001", 10.99)
        assert pid == 1

    def test_create_duplicate_sku(self, mock_db):
        mock_db.execute_query.return_value = [{"product_id": 1}]
        svc = ProductService(mock_db)
        with pytest.raises(ValidationError, match="SKU"):
            svc.create("Test", "SKU-001", 10.99)

    def test_get_by_id_found(self, mock_db):
        mock_db.execute_query.return_value = [{"product_id": 1, "name": "Test"}]
        svc = ProductService(mock_db)
        result = svc.get_by_id(1)
        assert result["name"] == "Test"

    def test_get_by_id_not_found(self, mock_db):
        mock_db.execute_query.return_value = []
        svc = ProductService(mock_db)
        with pytest.raises(NotFoundError):
            svc.get_by_id(999)

    def test_update_stock_increase(self, mock_db):
        mock_db.execute_query.return_value = [{"product_id": 1, "name": "Test"}]
        svc = ProductService(mock_db)
        svc.update_stock(1, 5)
        mock_db.execute_update.assert_called_once()

    def test_update_stock_decrease(self, mock_db):
        mock_db.execute_query.return_value = [{"product_id": 1, "name": "Test"}]
        svc = ProductService(mock_db)
        svc.update_stock(1, -3)
        mock_db.execute_update.assert_called_once()

    def test_get_low_stock(self, mock_db):
        mock_db.execute_query.return_value = [{"product_id": 1, "name": "Low"}]
        svc = ProductService(mock_db)
        result = svc.get_low_stock()
        assert len(result) == 1

    def test_dashboard_stats(self, mock_db):
        mock_db.execute_query.side_effect = [
            [{"count": 10, "total_stock": 100, "total_value": 5000.0}],
            [{"count": 2}],
            [{"count": 5}],
        ]
        svc = ProductService(mock_db)
        stats = svc.get_dashboard_stats()
        assert stats["count"] == 10
        assert stats["total_stock"] == 100
        assert stats["low_stock_count"] == 2
        assert stats["category_count"] == 5

    def test_generate_sku_no_category(self, mock_db):
        mock_db.execute_query.side_effect = [[{"c": 5}]]
        svc = ProductService(mock_db)
        sku = svc.generate_sku()
        assert sku.startswith("PRD-")
        assert sku == "PRD-0006"


class TestSupplierService:
    def test_create_valid(self, mock_db):
        mock_db.execute_query.return_value = [{"supplier_id": 1}]
        svc = SupplierService(mock_db)
        sid = svc.create("Test Supplier")
        assert sid == 1

    def test_create_empty_name(self, mock_db):
        svc = SupplierService(mock_db)
        with pytest.raises(ValidationError):
            svc.create("")

    def test_get_by_id_not_found(self, mock_db):
        mock_db.execute_query.return_value = []
        svc = SupplierService(mock_db)
        with pytest.raises(NotFoundError):
            svc.get_by_id(999)

    def test_update(self, mock_db):
        mock_db.execute_query.return_value = [{"supplier_id": 1, "name": "Old"}]
        svc = SupplierService(mock_db)
        svc.update(1, "New Name")
        mock_db.execute_update.assert_called_once()

    def test_delete(self, mock_db):
        mock_db.execute_query.return_value = [{"supplier_id": 1, "name": "Test"}]
        svc = SupplierService(mock_db)
        svc.delete(1)
        mock_db.execute_update.assert_called_once()


class TestCustomerService:
    def test_create_valid(self, mock_db):
        mock_db.execute_query.return_value = [{"customer_id": 1}]
        svc = CustomerService(mock_db)
        cid = svc.create("John Doe")
        assert cid == 1

    def test_create_empty_name(self, mock_db):
        svc = CustomerService(mock_db)
        with pytest.raises(ValidationError):
            svc.create("")

    def test_add_loyalty_points(self, mock_db):
        svc = CustomerService(mock_db)
        svc.add_loyalty_points(1, 50)
        mock_db.execute_update.assert_called_once()


class TestAuthService:
    def test_authenticate_valid(self, mock_db):
        from passlib.hash import bcrypt
        from inventory.config import PASSWORD_HASH_ROUNDS
        pwd_hash = bcrypt.using(rounds=PASSWORD_HASH_ROUNDS).hash("ValidP@ss1")
        mock_db.execute_query.return_value = [{
            "user_id": 1, "username": "admin", "email": "a@b.com",
            "password_hash": pwd_hash, "full_name": "Admin", "role": "admin",
            "is_active": True,
        }]
        svc = AuthService(mock_db)
        user = svc.authenticate("admin", "ValidP@ss1")
        assert user.user_id == 1
        assert user.role == "admin"

    def test_authenticate_invalid_password(self, mock_db):
        from passlib.hash import bcrypt
        from inventory.config import PASSWORD_HASH_ROUNDS
        pwd_hash = bcrypt.using(rounds=PASSWORD_HASH_ROUNDS).hash("ValidP@ss1")
        mock_db.execute_query.return_value = [{
            "user_id": 1, "username": "admin", "email": "a@b.com",
            "password_hash": pwd_hash, "full_name": "Admin", "role": "admin",
            "is_active": True,
        }]
        svc = AuthService(mock_db)
        with pytest.raises(AuthenticationError):
            svc.authenticate("admin", "WrongPass1")

    def test_authenticate_deactivated(self, mock_db):
        mock_db.execute_query.return_value = [{
            "user_id": 1, "username": "admin", "email": "a@b.com",
            "password_hash": "hash", "full_name": "Admin", "role": "admin",
            "is_active": False,
        }]
        svc = AuthService(mock_db)
        with pytest.raises(AuthenticationError, match="deactivated"):
            svc.authenticate("admin", "pass")

    def test_authenticate_empty_credentials(self, mock_db):
        svc = AuthService(mock_db)
        with pytest.raises(AuthenticationError):
            svc.authenticate("", "")

    def test_register_valid(self, mock_db):
        mock_db.execute_query.side_effect = [[], []]
        mock_db.get_connection.return_value.cursor.return_value.lastrowid = 1
        svc = AuthService(mock_db)
        uid = svc.register("newuser", "new@test.com", "StrongP@ss1", "New User")
        assert uid == 1

    def test_register_duplicate(self, mock_db):
        mock_db.execute_query.return_value = [{"user_id": 1}]
        svc = AuthService(mock_db)
        with pytest.raises(ValidationError):
            svc.register("existing", "e@t.com", "StrongP@ss1")

    def test_seed_admin_exists(self, mock_db):
        mock_db.execute_query.return_value = [{"user_id": 1}]
        svc = AuthService(mock_db)
        uid = svc.seed_admin()
        assert uid == 1
        mock_db.execute_update.assert_not_called()

    def test_seed_admin_new(self, mock_db):
        mock_db.execute_query.side_effect = [[], [{"user_id": 1}]]
        svc = AuthService(mock_db)
        uid = svc.seed_admin()
        assert uid == 1
        mock_db.execute_update.assert_called_once()


class TestUserService:
    def test_create_valid(self, mock_db):
        mock_db.execute_query.return_value = []
        svc = UserService(mock_db)
        svc.create("newuser", "new@test.com", "StrongP@ss1")
        assert mock_db.execute_update.call_count >= 1

    def test_create_duplicate(self, mock_db):
        mock_db.execute_query.return_value = [{"user_id": 1}]
        svc = UserService(mock_db)
        with pytest.raises(ValidationError):
            svc.create("existing", "e@t.com", "StrongP@ss1")

    def test_create_weak_password(self, mock_db):
        mock_db.execute_query.return_value = []
        svc = UserService(mock_db)
        with pytest.raises(ValidationError):
            svc.create("newuser", "new@test.com", "weak")

    def test_get_all(self, mock_db):
        mock_db.execute_query.return_value = [{"user_id": 1, "username": "admin"}]
        svc = UserService(mock_db)
        users = svc.get_all()
        assert len(users) == 1

    def test_delete_admin(self, mock_db):
        mock_db.execute_query.return_value = [{"user_id": 1, "username": "admin"}]
        svc = UserService(mock_db)
        with pytest.raises(ValidationError, match="admin"):
            svc.delete(1)

    def test_reset_password(self, mock_db):
        mock_db.execute_query.return_value = [{"user_id": 2, "username": "staff1"}]
        svc = UserService(mock_db)
        svc.reset_password(2, "NewStr0ng!")
        assert mock_db.execute_update.call_count >= 1


class TestPurchaseService:
    def test_create_empty_items(self, mock_db):
        svc = PurchaseService(mock_db)
        with pytest.raises(ValidationError, match="item"):
            svc.create(1, 1, [])

    def test_create_valid(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.lastrowid = 1
        mock_conn.cursor.return_value = mock_cursor
        mock_db.get_connection.return_value = mock_conn

        svc = PurchaseService(mock_db)
        items = [{"product_id": 1, "quantity": 10, "unit_cost": 5.0}]
        pid = svc.create(1, 1, items)
        assert pid == 1
        assert mock_cursor.execute.call_count == 3
        mock_conn.commit.assert_called_once()

    def test_cancel_already_cancelled(self, mock_db):
        mock_db.execute_query.return_value = [{"status": "cancelled", "items": []}]
        svc = PurchaseService(mock_db)
        with pytest.raises(ValidationError, match="cancelled"):
            svc.cancel(1)

    def test_cancel_valid(self, mock_db):
        mock_db.execute_query.side_effect = [
            [{"purchase_id": 1, "status": "received", "supplier_id": 1, "total_amount": 100.0}],
            [{"product_id": 1, "quantity": 5, "unit_cost": 10.0}],
        ]
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db.get_connection.return_value = mock_conn

        svc = PurchaseService(mock_db)
        svc.cancel(1)
        mock_conn.commit.assert_called_once()


class TestSaleService:
    def test_create_empty_items(self, mock_db):
        svc = SaleService(mock_db)
        with pytest.raises(ValidationError, match="item"):
            svc.create(1, [])

    def test_create_valid(self, mock_db):
        mock_db.execute_query.return_value = [{
            "product_id": 1, "name": "Test", "stock_quantity": 100,
            "selling_price": 10.0,
        }]
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.lastrowid = 1
        mock_conn.cursor.return_value = mock_cursor
        mock_db.get_connection.return_value = mock_conn

        svc = SaleService(mock_db)
        items = [{"product_id": 1, "quantity": 2, "unit_price": 10.0, "discount": 0}]
        sid = svc.create(1, items)
        assert sid == 1
        mock_conn.commit.assert_called_once()

    def test_create_insufficient_stock(self, mock_db):
        mock_db.execute_query.return_value = [{
            "product_id": 1, "name": "Test", "stock_quantity": 1,
            "selling_price": 10.0,
        }]
        svc = SaleService(mock_db)
        items = [{"product_id": 1, "quantity": 10, "unit_price": 10.0, "discount": 0}]
        with pytest.raises(InsufficientStockError):
            svc.create(1, items)

    def test_process_return_valid(self, mock_db):
        mock_db.execute_query.side_effect = [
            [{"sale_id": 1}],
            [{"product_id": 1, "quantity": 5, "unit_price": 10.0, "discount": 0}],
        ]
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.lastrowid = 1
        mock_conn.cursor.return_value = mock_cursor
        mock_db.get_connection.return_value = mock_conn

        svc = SaleService(mock_db)
        rid = svc.process_return(1, 1, 2, "Defective")
        assert rid == 1

    def test_process_return_exceeds_quantity(self, mock_db):
        mock_db.execute_query.side_effect = [
            [{"sale_id": 1}],
            [{"product_id": 1, "quantity": 2, "unit_price": 10.0, "discount": 0}],
        ]
        svc = SaleService(mock_db)
        with pytest.raises(ValidationError):
            svc.process_return(1, 1, 10)


class TestActivityService:
    def test_log(self, mock_db):
        svc = ActivityService(mock_db)
        svc.log(1, "test_action", "product", 1, {"key": "val"})
        mock_db.execute_update.assert_called_once()

    def test_get_all(self, mock_db):
        mock_db.execute_query.return_value = [{"activity_id": 1, "action": "test"}]
        svc = ActivityService(mock_db)
        results = svc.get_all()
        assert len(results) == 1

    def test_get_recent(self, mock_db):
        mock_db.execute_query.return_value = [{"activity_id": 1}]
        svc = ActivityService(mock_db)
        results = svc.get_recent(5)
        assert len(results) == 1


class TestSettingsService:
    def test_get_company_settings_new(self, mock_db):
        mock_db.execute_query.side_effect = [[], [{"setting_id": 1, "company_name": "My Co"}]]
        mock_db.execute_update.return_value = None
        svc = SettingsService(mock_db)
        result = svc.get_company_settings()
        assert result["company_name"] == "My Co"

    def test_update_company_settings(self, mock_db):
        svc = SettingsService(mock_db)
        svc.update_company_settings("My Co", "123 Street", "555-0100")
        assert mock_db.execute_update.call_count >= 1

    def test_backup_database_mysqldump_not_found(self, mock_db):
        mock_db._config = {
            "host": "localhost", "port": 3306,
            "user": "root", "password": "", "database": "test",
        }
        svc = SettingsService(mock_db)
        with pytest.raises(RuntimeError, match="mysqldump"):
            svc.backup_database("/tmp/test.sql")

    def test_restore_database_file_not_found(self, mock_db):
        svc = SettingsService(mock_db)
        with pytest.raises(ValidationError, match="not found"):
            svc.restore_database("/nonexistent/file.sql")
