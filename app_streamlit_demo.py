import streamlit as st
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

# Demo data
demo_products = [
    {"ID": 1, "Product Name": "Laptop", "Price ($)": 899.99, "Stock Quantity": 15},
    {"ID": 2, "Product Name": "Mouse", "Price ($)": 25.50, "Stock Quantity": 5},
    {"ID": 3, "Product Name": "Keyboard", "Price ($)": 75.00, "Stock Quantity": 8},
    {"ID": 4, "Product Name": "Monitor", "Price ($)": 299.99, "Stock Quantity": 3},
    {"ID": 5, "Product Name": "USB Cable", "Price ($)": 9.99, "Stock Quantity": 50},
]

demo_suppliers = [
    {"ID": 1, "Supplier Name": "Tech Supplies Co.", "Contact": "555-1001", "Email": "info@techsupply.com"},
    {"ID": 2, "Supplier Name": "Electronics Plus", "Contact": "555-2002", "Email": "sales@eplus.com"},
    {"ID": 3, "Supplier Name": "Global Hardware", "Contact": "555-3003", "Email": "contact@globalhw.com"},
]

# ============ Dashboard ============
if page == "🏠 Dashboard":
    st.header("Dashboard Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_products = len(demo_products)
    col1.metric("📦 Total Products", total_products)
    
    total_stock = sum([p["Stock Quantity"] for p in demo_products])
    col2.metric("📊 Total Stock", total_stock)
    
    total_suppliers = len(demo_suppliers)
    col3.metric("👥 Total Suppliers", total_suppliers)
    
    low_stock = sum([1 for p in demo_products if p["Stock Quantity"] < 10])
    col4.metric("⚠️ Low Stock Items", low_stock)

# ============ Add Product ============
elif page == "➕ Add Product":
    st.header("Add New Product")
    
    with st.form("add_product_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            product_name = st.text_input("Product Name", placeholder="e.g., Wireless Headphones")
        
        with col2:
            price = st.number_input("Price ($)", min_value=0.0, step=0.01)
        
        stock_quantity = st.number_input("Stock Quantity", min_value=0, step=1)
        
        submitted = st.form_submit_button("✅ Add Product")
        
        if submitted:
            if product_name.strip():
                st.success(f"✅ Product '{product_name}' added successfully!")
            else:
                st.warning("Product name cannot be empty")

# ============ View Products ============
elif page == "📋 View Products":
    st.header("All Products")
    
    if demo_products:
        df = pd.DataFrame(demo_products)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Products", len(df))
        col2.metric("Total Stock Value", f"${(df['Price ($)'] * df['Stock Quantity']).sum():.2f}")
        col3.metric("Avg Price", f"${df['Price ($)'].mean():.2f}")
    else:
        st.info("No products found. Add products using the 'Add Product' page.")

# ============ Add Supplier ============
elif page == "👥 Add Supplier":
    st.header("Add New Supplier")
    
    with st.form("add_supplier_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            supplier_name = st.text_input("Supplier Name", placeholder="e.g., Tech Wholesale Inc.")
        
        with col2:
            contact = st.text_input("Contact Number", placeholder="e.g., 555-1234")
        
        email = st.text_input("Email Address", placeholder="e.g., contact@supplier.com")
        
        submitted = st.form_submit_button("✅ Add Supplier")
        
        if submitted:
            if supplier_name.strip():
                st.success(f"✅ Supplier '{supplier_name}' added successfully!")
            else:
                st.warning("Supplier name cannot be empty")

# ============ Purchase Product ============
elif page == "🛒 Purchase":
    st.header("Purchase Product")
    
    if demo_products:
        product_names = [p["Product Name"] for p in demo_products]
        
        with st.form("purchase_form"):
            product_name = st.selectbox("Select Product", product_names)
            quantity = st.number_input("Quantity to Purchase", min_value=1, step=1)
            
            submitted = st.form_submit_button("✅ Purchase")
            
            if submitted:
                st.success(f"✅ Purchased {quantity} units of {product_name}")
    else:
        st.warning("No products available. Add products first.")

# ============ Sell Product ============
elif page == "💳 Sell":
    st.header("Sell Product")
    
    if demo_products:
        product_options = [f"{p['Product Name']} (Stock: {p['Stock Quantity']})" for p in demo_products]
        
        with st.form("sell_form"):
            product_choice = st.selectbox("Select Product", product_options)
            
            # Extract product and available stock
            selected_product = next((p for p in demo_products if p['Product Name'] in product_choice), None)
            available_stock = selected_product["Stock Quantity"] if selected_product else 0
            
            quantity = st.number_input("Quantity to Sell", min_value=1, max_value=available_stock, step=1)
            
            submitted = st.form_submit_button("✅ Sell")
            
            if submitted:
                st.success(f"✅ Sold {quantity} units of {selected_product['Product Name']}")
    else:
        st.warning("No products available. Add products first.")

# ============ Low Stock Report ============
elif page == "⚠️ Low Stock":
    st.header("Low Stock Alert")
    
    low_stock_items = [p for p in demo_products if p["Stock Quantity"] < 10]
    
    if low_stock_items:
        df_low = pd.DataFrame(low_stock_items)
        st.dataframe(df_low, use_container_width=True, hide_index=True)
        st.warning(f"⚠️ {len(low_stock_items)} items have low stock levels!")
    else:
        st.success("✅ All items have sufficient stock!")

# ============ Reports ============
elif page == "📊 Reports":
    st.header("Sales & Inventory Reports")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Inventory Summary")
        df_products = pd.DataFrame(demo_products)
        st.bar_chart(df_products.set_index("Product Name")["Stock Quantity"])
    
    with col2:
        st.subheader("Product Value Distribution")
        df_products["Product Value"] = df_products["Price ($)"] * df_products["Stock Quantity"]
        st.bar_chart(df_products.set_index("Product Name")["Product Value"])

st.sidebar.markdown("---")
st.sidebar.info("📌 **Demo Mode** - This is a preview. Deploy to see live data from your MySQL database.")
