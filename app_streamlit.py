import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="📦 Inventory Management System",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
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

# Database connection
@st.cache_resource
def get_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="inventory_db"
        )
        return conn
    except Error as e:
        st.error(f"❌ Database Connection Failed: {e}")
        st.info("⚠️ Make sure MySQL is running and database is configured correctly.")
        return None

# Title
st.title("📦 Inventory Management System")
st.markdown("---")

# Sidebar navigation
st.sidebar.title("🔧 Navigation")
page = st.sidebar.radio(
    "Select an option:",
    ["🏠 Dashboard", "➕ Add Product", "📋 View Products", "👥 Add Supplier", 
     "🛒 Purchase", "💳 Sell", "⚠️ Low Stock", "📊 Reports"]
)

conn = get_connection()

if conn is None:
    st.error("Cannot proceed without database connection")
    st.stop()

cursor = conn.cursor()

# ============ Dashboard ============
if page == "🏠 Dashboard":
    st.header("Dashboard Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        cursor.execute("SELECT COUNT(*) FROM Products")
        total_products = cursor.fetchone()[0]
        col1.metric("📦 Total Products", total_products)
        
        cursor.execute("SELECT SUM(stock_quantity) FROM Products")
        total_stock = cursor.fetchone()[0] or 0
        col2.metric("📊 Total Stock", total_stock)
        
        cursor.execute("SELECT COUNT(*) FROM Suppliers")
        total_suppliers = cursor.fetchone()[0]
        col3.metric("👥 Total Suppliers", total_suppliers)
        
        cursor.execute("SELECT COUNT(*) FROM Products WHERE stock_quantity < 10")
        low_stock = cursor.fetchone()[0]
        col4.metric("⚠️ Low Stock Items", low_stock, delta=None)
    except Error as e:
        st.error(f"Error loading dashboard: {e}")

# ============ Add Product ============
elif page == "➕ Add Product":
    st.header("Add New Product")
    
    with st.form("add_product_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            product_name = st.text_input("Product Name")
        
        with col2:
            price = st.number_input("Price ($)", min_value=0.0, step=0.01)
        
        stock_quantity = st.number_input("Stock Quantity", min_value=0, step=1)
        
        submitted = st.form_submit_button("✅ Add Product")
        
        if submitted:
            if product_name.strip():
                try:
                    cursor.execute(
                        "INSERT INTO Products(product_name, price, stock_quantity) VALUES(%s, %s, %s)",
                        (product_name, price, stock_quantity)
                    )
                    conn.commit()
                    st.success(f"✅ Product '{product_name}' added successfully!")
                except Error as e:
                    st.error(f"Error adding product: {e}")
                    conn.rollback()
            else:
                st.warning("Product name cannot be empty")

# ============ View Products ============
elif page == "📋 View Products":
    st.header("All Products")
    
    try:
        cursor.execute("SELECT product_id, product_name, price, stock_quantity FROM Products ORDER BY product_id")
        products = cursor.fetchall()
        
        if products:
            df = pd.DataFrame(
                products,
                columns=["ID", "Product Name", "Price ($)", "Stock Quantity"]
            )
            
            # Display as table
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Summary statistics
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Products", len(df))
            col2.metric("Total Stock Value", f"${(df['Price ($)'] * df['Stock Quantity']).sum():.2f}")
            col3.metric("Avg Price", f"${df['Price ($)'].mean():.2f}")
        else:
            st.info("No products found. Add products using the 'Add Product' page.")
    except Error as e:
        st.error(f"Error retrieving products: {e}")

# ============ Add Supplier ============
elif page == "👥 Add Supplier":
    st.header("Add New Supplier")
    
    with st.form("add_supplier_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            supplier_name = st.text_input("Supplier Name")
        
        with col2:
            contact = st.text_input("Contact Number")
        
        email = st.text_input("Email Address")
        
        submitted = st.form_submit_button("✅ Add Supplier")
        
        if submitted:
            if supplier_name.strip():
                try:
                    cursor.execute(
                        "INSERT INTO Suppliers(supplier_name, contact_info, email) VALUES(%s, %s, %s)",
                        (supplier_name, contact, email)
                    )
                    conn.commit()
                    st.success(f"✅ Supplier '{supplier_name}' added successfully!")
                except Error as e:
                    st.error(f"Error adding supplier: {e}")
                    conn.rollback()
            else:
                st.warning("Supplier name cannot be empty")

# ============ Purchase Product ============
elif page == "🛒 Purchase":
    st.header("Purchase Product")
    
    try:
        cursor.execute("SELECT product_id, product_name FROM Products")
        products = cursor.fetchall()
        
        if products:
            product_dict = {name: pid for pid, name in products}
            
            with st.form("purchase_form"):
                product_name = st.selectbox("Select Product", list(product_dict.keys()))
                quantity = st.number_input("Quantity to Purchase", min_value=1, step=1)
                
                submitted = st.form_submit_button("✅ Purchase")
                
                if submitted:
                    product_id = product_dict[product_name]
                    try:
                        cursor.execute(
                            "UPDATE Products SET stock_quantity = stock_quantity + %s WHERE product_id = %s",
                            (quantity, product_id)
                        )
                        conn.commit()
                        st.success(f"✅ Purchased {quantity} units of {product_name}")
                    except Error as e:
                        st.error(f"Error processing purchase: {e}")
                        conn.rollback()
        else:
            st.warning("No products available. Add products first.")
    except Error as e:
        st.error(f"Error loading products: {e}")

# ============ Sell Product ============
elif page == "💳 Sell":
    st.header("Sell Product")
    
    try:
        cursor.execute("SELECT product_id, product_name, stock_quantity FROM Products")
        products = cursor.fetchall()
        
        if products:
            product_dict = {f"{name} (Stock: {stock})": (pid, stock) for pid, name, stock in products}
            
            with st.form("sell_form"):
                product_name = st.selectbox("Select Product", list(product_dict.keys()))
                product_id, available_stock = product_dict[product_name]
                
                quantity = st.number_input("Quantity to Sell", min_value=1, max_value=available_stock, step=1)
                
                submitted = st.form_submit_button("✅ Sell")
                
                if submitted:
                    try:
                        cursor.execute(
                            "UPDATE Products SET stock_quantity = stock_quantity - %s WHERE product_id = %s",
                            (quantity, product_id)
                        )
                        conn.commit()
                        st.success(f"✅ Sold {quantity} units")
                    except Error as e:
                        st.error(f"Error processing sale: {e}")
                        conn.rollback()
        else:
            st.warning("No products available.")
    except Error as e:
        st.error(f"Error loading products: {e}")

# ============ Low Stock Report ============
elif page == "⚠️ Low Stock":
    st.header("Low Stock Report")
    
    try:
        cursor.execute(
            "SELECT product_id, product_name, stock_quantity FROM Products WHERE stock_quantity < 10 ORDER BY stock_quantity"
        )
        low_stock_products = cursor.fetchall()
        
        if low_stock_products:
            df = pd.DataFrame(
                low_stock_products,
                columns=["ID", "Product Name", "Stock Quantity"]
            )
            
            st.warning(f"⚠️ {len(df)} products have low stock (less than 10 units)")
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.success("✅ No low stock items! Everything is well stocked.")
    except Error as e:
        st.error(f"Error loading low stock report: {e}")

# ============ Reports ============
elif page == "📊 Reports":
    st.header("Sales & Inventory Reports")
    
    try:
        cursor.execute(
            "SELECT product_name, stock_quantity, price, (stock_quantity * price) as total_value FROM Products ORDER BY total_value DESC"
        )
        report_data = cursor.fetchall()
        
        if report_data:
            df = pd.DataFrame(
                report_data,
                columns=["Product Name", "Stock Quantity", "Price ($)", "Total Value ($)"]
            )
            
            # Summary
            st.subheader("📊 Inventory Summary")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Products", len(df))
            col2.metric("Total Items in Stock", df["Stock Quantity"].sum())
            col3.metric("Total Inventory Value", f"${df['Total Value ($)'].sum():.2f}")
            
            # Detailed Report
            st.subheader("Product Details")
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Charts
            st.subheader("📈 Analytics")
            col1, col2 = st.columns(2)
            
            with col1:
                st.bar_chart(df.set_index("Product Name")["Stock Quantity"])
            
            with col2:
                st.bar_chart(df.set_index("Product Name")["Total Value ($)"])
        else:
            st.info("No data available for reports.")
    except Error as e:
        st.error(f"Error loading reports: {e}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>📦 Inventory Management System | Built with Streamlit</p>
    <p><small>Last updated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</small></p>
</div>
""", unsafe_allow_html=True)
