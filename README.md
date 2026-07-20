  ___           _            _   _                 _   _       __  __
 |_ _|_ __ ___ (_)_ __   ___| |_(_)_ __ ___   __ _| | | |_   _|  \/  | __ _ _ __
  | || '_ ` _ \| | '_ \ / __| __| | '_ ` _ \ / _` | | | \ \ / / |\/| |/ _` | '__|
  | || | | | | | | | | | (__| |_| | | | | | | (_| | | | |\ V /| |  | | (_| | |
 |___|_| |_| |_|_|_| |_|\___|\__|_|_| |_| |_|\__,_|_| |_| \_/ |_|  |_|\__,_|_|

                    _   _                 ____
                   | \ | | ___  ___ _ __ / ___|___  _ __ ___
                   |  \| |/ _ \/ _ \ '_ \\___ \ _ \| '_ ` _ \
                   | |\  |  __/  __/ |_) |___) | | | | | | | |
                   |_| \_|\___|\___| .__/|____/|_| |_| |_| |_|
                                   |_|

A Python desktop application for managing products, suppliers, purchases,
and sales with a modern PySide6 (Qt) GUI and MySQL database.

---

  ___      _   _
 / _ \ ___| |_| |_ ___ _ __
| | | / __| __| __/ _ \ '__|
| |_| \__ \ |_| |_  __/ |
 \___/|___/\__|\__\___|_|

[x] Add, view, and manage products with categories, SKUs, and barcodes
[x] Supplier management with contact info and purchase history
[x] Purchase order tracking with stock updates
[x] Sales invoicing with customer management and loyalty points
[x] Low stock alerts and automatic reorder suggestions
[x] Reports and analytics (inventory valuation, profit/loss, best sellers)
[x] MySQL database integration with connection retry logic
[x] Role-based access control (admin, manager, staff)
[x] CSV export for all reports
[x] Dark/light theme toggle

---

  ___                _   _
 / _ \ _ __  ___  __| | | |_ ___  __ _ _ __
| | | | '_ \/ __|/ _` | | __/ _ \/ _` | '_ \
| |_| | |_) \__ \ (_| | | |_|  __/ (_| | | | |
 \___/| .__/|___/\__,_|  \__\___|\__,_|_| |_|
      |_|

### Prerequisites

- Python 3.7+
- MySQL Server (running locally or remotely)
- pip package manager

### Setup

```bash
# Clone the repository
git clone https://github.com/dwivedi-mohit/stockandinventory.git
cd stockandinventory

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up the database
mysql -u root -p < database_setup.sql

# Configure environment
cp .env.example .env
# Edit .env with your MySQL credentials
```

---

  __ _ _ __  _   _  __ _  __ _
 / _` | '_ \| | | |/ _` |/ _` |
| (_| | | | | |_| | (_| | (_| |
 \__,_|_| |_|\__,_|\__, |\__,_|
                   |___/

```bash
source .venv/bin/activate
python main.py
```

  ___ _   _ _ __ ___  _ __ ___   __ _ _ __
 / _ \ | | | '_ ` _ \| '_ ` _ \ / _` | '__|
|  __/ |_| | | | | | | | | | | | (_| | |
 \___|\__,_|_| |_| |_|_| |_| |_|\__,_|_|

```
stockandinventory/
|-- main.py                     Application entry point
|-- database_setup.sql          Database schema and seed data
|-- requirements.txt            Python dependencies
|-- .env.example                Environment variable template
|-- inventory/
|   |-- config.py               Configuration (DB, app, env loader)
|   |-- database.py             Database manager (connection pool)
|   |-- exceptions.py           Custom exception classes
|   |-- session.py              User session management
|   |-- services/
|   |   |-- base_service.py     Base class with activity logging
|   |   |-- activity_service.py Audit trail
|   |   |-- auth_service.py     Authentication and registration
|   |   |-- category_service.py Product categories
|   |   |-- customer_service.py Customer management
|   |   |-- product_service.py  Product CRUD and stock
|   |   |-- purchase_service.py Purchase orders
|   |   |-- report_service.py   Reporting engine
|   |   |-- sale_service.py     Sales and returns
|   |   |-- settings_service.py Company settings and backup
|   |   |-- supplier_service.py Supplier management
|   |   |-- user_service.py     User management
|   |-- utils/
|       |-- password_utils.py   Password hashing (scrypt)
|       |-- validators.py       Input validation
|-- ui/
|   |-- app.py                  Main window, sidebar, navigation
|   |-- theme.py                Dark/light theme manager
|   |-- components/
|   |   |-- table_widget.py     Reusable data table component
|   |-- dialogs/
|   |   |-- form_dialog.py      Generic form dialog
|   |   |-- purchase_dialog.py  Purchase order form
|   |   |-- sale_dialog.py      Sales invoice form
|   |-- pages/
|       |-- login_page.py       Login screen
|       |-- dashboard_page.py   Dashboard with charts
|       |-- products_page.py    Product management
|       |-- suppliers_page.py   Supplier management
|       |-- customers_page.py   Customer management
|       |-- purchases_page.py   Purchase orders
|       |-- sales_page.py       Sales invoices
|       |-- reports_page.py     Reports and CSV export
|       |-- activity_log_page.py Audit log viewer
|       |-- settings_page.py    Settings (users, company, backup)
```

---

  ____   ___  _   _ _____ ____ ___  _   _ ____
 / ___| / _ \| | | | ____/ ___/ _ \| \ | / ___|
| |  _ | | | | | | |  _|| |  | | | |  \| \___ \
| |_| || |_| | |_| | |__| |__| |_| | |\  |___) |
 \____| \___/ \___/|_____\____\___/|_| \_|____/

Copy `.env.example` to `.env` and set:

```
DB_HOST=localhost          MySQL host
DB_PORT=3306               MySQL port
DB_USER=root               MySQL user
DB_PASSWORD=your_password  MySQL password
DB_NAME=inventory_db       Database name
APP_TITLE=Inventory Management System
APP_COMPANY=Your Company Name
```

---

  ____          _                  _____         _
 |  _ \        | |                |  ___|       | |
 | | | |  __ _ | |_  ___   _ __   | |__    __ _ | |_   ___
 | | | | / _` || __|/ _ \ | '_ \  |  __|  / _` || __| / _ \
 | |_| || (_| || |_| (_) || | | | | |___ | (_| || |_ |  __/
 |____/  \__,_| \__|\___/ |_| |_| \____/  \__,_| \__| \___|

### Database Connection Error
- Ensure MySQL Server is running
- Verify username and password in .env
- Check database name exists

### GUI Not Launching
- Ensure PySide6 is installed: `pip install PySide6`
- Check Python version (3.7+)

---

  __     ___          _
 \ \   / (_)         | |
  \ \ / / _ _ __ ___ | |__   ___ _ __ ___
   \ V / | | '_ ` _ \| '_ \ / _ \ '__/ __|
    \ /  | | | | | | | |_) |  __/ |  \__ \
    |_|  |_|_| |_| |_|_.__/ \___|_|  |___/

- **v1.0.0** - Initial release
  - Features: Product management, Sales tracking, Reports

---

  _     ____          _
 | |   / ___| ___  __| | ___ _ __
 | |   \___ \/ _ \/ _` |/ _ \ '__|
 | |_   ___) |  __/ (_| |  __/ |
 |_(_) |____/ \___|\__,_|\___|_|

This project is open source and available under the MIT License.

**Author:** Mohit Dwivedi
- GitHub: [@dwivedi-mohit](https://github.com/dwivedi-mohit)

For issues, questions, or contributions, please create an issue on GitHub.
