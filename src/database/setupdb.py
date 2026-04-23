#setupdb.py

import sqlite3

connection = sqlite3.connect('ecommerce.db')
cursor = connection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY,
    name TEXT,
    region TEXT,
    signup_date DATE
)''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    order_date DATE,
    total_amount REAL,
    FOREIGN KEY(customer_id) REFERENCES customers(id)
    )
''')

customers_data = [
    (1, 'Alice Smith', 'North', '2023-01-15'),
    (2, 'Bob Jones', 'South', '2023-02-20'),
    (3, 'Charlie Brown', 'East', '2023-03-10')
]

orders_data = [
    (101, 1, '2023-05-01', 150.00),
    (102, 2, '2023-05-02', 200.00),
    (103, 1, '2023-05-03', 50.00)
]

cursor.executemany('INSERT OR IGNORE INTO customers VALUES (?,?,?,?)', customers_data)
cursor.executemany('INSERT OR IGNORE INTO orders VALUES (?,?,?,?)', orders_data)

print("---- orders data: -----")
cursor.execute("SELECT * FROM orders")
for row in cursor.fetchall():
    print(row)

print("---- customer data: -----")
cursor.execute("SELECT * FROM customers")
for row in cursor.fetchall():
    print(row)


connection.commit()
connection.close()
print("Database 'ecommerce.db' created with sample data!")