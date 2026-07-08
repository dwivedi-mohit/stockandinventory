import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import mysql.connector
from mysql.connector import Error

class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management System")
        self.root.geometry("900x600")
        self.root.resizable(True, True)
        
        # Database connection
        self.conn = None
        self.cursor = None
        self.connect_db()
        
        # Create GUI
        self.create_widgets()
        
    def connect_db(self):
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="root",
                database="inventory_db"
            )
            self.cursor = self.conn.cursor()
        except Error as e:
            messagebox.showerror("Database Error", f"Connection failed: {e}\n\nMake sure MySQL is running and database is configured.")
            
    def create_widgets(self):
        # Title
        title = tk.Label(
            self.root,
            text="📦 Inventory Management System",
            font=("Arial", 22, "bold"),
            fg="#2c3e50"
        )
        title.pack(pady=15)
        
        # Button Frame
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=False)
        
        buttons = [
            ("➕ Add Product", self.add_product),
            ("📋 View Products", self.view_products),
            ("👥 Add Supplier", self.add_supplier),
            ("🛒 Purchase Product", self.purchase_product),
            ("💳 Sell Product", self.sell_product),
            ("⚠️ Low Stock Report", self.low_stock_report),
            ("📊 Sales Summary", self.sales_summary),
        ]
        
        for i, (text, command) in enumerate(buttons):
            btn = ttk.Button(
                button_frame,
                text=text,
                command=command,
                width=20
            )
            row = i // 2
            col = i % 2
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        
        # Display Frame
        display_frame = ttk.LabelFrame(self.root, text="Data Display", padding=10)
        display_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Text Widget with Scrollbar
        scrollbar = ttk.Scrollbar(display_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.display_text = tk.Text(
            display_frame,
            height=15,
            width=80,
            yscrollcommand=scrollbar.set
        )
        self.display_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.display_text.yview)
        
        # Status Bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def add_product(self):
        try:
            window = tk.Toplevel(self.root)
            window.title("Add Product")
            window.geometry("400x200")
            
            ttk.Label(window, text="Product Name:").pack(pady=5)
            name_entry = ttk.Entry(window, width=30)
            name_entry.pack(pady=5)
            
            ttk.Label(window, text="Price:").pack(pady=5)
            price_entry = ttk.Entry(window, width=30)
            price_entry.pack(pady=5)
            
            ttk.Label(window, text="Stock Quantity:").pack(pady=5)
            stock_entry = ttk.Entry(window, width=30)
            stock_entry.pack(pady=5)
            
            def save():
                name = name_entry.get()
                price = float(price_entry.get())
                stock = int(stock_entry.get())
                
                if not name:
                    messagebox.showerror("Error", "Product name is required")
                    return
                
                self.cursor.execute(
                    "INSERT INTO Products(product_name, price, stock_quantity) VALUES(%s, %s, %s)",
                    (name, price, stock)
                )
                self.conn.commit()
                messagebox.showinfo("Success", "✅ Product Added Successfully")
                window.destroy()
                self.status_var.set("Product added successfully")
                
            ttk.Button(window, text="Save", command=save).pack(pady=10)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def view_products(self):
        try:
            self.cursor.execute("SELECT product_id, product_name, price, stock_quantity FROM Products")
            products = self.cursor.fetchall()
            
            self.display_text.delete(1.0, tk.END)
            self.display_text.insert(tk.END, "=" * 80 + "\n")
            self.display_text.insert(tk.END, f"{'ID':<5} {'Product Name':<30} {'Price':<15} {'Stock':<15}\n")
            self.display_text.insert(tk.END, "=" * 80 + "\n")
            
            if products:
                for product in products:
                    self.display_text.insert(tk.END, f"{product[0]:<5} {product[1]:<30} ${product[2]:<14.2f} {product[3]:<15}\n")
            else:
                self.display_text.insert(tk.END, "No products found\n")
                
            self.status_var.set(f"Showing {len(products)} products")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def add_supplier(self):
        try:
            window = tk.Toplevel(self.root)
            window.title("Add Supplier")
            window.geometry("400x200")
            
            ttk.Label(window, text="Supplier Name:").pack(pady=5)
            name_entry = ttk.Entry(window, width=30)
            name_entry.pack(pady=5)
            
            ttk.Label(window, text="Contact:").pack(pady=5)
            contact_entry = ttk.Entry(window, width=30)
            contact_entry.pack(pady=5)
            
            ttk.Label(window, text="Email:").pack(pady=5)
            email_entry = ttk.Entry(window, width=30)
            email_entry.pack(pady=5)
            
            def save():
                name = name_entry.get()
                contact = contact_entry.get()
                email = email_entry.get()
                
                if not name:
                    messagebox.showerror("Error", "Supplier name is required")
                    return
                
                self.cursor.execute(
                    "INSERT INTO Suppliers(supplier_name, contact_info, email) VALUES(%s, %s, %s)",
                    (name, contact, email)
                )
                self.conn.commit()
                messagebox.showinfo("Success", "✅ Supplier Added Successfully")
                window.destroy()
                self.status_var.set("Supplier added successfully")
                
            ttk.Button(window, text="Save", command=save).pack(pady=10)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def purchase_product(self):
        try:
            product_id = simpledialog.askinteger("Purchase Product", "Enter Product ID:")
            if product_id:
                quantity = simpledialog.askinteger("Purchase Product", "Enter Quantity:")
                if quantity:
                    self.cursor.execute(
                        "UPDATE Products SET stock_quantity = stock_quantity + %s WHERE product_id = %s",
                        (quantity, product_id)
                    )
                    self.conn.commit()
                    messagebox.showinfo("Success", f"✅ Purchased {quantity} units")
                    self.status_var.set(f"Purchased {quantity} units of product {product_id}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def sell_product(self):
        try:
            product_id = simpledialog.askinteger("Sell Product", "Enter Product ID:")
            if product_id:
                quantity = simpledialog.askinteger("Sell Product", "Enter Quantity:")
                if quantity:
                    self.cursor.execute("SELECT stock_quantity FROM Products WHERE product_id = %s", (product_id,))
                    result = self.cursor.fetchone()
                    
                    if result and result[0] >= quantity:
                        self.cursor.execute(
                            "UPDATE Products SET stock_quantity = stock_quantity - %s WHERE product_id = %s",
                            (quantity, product_id)
                        )
                        self.conn.commit()
                        messagebox.showinfo("Success", f"✅ Sold {quantity} units")
                        self.status_var.set(f"Sold {quantity} units of product {product_id}")
                    else:
                        messagebox.showerror("Error", "Insufficient stock")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def low_stock_report(self):
        try:
            self.cursor.execute("SELECT product_id, product_name, stock_quantity FROM Products WHERE stock_quantity < 10")
            products = self.cursor.fetchall()
            
            self.display_text.delete(1.0, tk.END)
            self.display_text.insert(tk.END, "=" * 80 + "\n")
            self.display_text.insert(tk.END, "⚠️ LOW STOCK REPORT (Less than 10 units)\n")
            self.display_text.insert(tk.END, "=" * 80 + "\n")
            
            if products:
                for product in products:
                    self.display_text.insert(tk.END, f"ID: {product[0]} | Product: {product[1]} | Stock: {product[2]}\n")
            else:
                self.display_text.insert(tk.END, "No low stock items\n")
                
            self.status_var.set(f"Low stock items: {len(products)}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def sales_summary(self):
        try:
            self.cursor.execute(
                "SELECT product_name, SUM(stock_quantity) as total_stock FROM Products GROUP BY product_name"
            )
            results = self.cursor.fetchall()
            
            self.display_text.delete(1.0, tk.END)
            self.display_text.insert(tk.END, "=" * 80 + "\n")
            self.display_text.insert(tk.END, "📊 SALES SUMMARY\n")
            self.display_text.insert(tk.END, "=" * 80 + "\n")
            
            total_products = 0
            if results:
                for product in results:
                    self.display_text.insert(tk.END, f"Product: {product[0]} | Total Stock: {product[1]}\n")
                    total_products += product[1]
                
                self.display_text.insert(tk.END, "\n" + "=" * 80 + "\n")
                self.display_text.insert(tk.END, f"Total Items in Inventory: {total_products}\n")
            else:
                self.display_text.insert(tk.END, "No data available\n")
                
            self.status_var.set(f"Total items: {total_products}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()