import mysql.connector


class InsufficientStockError(Exception):
    pass


conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="inventory_db"
)

cursor = conn.cursor()

while True:

    print("\n===== INVENTORY MANAGEMENT SYSTEM =====")
    print("1. Add Product")
    print("2. View Products")
    print("3. Add Supplier")
    print("4. Purchase Product")
    print("5. Sell Product")
    print("6. Low Stock Report")
    print("7. Sales Summary")
    print("8. Exit")

    choice = input("Enter Choice: ")

    if choice == "1":

        name = input("Enter Product Name: ")
        price = float(input("Enter Price: "))
        stock = int(input("Enter Stock Quantity: "))

        cursor.execute(
            """
            INSERT INTO Products(product_name,price,stock_quantity)
            VALUES(%s,%s,%s)
            """,
            (name, price, stock)
        )

        conn.commit()

        print("✅ Product Added Successfully")

    elif choice == "2":

        cursor.execute("SELECT * FROM Products")

        rows = cursor.fetchall()

        print("\nPRODUCT LIST")

        for row in rows:
            print(row)

    elif choice == "3":

        supplier_name = input("Enter Supplier Name: ")
        contact = input("Enter Contact Number: ")

        cursor.execute(
            """
            INSERT INTO Suppliers(supplier_name,contact)
            VALUES(%s,%s)
            """,
            (supplier_name, contact)
        )

        conn.commit()

        print("✅ Supplier Added Successfully")

    elif choice == "4":

        product_id = int(input("Enter Product ID: "))
        quantity = int(input("Enter Purchase Quantity: "))

        cursor.execute(
            """
            INSERT INTO Purchases(product_id,quantity,purchase_date)
            VALUES(%s,%s,CURDATE())
            """,
            (product_id, quantity)
        )

        cursor.execute(
            """
            UPDATE Products
            SET stock_quantity = stock_quantity + %s
            WHERE product_id = %s
            """,
            (quantity, product_id)
        )

        conn.commit()

        print("✅ Purchase Recorded Successfully")

    elif choice == "5":

        product_id = int(input("Enter Product ID: "))
        quantity = int(input("Enter Sale Quantity: "))

        cursor.execute(
            """
            SELECT stock_quantity
            FROM Products
            WHERE product_id=%s
            """,
            (product_id,)
        )

        result = cursor.fetchone()

        if result is None:
            print("❌ Product Not Found")
            continue

        current_stock = result[0]

        try:

            if quantity > current_stock:
                raise InsufficientStockError(
                    "Insufficient Stock Available"
                )

            cursor.execute(
                """
                INSERT INTO Sales(product_id,quantity,sale_date)
                VALUES(%s,%s,CURDATE())
                """,
                (product_id, quantity)
            )

            cursor.execute(
                """
                UPDATE Products
                SET stock_quantity = stock_quantity - %s
                WHERE product_id = %s
                """,
                (quantity, product_id)
            )

            conn.commit()

            print("✅ Sale Recorded Successfully")

        except InsufficientStockError as e:
            print("❌", e)

    elif choice == "6":

        cursor.execute(
            """
            SELECT *
            FROM Products
            WHERE stock_quantity < 5
            """
        )

        rows = cursor.fetchall()

        print("\nLOW STOCK PRODUCTS")

        if len(rows) == 0:
            print("No Low Stock Products")

        for row in rows:
            print(row)

    elif choice == "7":

        cursor.execute(
            """
            SELECT product_id,
                   SUM(quantity)
            FROM Sales
            GROUP BY product_id
            """
        )

        rows = cursor.fetchall()

        print("\nSALES SUMMARY")

        if len(rows) == 0:
            print("No Sales Recorded")

        for row in rows:
            print(
                "Product ID:",
                row[0],
                "Total Sold:",
                row[1]
            )

    elif choice == "8":

        print("Thank You")
        break

    else:
        print("Invalid Choice")

conn.close()