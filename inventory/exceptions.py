class InventoryError(Exception):
    pass

class DatabaseConnectionError(InventoryError):
    def __init__(self, message="Could not connect to the database. Check your credentials and ensure MySQL is running."):
        super().__init__(message)

class AuthenticationError(InventoryError):
    def __init__(self, message="Invalid username or password."):
        super().__init__(message)

class ValidationError(InventoryError):
    def __init__(self, message, field=None):
        self.field = field
        super().__init__(message)

class NotFoundError(InventoryError):
    def __init__(self, entity="Resource"):
        super().__init__(f"{entity} not found.")

class InsufficientStockError(InventoryError):
    def __init__(self, product_name="", available=0, requested=0):
        msg = f"Insufficient stock for '{product_name}'. Available: {available}, Requested: {requested}"
        super().__init__(msg)

class PermissionDeniedError(InventoryError):
    def __init__(self, message="You do not have permission to perform this action."):
        super().__init__(message)
