import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="inventory_db"
)

print("Connected Successfully")

conn.close()
