import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

st.set_page_config(
    page_title="Inventory Management System",
    page_icon=":package:",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        background-color: #2E86DE;
        color: white;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #1C54B2;
    }
</style>
""", unsafe_allow_html=True)


def get_db():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS Products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        price REAL NOT NULL,
        stock_quantity INTEGER NOT NULL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS Suppliers (
        supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_name TEXT NOT NULL,
        contact_info TEXT,
        email TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS Transactions (
        transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        transaction_type TEXT,
        quantity INTEGER,
        transaction_date TEXT,
        FOREIGN KEY (product_id) REFERENCES Products(product_id)
    )""")
    if c.execute("SELECT COUNT(*) FROM Products").fetchone()[0] == 0:
        sample_products = [
            ("Laptop", 899.99, 15), ("Mouse", 25.50, 5),
            ("Keyboard", 75.00, 8), ("Monitor", 299.99, 3),
            ("USB Cable", 9.99, 50), ("Headphones", 149.99, 12),
            ("Webcam", 79.99, 7), ("Printer", 199.99, 2),
        ]
        c.executemany("INSERT INTO Products (product_name, price, stock_quantity) VALUES (?, ?, ?)", sample_products)
        sample_suppliers = [
            ("Tech Supplies Co.", "555-1001", "info@techsupply.com"),
            ("Electronics Plus", "555-2002", "sales@eplus.com"),
            ("Global Hardware", "555-3003", "contact@globalhw.com"),
        ]
        c.executemany("INSERT INTO Suppliers (supplier_name, contact_info, email) VALUES (?, ?, ?)", sample_suppliers)
        conn.commit()
    return conn


if "db_conn" not in st.session_state:
    st.session_state.db_conn = get_db()

conn = st.session_state.db_conn
cursor = conn.cursor()

st.title("Inventory Management System")
st.markdown("---")

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select an option:",
    ["Dashboard", "Add Product", "View Products", "Add Supplier",
     "Purchase", "Sell", "Low Stock", "Reports"]
)

if page == "Dashboard":
    st.header("Dashboard Overview")
    col1, col2, col3, col4 = st.columns(4)

    cursor.execute("SELECT COUNT(*) FROM Products")
    col1.metric("Total Products", cursor.fetchone()[0])

    cursor.execute("SELECT COALESCE(SUM(stock_quantity), 0) FROM Products")
    col2.metric("Total Stock", cursor.fetchone()[0])

    cursor.execute("SELECT COUNT(*) FROM Suppliers")
    col3.metric("Total Suppliers", cursor.fetchone()[0])

    cursor.execute("SELECT COUNT(*) FROM Products WHERE stock_quantity < 10")
    col4.metric("Low Stock Items", cursor.fetchone()[0])

    st.markdown("---")
    st.subheader("Recent Transactions")
    cursor.execute("""
        SELECT p.product_name, t.transaction_type, t.quantity, t.transaction_date
        FROM Transactions t JOIN Products p ON t.product_id = p.product_id
        ORDER BY t.transaction_id DESC LIMIT 10
    """)
    rows = cursor.fetchall()
    if rows:
        df = pd.DataFrame(rows, columns=["Product", "Type", "Quantity", "Date"])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No transactions yet.")

elif page == "Add Product":
    st.header("Add New Product")
    with st.form("add_product_form"):
        col1, col2 = st.columns(2)
        with col1:
            product_name = st.text_input("Product Name")
        with col2:
            price = st.number_input("Price ($)", min_value=0.0, step=0.01)
        stock_quantity = st.number_input("Stock Quantity", min_value=0, step=1)
        submitted = st.form_submit_button("Add Product")
        if submitted:
            if product_name.strip():
                cursor.execute(
                    "INSERT INTO Products (product_name, price, stock_quantity) VALUES (?, ?, ?)",
                    (product_name.strip(), price, stock_quantity)
                )
                conn.commit()
                st.success(f"Product '{product_name}' added successfully!")
                st.rerun()
            else:
                st.warning("Product name cannot be empty")

elif page == "View Products":
    st.header("All Products")
    cursor.execute("SELECT product_id, product_name, price, stock_quantity FROM Products ORDER BY product_id")
    products = cursor.fetchall()
    if products:
        df = pd.DataFrame(products, columns=["ID", "Product Name", "Price ($)", "Stock Quantity"])
        st.dataframe(df, use_container_width=True, hide_index=True)
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Products", len(df))
        col2.metric("Total Stock Value", f"${(df['Price ($)'] * df['Stock Quantity']).sum():.2f}")
        col3.metric("Avg Price", f"${df['Price ($)'].mean():.2f}")

        st.subheader("Delete Product")
        del_id = st.selectbox("Select product to delete", df["ID"].tolist(),
                              format_func=lambda x: f"{x} - {df[df['ID']==x]['Product Name'].values[0]}")
        if st.button("Delete", type="secondary"):
            cursor.execute("DELETE FROM Products WHERE product_id = ?", (del_id,))
            conn.commit()
            st.success("Product deleted!")
            st.rerun()
    else:
        st.info("No products found. Add products using the 'Add Product' page.")

elif page == "Add Supplier":
    st.header("Add New Supplier")
    with st.form("add_supplier_form"):
        col1, col2 = st.columns(2)
        with col1:
            supplier_name = st.text_input("Supplier Name")
        with col2:
            contact = st.text_input("Contact Number")
        email = st.text_input("Email Address")
        submitted = st.form_submit_button("Add Supplier")
        if submitted:
            if supplier_name.strip():
                cursor.execute(
                    "INSERT INTO Suppliers (supplier_name, contact_info, email) VALUES (?, ?, ?)",
                    (supplier_name.strip(), contact, email)
                )
                conn.commit()
                st.success(f"Supplier '{supplier_name}' added successfully!")
                st.rerun()
            else:
                st.warning("Supplier name cannot be empty")

    st.markdown("---")
    st.subheader("Current Suppliers")
    cursor.execute("SELECT supplier_id, supplier_name, contact_info, email FROM Suppliers")
    suppliers = cursor.fetchall()
    if suppliers:
        df = pd.DataFrame(suppliers, columns=["ID", "Name", "Contact", "Email"])
        st.dataframe(df, use_container_width=True, hide_index=True)

elif page == "Purchase":
    st.header("Purchase Product")
    cursor.execute("SELECT product_id, product_name, stock_quantity FROM Products")
    products = cursor.fetchall()
    if products:
        product_dict = {name: (pid, stock) for pid, name, stock in products}
        with st.form("purchase_form"):
            product_name = st.selectbox("Select Product", list(product_dict.keys()))
            quantity = st.number_input("Quantity to Purchase", min_value=1, step=1)
            submitted = st.form_submit_button("Purchase")
            if submitted:
                pid, _ = product_dict[product_name]
                cursor.execute("UPDATE Products SET stock_quantity = stock_quantity + ? WHERE product_id = ?",
                               (quantity, pid))
                cursor.execute(
                    "INSERT INTO Transactions (product_id, transaction_type, quantity, transaction_date) VALUES (?, 'Purchase', ?, ?)",
                    (pid, quantity, datetime.now().isoformat())
                )
                conn.commit()
                st.success(f"Purchased {quantity} units of {product_name}")
                st.rerun()
    else:
        st.warning("No products available. Add products first.")

elif page == "Sell":
    st.header("Sell Product")
    cursor.execute("SELECT product_id, product_name, stock_quantity FROM Products")
    products = cursor.fetchall()
    if products:
        product_dict = {f"{name} (Stock: {stock})": (pid, stock) for pid, name, stock in products}
        with st.form("sell_form"):
            product_choice = st.selectbox("Select Product", list(product_dict.keys()))
            pid, available_stock = product_dict[product_choice]
            quantity = st.number_input("Quantity to Sell", min_value=1, max_value=available_stock, step=1)
            submitted = st.form_submit_button("Sell")
            if submitted:
                cursor.execute("UPDATE Products SET stock_quantity = stock_quantity - ? WHERE product_id = ?",
                               (quantity, pid))
                cursor.execute(
                    "INSERT INTO Transactions (product_id, transaction_type, quantity, transaction_date) VALUES (?, 'Sale', ?, ?)",
                    (pid, quantity, datetime.now().isoformat())
                )
                conn.commit()
                st.success(f"Sold {quantity} units")
                st.rerun()
    else:
        st.warning("No products available.")

elif page == "Low Stock":
    st.header("Low Stock Report")
    cursor.execute("SELECT product_id, product_name, stock_quantity FROM Products WHERE stock_quantity < 10 ORDER BY stock_quantity")
    low_stock = cursor.fetchall()
    if low_stock:
        df = pd.DataFrame(low_stock, columns=["ID", "Product Name", "Stock Quantity"])
        st.warning(f"{len(df)} products have low stock (less than 10 units)")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.success("No low stock items! Everything is well stocked.")

elif page == "Reports":
    st.header("Sales & Inventory Reports")
    cursor.execute("""
        SELECT product_name, stock_quantity, price, (stock_quantity * price) as total_value
        FROM Products ORDER BY total_value DESC
    """)
    report_data = cursor.fetchall()
    if report_data:
        df = pd.DataFrame(report_data, columns=["Product Name", "Stock Quantity", "Price ($)", "Total Value ($)"])

        st.subheader("Inventory Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Products", len(df))
        col2.metric("Total Items in Stock", int(df["Stock Quantity"].sum()))
        col3.metric("Total Inventory Value", f"${df['Total Value ($)'].sum():.2f}")

        st.subheader("Product Details")
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.subheader("Analytics")
        col1, col2 = st.columns(2)
        with col1:
            st.bar_chart(df.set_index("Product Name")["Stock Quantity"])
        with col2:
            st.bar_chart(df.set_index("Product Name")["Total Value ($)"])
    else:
        st.info("No data available for reports.")

st.sidebar.markdown("---")
st.sidebar.info("This app uses in-memory SQLite. Data resets on page refresh.")
