import tkinter as tk

root = tk.Tk()

root.title("Inventory Management System")
root.geometry("700x500")

title = tk.Label(
    root,
    text="Inventory Management System",
    font=("Arial", 20, "bold")
)

title.pack(pady=20)

btn1 = tk.Button(
    root,
    text="Add Product",
    width=20
)

btn1.pack(pady=10)

btn2 = tk.Button(
    root,
    text="View Products",
    width=20
)

btn2.pack(pady=10)

btn3 = tk.Button(
    root,
    text="Add Supplier",
    width=20
)

btn3.pack(pady=10)

btn4 = tk.Button(
    root,
    text="Purchase Product",
    width=20
)

btn4.pack(pady=10)

btn5 = tk.Button(
    root,
    text="Sell Product",
    width=20
)

btn5.pack(pady=10)

root.mainloop()