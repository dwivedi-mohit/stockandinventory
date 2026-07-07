import os

while True:

    os.system("clear")

    print("=" * 50)
    print(" INVENTORY MANAGEMENT SYSTEM ")
    print("=" * 50)

    print("1. Add Product")
    print("2. View Products")
    print("3. Add Supplier")
    print("4. Purchase Product")
    print("5. Sell Product")
    print("6. Low Stock Report")
    print("7. Sales Summary")
    print("8. Exit")

    print("=" * 50)

    choice = input("Enter Choice: ")

    if choice == "8":
        break