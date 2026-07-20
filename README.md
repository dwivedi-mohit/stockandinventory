╔═══════════════════════════════════════════════════════════════════════════════════╗
║                                                                                   ║
║                           .  WAREHOUSE  .                                         ║
║                       /_____________________\                                     ║
║                        |                   |                                      ║
║                        |  [P001]  [P002]   |                                      ║
║                        |  [P003]  [P004]   |                                      ║
║                        |___________________|                                      ║
║                        |  [P005]  [P006]   |                                      ║
║                        |  [P007]  [P008]   |                                      ║
║                        |  [P009]  [P010]   |                                      ║
║                        |___________________|                                      ║
║                                                                                   ║
║         O            |=======================|                                    ║
║        /|\           |  MANAGEMENT CONSOLE   |                                    ║
║        / \           |  v1.0  [ACTIVE]       |                                    ║
║                                                                                   ║
║                       INVENTORY MANAGEMENT SYSTEM                                 ║
║                                                                                   ║
║ ·~·~·~·~·~·~·~·~·~·~·~·~·~·~·~·~·~·~·~·~·~·~·~·~·~·~·~·~·~·~·~·~·~·~·~·~·~·~·~·~· ║
║ ·                                                                                 ║
║ ·   ___           _            _   _                 _   _       __  __           ║
║ ·  |_ _|_ __ ___ (_)_ __   ___| |_(_)_ __ ___   __ _| | | |_   _|  \/  | __ _ _ _ ║
║ ·   | || '_ ` _ \| | '_ \ / __| __| | '_ ` _ \ / _` | | | \ \ / / |\/| |/ _` | '_ ║
║                                                                                   ║
║ ·  |___|_| |_| |_|_|_| |_|\___|\__|_|_| |_| |_|\__,_|_| |_| \_/ |_|  |_|\__,_|_|  ║
║ ·                     _   _                 ____                                  ║
║ ·                    | \ | | ___  ___ _ __ / ___|___  _ __ ___                    ║
║ ·                    |  \| |/ _ \/ _ \ '_ \\___ \ _ \| '_ ` _ \                   ║
║ ·                    | |\  |  __/  __/ |_) |___) | | | | | | | |                  ║
║ ·                    |_| \_|\___|\___| .__/|____/|_| |_| |_| |_|                  ║
║                                                                                   ║
║ A Python desktop application for managing products, suppliers, purchases,         ║
║ and sales with a modern PySide6 (Qt) GUI and MySQL database.                      ║
║                                                                                   ║
╠═══════════════════════════════════════════════════════════════════════════════════╣
║                                                                                   ║
║   ┌───────────────────────────────────────────────────────────────────────────┐   ║
║   │                                  FEATURES                                 │   ║
║   ├───────────────────────────────────────────────────────────────────────────┤   ║
║   │   -  Add, view, manage products with categories, SKUs, barcodes           │   ║
║   │   -  Supplier management with contact info and purchase history           │   ║
║   │   -  Purchase order tracking with automatic stock updates                 │   ║
║   │   -  Sales invoicing with customer management and loyalty points          │   ║
║   │   -  Low stock alerts and automatic reorder suggestions                   │   ║
║   │   -  Reports: inventory valuation, profit/loss, best sellers              │   ║
║   │   -  MySQL database integration with connection retry logic               │   ║
║   │   -  Role-based access control (admin, manager, staff)                    │   ║
║   │   -  CSV export for all reports and data tables                           │   ║
║   │   -  Dark/light theme toggle with persistent preference                   │   ║
║   └───────────────────────────────────────────────────────────────────────────┘   ║
║                                                                                   ║
╠═══════════════════════════════════════════════════════════════════════════════════╣
║                                                                                   ║
║   ┌───────────────────────────────────────────────────────────────────────────┐   ║
║   │                                REQUIREMENTS                               │   ║
║   ├───────────────────────────────────────────────────────────────────────────┤   ║
║   │   -  Python 3.7+                                                          │   ║
║   │   -  MySQL Server (running locally or remotely)                           │   ║
║   │   -  pip package manager                                                  │   ║
║   └───────────────────────────────────────────────────────────────────────────┘   ║
║                                                                                   ║
╠═══════════════════════════════════════════════════════════════════════════════════╣
║                                                                                   ║
║   ┌───────────────────────────────────────────────────────────────────────────┐   ║
║   │                                   SETUP                                   │   ║
║   ├───────────────────────────────────────────────────────────────────────────┤   ║
║   │   $  git clone https://github.com/dwivedi-mohit/stockandinventory.git     │   ║
║   │   $  cd stockandinventory                                                 │   ║
║   │   $  python -m venv .venv                                                 │   ║
║   │   $  source .venv/bin/activate                                            │   ║
║   │   $  pip install -r requirements.txt                                      │   ║
║   │   $  mysql -u root -p < database_setup.sql                                │   ║
║   │   $  cp .env.example .env                                                 │   ║
║   │   $  # Edit .env with your MySQL credentials                              │   ║
║   └───────────────────────────────────────────────────────────────────────────┘   ║
║                                                                                   ║
╠═══════════════════════════════════════════════════════════════════════════════════╣
║                                                                                   ║
║   ┌───────────────────────────────────────────────────────────────────────────┐   ║
║   │                                    RUN                                    │   ║
║   ├───────────────────────────────────────────────────────────────────────────┤   ║
║   │   $  source .venv/bin/activate                                            │   ║
║   │   $  python main.py                                                       │   ║
║   └───────────────────────────────────────────────────────────────────────────┘   ║
║                                                                                   ║
╠═══════════════════════════════════════════════════════════════════════════════════╣
║                                                                                   ║
║   ┌───────────────────────────────────────────────────────────────────────────┐   ║
║   │                             PROJECT STRUCTURE                             │   ║
║   ├───────────────────────────────────────────────────────────────────────────┤   ║
║   │   stockandinventory/                                                      │   ║
║   │   ├── main.py                     Entry point                             │   ║
║   │   ├── database_setup.sql          Database schema                         │   ║
║   │   ├── requirements.txt            Python deps                             │   ║
║   │   ├── .env.example                Env template                            │   ║
║   │   ├── inventory/                                                          │   ║
║   │   │   ├── config.py                                                       │   ║
║   │   │   ├── database.py                                                     │   ║
║   │   │   ├── exceptions.py                                                   │   ║
║   │   │   ├── session.py                                                      │   ║
║   │   │   ├── services/                                                       │   ║
║   │   │   │   ├── base_service.py                                             │   ║
║   │   │   │   ├── auth_service.py                                             │   ║
║   │   │   │   ├── product_service.py                                          │   ║
║   │   │   │   ├── purchase_service.py                                         │   ║
║   │   │   │   ├── sale_service.py                                             │   ║
║   │   │   │   ├── report_service.py                                           │   ║
║   │   │   │   ├── supplier_service.py                                         │   ║
║   │   │   │   ├── customer_service.py                                         │   ║
║   │   │   │   ├── category_service.py                                         │   ║
║   │   │   │   ├── user_service.py                                             │   ║
║   │   │   │   ├── settings_service.py                                         │   ║
║   │   │   │   └── activity_service.py                                         │   ║
║   │   │   ├── utils/                                                          │   ║
║   │   │   │   ├── password_utils.py                                           │   ║
║   │   │   │   └── validators.py                                               │   ║
║   │   ├── ui/                                                                 │   ║
║   │   │   ├── app.py                                                          │   ║
║   │   │   ├── theme.py                                                        │   ║
║   │   │   ├── components/                                                     │   ║
║   │   │   │   └── table_widget.py                                             │   ║
║   │   │   ├── dialogs/                                                        │   ║
║   │   │   │   ├── form_dialog.py                                              │   ║
║   │   │   │   ├── purchase_dialog.py                                          │   ║
║   │   │   │   └── sale_dialog.py                                              │   ║
║   │   │   └── pages/                                                          │   ║
║   │   │       ├── login_page.py                                               │   ║
║   │   │       ├── dashboard_page.py                                           │   ║
║   │   │       ├── products_page.py                                            │   ║
║   │   │       ├── suppliers_page.py                                           │   ║
║   │   │       ├── customers_page.py                                           │   ║
║   │   │       ├── purchases_page.py                                           │   ║
║   │   │       ├── sales_page.py                                               │   ║
║   │   │       ├── reports_page.py                                             │   ║
║   │   │       ├── activity_log_page.py                                        │   ║
║   │   │       └── settings_page.py                                            │   ║
║   └───────────────────────────────────────────────────────────────────────────┘   ║
║                                                                                   ║
╠═══════════════════════════════════════════════════════════════════════════════════╣
║                                                                                   ║
║   ┌───────────────────────────────────────────────────────────────────────────┐   ║
║   │                               CONFIGURATION                               │   ║
║   ├───────────────────────────────────────────────────────────────────────────┤   ║
║   │   DB_HOST=localhost          MySQL host                                   │   ║
║   │   DB_PORT=3306               MySQL port                                   │   ║
║   │   DB_USER=root               MySQL user                                   │   ║
║   │   DB_PASSWORD=your_password  MySQL password                               │   ║
║   │   DB_NAME=inventory_db       Database name                                │   ║
║   │   APP_TITLE=Inventory Management System                                   │   ║
║   │   APP_COMPANY=Your Company Name                                           │   ║
║   └───────────────────────────────────────────────────────────────────────────┘   ║
║                                                                                   ║
╠═══════════════════════════════════════════════════════════════════════════════════╣
║                                                                                   ║
║   ┌───────────────────────────────────────────────────────────────────────────┐   ║
║   │                              TROUBLESHOOTING                              │   ║
║   ├───────────────────────────────────────────────────────────────────────────┤   ║
║   │   Database Connection Error:                                              │   ║
║   │     -  Ensure MySQL Server is running                                     │   ║
║   │     -  Verify username and password in .env                               │   ║
║   │     -  Check database name exists                                         │   ║
║   │                                                                           │   ║
║   │   GUI Not Launching:                                                      │   ║
║   │     -  pip install PySide6                                                │   ║
║   │     -  python --version (must be 3.7+)                                    │   ║
║   └───────────────────────────────────────────────────────────────────────────┘   ║
║                                                                                   ║
╠═══════════════════════════════════════════════════════════════════════════════════╣
║                                                                                   ║
║   ┌───────────────────────────────────────────────────────────────────────────┐   ║
║   │                                INFORMATION                                │   ║
║   ├───────────────────────────────────────────────────────────────────────────┤   ║
║   │   Version:  1.0.0                                                         │   ║
║   │   License:  MIT License                                                   │   ║
║   │   Author:   Mohit Dwivedi                                                 │   ║
║   │   GitHub:   @dwivedi-mohit                                                │   ║
║   │   Repo:     github.com/dwivedi-mohit/stockandinventory                    │   ║
║   └───────────────────────────────────────────────────────────────────────────┘   ║
║                                                                                   ║
╠═══════════════════════════════════════════════════════════════════════════════════╣
║                                                                                   ║
║                     ┌────────────────┐                                            ║
║                     │  IMS  v1.0.0  │   [MIT]                                     ║
║                     └────────────────┘                                            ║
║               <  Inventory Management System  >                                   ║
║                                                                                   ║
╚═══════════════════════════════════════════════════════════════════════════════════╝