# Invictus - Inventory Management System
## Project Analysis & PowerPoint Content Guide

---

## 1. PROJECT OVERVIEW

**Name:** Invictus - Inventory Management System (IMS)
**Version:** 1.0.0
**Type:** Desktop Application
**Developed By:** BEE Tech

A full-featured desktop-based Stock & Inventory Management System built with Python, PySide6 (Qt6), and MySQL. It provides a complete GUI for managing products, suppliers, customers, purchases, sales, reports, and system settings with role-based access control.

---

## 2. TECH STACK

| Component       | Technology                  |
|-----------------|-----------------------------|
| Language        | Python 3                    |
| GUI Framework   | PySide6 (Qt6)               |
| Database        | MySQL 8                     |
| Auth/Security   | scrypt hashing, RBAC        |
| Configuration   | .env file                   |
| Password Hash   | scrypt (salt-based)         |
| Styling         | QSS (Qt Style Sheets)       |

---

## 3. SYSTEM ARCHITECTURE

### 3.1 Layered Architecture

```
┌─────────────────────────────────────────────┐
│            UI LAYER (PySide6)               │
│  Pages, Dialogs, Components, Theme Manager  │
├─────────────────────────────────────────────┤
│          SERVICE LAYER (Business Logic)     │
│  AuthService, ProductService, SaleService,  │
│  PurchaseService, ReportService, etc.       │
├─────────────────────────────────────────────┤
│           DATA LAYER (MySQL)                │
│  DatabaseManager, Transactions, Queries     │
└─────────────────────────────────────────────┘
```

### 3.2 Project Structure

```
stockandinventory/
├── main.py                     # Entry point, DB init, admin seed
├── database_setup.sql          # Full DB schema + seed data
├── requirements.txt            # PySide6, mysql-connector-python
├── .env.example                # Environment config template
├── assets/                     # Images/logos
├── inventory/                  # Business Logic Layer
│   ├── config.py               # DB & app config from .env
│   ├── database.py             # MySQL connection manager
│   ├── session.py              # User session + RBAC
│   ├── exceptions.py           # Custom exception classes
│   ├── utils/
│   │   ├── password_utils.py   # scrypt hash/verify
│   │   └── validators.py       # Input validation rules
│   └── services/
│       ├── base_service.py     # Base service with logging
│       ├── auth_service.py     # Login, register, seed admin
│       ├── product_service.py  # CRUD, stock, SKU generation
│       ├── supplier_service.py # Supplier CRUD
│       ├── customer_service.py # Customer CRUD, loyalty points
│       ├── purchase_service.py # Purchase orders, stock update
│       ├── sale_service.py     # Sales, returns, stock deduction
│       ├── report_service.py   # P&L, sales, inventory valuation
│       ├── activity_service.py # Audit log
│       └── settings_service.py # Company settings, DB backup
└── ui/                         # Presentation Layer
    ├── app.py                  # MainWindow, sidebar, navigation
    ├── theme.py                # Light/Dark theme (QSS)
    ├── components/
    │   └── table_widget.py     # Reusable table component
    ├── pages/
    │   ├── login_page.py       # Login screen
    │   ├── dashboard_page.py   # Dashboard with KPIs
    │   ├── products_page.py    # Product management
    │   ├── suppliers_page.py   # Supplier management
    │   ├── customers_page.py   # Customer management
    │   ├── purchases_page.py   # Purchase orders
    │   ├── sales_page.py       # Sales processing
    │   ├── reports_page.py     # Reporting dashboard
    │   ├── activity_log_page.py# Audit log viewer
    │   └── settings_page.py    # System settings
    └── dialogs/
        ├── form_dialog.py      # Generic form dialog
        ├── purchase_dialog.py  # Purchase creation dialog
        └── sale_dialog.py      # Sale creation dialog
```

---

## 4. DATABASE DESIGN

### 4.1 Tables (13 total)

| Table              | Purpose                                   |
|--------------------|-------------------------------------------|
| users              | User accounts & role management           |
| categories         | Product categories (hierarchical)         |
| products           | Product catalog with stock tracking       |
| suppliers          | Supplier information                      |
| customers          | Customer info & loyalty points            |
| purchases          | Purchase orders from suppliers            |
| purchase_items     | Line items for each purchase order        |
| sales              | Sales transactions                        |
| sale_items         | Line items for each sale                  |
| returns            | Product returns tracking                  |
| activity_log       | Audit trail for all system actions        |
| company_settings   | Company configuration (name, tax, etc.)   |
| backup_log         | Database backup history                   |

### 4.2 Entity Relationships

```
users ──────────< purchases
users ──────────< sales
users ──────────< activity_log
users ──────────< backup_log

suppliers ──────< purchases
customers ──────< sales

categories ─────< products

purchases ──────< purchase_items >──── products

sales ──────────< sale_items >──── products

sales ──────────< returns >──── products
```

### 4.3 Key Indexes

- products: category_id, sku, stock_quantity, is_active
- purchases: supplier_id, purchase_date, status
- sales: sale_date, customer_id, payment_method
- activity_log: user_id, (entity_type, entity_id), created_at
- returns: sale_id, return_date

---

## 5. KEY FEATURES

### 5.1 Authentication & Authorization
- Login with username or email
- scrypt password hashing (salt-based, N=16384)
- 3-tier role hierarchy: Admin > Manager > Staff
- Session management with change listener pattern
- Automatic admin seeding (admin/admin123)

### 5.2 Dashboard
- Total Products count & stock value
- Total Sales revenue
- Total Purchase cost
- Low Stock alert count
- 7-day sales trend chart
- Quick navigation sidebar

### 5.3 Product Management
- Full CRUD operations
- Auto SKU generation (category-based prefix)
- Barcode support
- Category assignment
- Cost price & selling price tracking
- Stock quantity & minimum stock level
- Active/inactive status
- Search by name, SKU, or barcode

### 5.4 Supplier Management
- Full CRUD operations
- Contact person, email, phone, address, city
- Purchase summary per supplier
- Search across all fields

### 5.5 Customer Management
- Full CRUD operations
- Loyalty points system (auto-earned on sales)
- Purchase history & summary
- Search by name, email, phone

### 5.6 Purchase Orders
- Create purchase orders with multiple items
- Select supplier and add products
- Set quantities and unit costs
- Auto stock increment on receive
- Cancel purchases (reverse stock)
- Status tracking: pending → received → cancelled

### 5.7 Sales Processing
- Cart-based sales with multiple items
- Stock validation (prevents overselling)
- Discount & tax calculation
- Multiple payment methods (cash, card, transfer)
- Auto stock deduction
- Auto loyalty points for customers
- Return processing with stock restoration

### 5.8 Reporting Engine
- **Inventory Valuation:** Cost & sale value by product
- **Sales Report:** Daily/monthly/yearly grouped
- **Profit & Loss:** Per-product and summary
- **Best-Selling Products:** Top 10 by quantity
- **Supplier Performance:** Orders, spend, avg value
- **Category Summary:** Stock & sales by category

### 5.9 Activity Logging
- Tracks all CRUD operations
- Records user, action, entity, timestamp
- Filterable by user, action type, date range
- JSON details for each action

### 5.10 Settings & Administration
- Company profile (name, address, tax ID, logo)
- Tax rate configuration
- Currency symbol
- Database backup (mysqldump)
- Database restore (mysql client)
- Backup history log

### 5.11 UI/UX Features
- Light & Dark theme toggle (Ctrl+T)
- Animated collapsible sidebar (Ctrl+B)
- Responsive table widgets with sorting
- Form validation with error messages
- Status bar with DB connection indicator
- Menu bar with keyboard shortcuts
- Confirmation dialogs for destructive actions

---

## 6. SECURITY FEATURES

- scrypt password hashing with random salt
- Role-based access control (Admin/Manager/Staff)
- Input validation on all forms (email, phone, password strength)
- SQL injection prevention (parameterized queries)
- Transaction rollback on errors
- Activity audit logging
- Session-based authentication

---

## 7. POWERPOINT SLIDE CONTENT

### SLIDE 1 — Title Slide

**Title:** Invictus - Inventory Management System
**Subtitle:** A Python/PySide6/MySQL Desktop Application
**Details:**
- Version 1.0.0
- Developed by BEE Tech
- Built with Python, Qt6, MySQL

---

### SLIDE 2 — Problem Statement

**Title:** The Problem

- Manual stock tracking is error-prone and time-consuming
- No real-time visibility into inventory levels
- Difficulty tracking purchases, sales, and profits
- Lack of role-based access control for teams
- No audit trails for accountability
- Paper-based reporting is slow and inaccurate

**Visual:** Show a frustrated person with paperwork/piles of paper

---

### SLIDE 3 — Our Solution

**Title:** Our Solution

- Complete desktop GUI for inventory lifecycle management
- Real-time stock tracking with automated low-stock alerts
- Integrated purchase and sales workflow
- Role-based access control (Admin, Manager, Staff)
- Automated reporting (P&L, inventory valuation, best sellers)
- Activity audit logging for full accountability

**Visual:** Show a clean dashboard screenshot

---

### SLIDE 4 — Tech Stack

**Title:** Technology Stack

| Layer        | Technology              |
|--------------|-------------------------|
| Frontend     | PySide6 (Qt6)           |
| Backend      | Python 3                |
| Database     | MySQL 8                 |
| Security     | scrypt, RBAC            |
| Styling      | QSS (Qt Style Sheets)   |
| Config       | .env                    |

**Visual:** Show logos of Python, Qt, MySQL

---

### SLIDE 5 — Architecture

**Title:** System Architecture

```
┌─────────────────────────────────────┐
│       UI LAYER (PySide6)            │
│  9 Pages, 3 Dialogs, Themes         │
├─────────────────────────────────────┤
│     SERVICE LAYER (Business)        │
│  9 Services with validation         │
├─────────────────────────────────────┤
│      DATA LAYER (MySQL)             │
│  13 Tables, Transactions            │
└─────────────────────────────────────┘
```

**Visual:** Use a layered diagram with arrows

---

### SLIDE 6 — Database Design

**Title:** Database Design

- 13 MySQL tables with proper relationships
- Foreign key constraints for data integrity
- Indexed columns for performance
- JSON support for activity log details
- Seed data for quick demo

**Key Tables:**
- users, products, categories, suppliers, customers
- purchases, purchase_items, sales, sale_items
- returns, activity_log, company_settings, backup_log

**Visual:** Show ER diagram

---

### SLIDE 7 — Dashboard

**Title:** Dashboard

**Features:**
- 4 KPI cards: Total Products, Sales Revenue, Purchase Cost, Low Stock
- 7-day sales trend chart
- Quick navigation sidebar
- Database connection status indicator
- Welcome message with user role

**Visual:** Screenshot of dashboard page

---

### SLIDE 8 — Product Management

**Title:** Product Management

**Features:**
- Full CRUD operations
- Auto SKU generation (e.g., ELE-0001 for Electronics)
- Barcode support for scanning
- Category-based organization
- Stock level tracking with min-stock alerts
- Search by name, SKU, or barcode
- Active/inactive product status

**Visual:** Screenshot of products page with table

---

### SLIDE 9 — Sales & Purchases

**Title:** Sales & Purchase Workflow

**Sales Process:**
1. Select customer (optional)
2. Add products with quantities
3. Apply discount & tax
4. Choose payment method (cash/card/transfer)
5. Process sale → Auto stock deduction → Loyalty points

**Purchase Process:**
1. Select supplier
2. Add products with quantities & costs
3. Receive purchase → Auto stock increment
4. Option to cancel (reverse stock)

**Visual:** Flow diagram showing both workflows

---

### SLIDE 10 — Reporting

**Title:** Reporting Engine

**Available Reports:**
- Inventory Valuation (cost & sale value)
- Sales Report (daily/monthly/yearly)
- Profit & Loss (per product & summary)
- Best-Selling Products (top 10)
- Supplier Performance (orders, spend, avg)
- Category Summary (stock & sales)

**Visual:** Screenshot of reports page or chart icons

---

### SLIDE 11 — Security

**Title:** Security & Access Control

- **3-tier RBAC:** Admin > Manager > Staff
- **Password Hashing:** scrypt with random salt
- **Input Validation:** Email, phone, password strength
- **SQL Injection Prevention:** Parameterized queries
- **Transaction Safety:** Rollback on errors
- **Audit Logging:** All actions tracked with timestamp

**Role Permissions:**
| Feature         | Admin | Manager | Staff |
|-----------------|-------|---------|-------|
| Dashboard       | ✓     | ✓       | ✓     |
| Products        | ✓     | ✓       | ✓     |
| Sales           | ✓     | ✓       | ✓     |
| Purchases       | ✓     | ✓       | ✓     |
| Reports         | ✓     | ✓       | ✗     |
| Activity Log    | ✓     | ✗       | ✗     |
| Settings        | ✓     | ✗       | ✗     |

---

### SLIDE 12 — UI/UX Features

**Title:** User Experience

- Light & Dark theme toggle (Ctrl+T)
- Animated collapsible sidebar (Ctrl+B)
- Responsive table widgets with sorting
- Form validation with clear error messages
- Status bar with database connection status
- Menu bar with keyboard shortcuts
- Confirmation dialogs for destructive actions

**Visual:** Show light and dark theme screenshots side by side

---

### SLIDE 13 — Project Structure

**Title:** Code Organization

```
main.py              → Entry point
inventory/           → Business logic (services, utils)
ui/                  → Presentation (pages, dialogs, theme)
database_setup.sql   → Schema + seed data
```

**Key Design Patterns:**
- Service Layer Pattern (separation of concerns)
- Singleton Session Manager
- Observer Pattern (session change listeners)
- Base Service inheritance

---

### SLIDE 14 — Future Enhancements

**Title:** Future Roadmap

- Barcode scanner integration
- Export reports to PDF/Excel
- Multi-location warehouse support
- Cloud database option
- REST API for mobile access
- Email notifications for low stock
- Multi-language support
- Invoice generation (PDF)

---

### SLIDE 15 — Thank You

**Title:** Thank You

**Contact:** BEE Tech

**Demo:** Run the application
```bash
pip install -r requirements.txt
mysql -u root -p < database_setup.sql
python main.py
```

**Default Login:** admin / admin123

---

## 8. DESIGN TIPS FOR PPT

- **Primary Color:** Blue #1A73E8 (matches app theme)
- **Dark Background:** #1E1E2E (for dark-mode slides)
- **Text Color:** White on dark, #2C3E50 on light
- **Font:** Segoe UI, Arial, or Helvetica
- **Icons:** Use icons for features (database, cart, chart, lock, user)
- **Screenshots:** Run the app and capture actual UI
- **Diagrams:** Use draw.io or Mermaid for architecture/ER diagrams
- **Layout:** Keep text minimal, use bullet points
- **Animation:** Subtle fade-in for slides, no excessive effects
