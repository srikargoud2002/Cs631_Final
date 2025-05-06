import mysql.connector
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

DB_NAME = 'srikar_final'

def get_connection():
    try:
        return mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=DB_NAME
        )
    except mysql.connector.Error as err:
        print(f"Connection error: {err}")
        return None

def insert_data():
    conn = get_connection()
    if not conn:
        return

    cursor = conn.cursor()

    # Product data
    product_data = [
        ('P001', 'Laptop A', 'laptops', 999.99, 20, '14" 8GB RAM, 256GB SSD'),
        ('P002', 'Laptop B', 'laptops', 1299.99, 15, '15.6" 16GB RAM, RTX GPU'),
        ('P003', 'Laptop C', 'laptops', 1099.99, 10, '13.3" 16GB RAM, 512GB SSD'),
        ('P004', 'Laptop D', 'laptops', 899.99, 18, '2-in-1 Touchscreen, 8GB RAM'),
        ('P005', 'Laptop E', 'laptops', 599.99, 25, '15.6" 4GB RAM, 128GB SSD'),
        ('P006', 'Printer X', 'printers', 149.99, 15, 'Color Inkjet Printer with WiFi'),
        ('P007', 'Printer Y', 'printers', 199.99, 8, 'Laser B/W, High-Speed'),
        ('P008', 'Printer Z', 'printers', 249.99, 12, 'All-in-One: Print, Scan, Fax'),
        ('P009', 'Printer Eco', 'printers', 299.99, 6, 'EcoTank Refillable System'),
        ('P010', 'Printer Photo', 'printers', 179.99, 10, 'High-res Color Photo Printer'),
        ('P011', 'Desktop A', 'computers', 749.99, 14, '8GB RAM, 256GB SSD'),
        ('P012', 'Desktop B', 'computers', 849.99, 12, '16GB RAM, SSD'),
        ('P013', 'Desktop C', 'computers', 1399.99, 8, 'RTX 3060, Gaming'),
        ('P014', 'Desktop D', 'computers', 699.99, 20, 'Mini PC, 8GB RAM, 512GB SSD'),
        ('P015', 'Desktop E', 'computers', 999.99, 10, 'All-in-One 21", 8GB RAM')
    ]
    cursor.executemany("""
        INSERT INTO PRODUCT (PID, PName, PType, PPrice, PQuantity, Description)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, product_data)

    # Laptops in COMPUTER
    cursor.executemany("INSERT INTO LAPTOP (PID, BType, Weight) VALUES (%s, %s, %s)", [
        ('P001', 'Ultrabook', 1.20),
        ('P002', 'Gaming', 2.50),
        ('P003', 'Business', 1.30),
        ('P004', 'Convertible', 1.40),
        ('P005', 'Budget', 2.00)
    ])

    # Desktops in COMPUTER
    cursor.executemany("INSERT INTO COMPUTER (PID, CPUType) VALUES (%s, %s)", [
        ('P011', 'Intel i5'),
        ('P012', 'Intel i5'),
        ('P013', 'Intel i7'),
        ('P014', 'AMD Ryzen 5'),
        ('P015', 'Intel i5')
    ])

    # PRINTER entries
    cursor.executemany("INSERT INTO PRINTER (PID, PrinterType, Resolution) VALUES (%s, %s, %s)", [
        ('P006', 'Inkjet', '1200x1200'),
        ('P007', 'Laser', '2400x600'),
        ('P008', 'All-in-One', '1200x1200'),
        ('P009', 'EcoTank', '4800x1200'),
        ('P010', 'Photo', '5760x1440')
    ])

    cursor.executemany("""
        INSERT INTO CUSTOMER (CID, FName, LName, Email, Address, Phone, Status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, [
        ('C001', 'Alice', 'Wong', 'alice@example.com', '123 Maple St', '1234567890', 'gold'),
        ('C002', 'Bob', 'Smith', 'bob@example.com', '456 Oak Ave', '2345678901', 'silver'),
        ('C003', 'Charlie', 'Johnson', 'charlie@example.com', '789 Pine Rd', '3456789012', 'platinum'),
        ('C004', 'Dana', 'Lee', 'dana@example.com', '135 Birch Ln', '4567890123', 'bronze')
    ])

    cursor.executemany("""
        INSERT INTO CREDIT_CARD (CCNumber, SecNumber, OwnerName, CCType, BillingAddress, ExpDate, StoredCardCID)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, [
        ('4111111111111111', '123', 'Alice Wong', 'Visa', '123 Maple St', '2026-05-01', 'C001'),
        ('5500000000000004', '456', 'Bob Smith', 'MasterCard', '456 Oak Ave', '2027-08-15', 'C002'),
        ('340000000000009', '789', 'Charlie Johnson', 'Amex', '789 Pine Rd', '2025-12-01', 'C003')
    ])

    cursor.executemany("""
        INSERT INTO SHIPPING_ADDRESS (CID, SAName, RecipientName, SNumber, Street, City, State, Country, Zip)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, [
        ('C001', 'Home', 'Alice Wong', '123', 'Maple St', 'Springfield', 'VA', 'USA', '22150'),
        ('C002', 'Office', 'Bob Smith', '456', 'Oak Ave', 'Arlington', 'VA', 'USA', '22203'),
        ('C003', 'Main', 'Charlie Johnson', '789', 'Pine Rd', 'Fairfax', 'VA', 'USA', '22030')
    ])

    cursor.executemany("""
        INSERT INTO BASKET (BID, CID)
        VALUES (%s, %s)
    """, [
        ('B1001', 'C001'),
        ('B1002', 'C002'),
        ('B1003', 'C003')
    ])

    cursor.executemany("""
        INSERT INTO TRANSACTIONS (BID, CID, SAName, TDate, CCNumber, TTag)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, [
        ('B1001', 'C001', 'Home', '2025-05-01', '4111111111111111', 'Completed'),
        ('B1002', 'C002', 'Office', '2025-05-02', '5500000000000004', 'Pending'),
        ('B1003', 'C003', 'Main', '2025-05-03', '340000000000009', 'Completed')
    ])

    cursor.executemany("""
        INSERT INTO APPEARS_IN (BID, PID, Quantity, PriceSold)
        VALUES (%s, %s, %s, %s)
    """, [
        ('B1001', 'P001', 1, 999.99),
        ('B1001', 'P006', 1, 149.99),
        ('B1002', 'P002', 1, 1299.99),
        ('B1003', 'P013', 1, 1399.99)
    ])

    cursor.executemany("""
        INSERT INTO OFFER_PRODUCT (PID, OfferPrice)
        VALUES (%s, %s)
    """, [
        ('P001', 899.99),
        ('P006', 129.99),
        ('P013', 1249.99)
    ])
    cursor.executemany("""
        INSERT INTO SILVER_AND_ABOVE (CID, CreditLine)
        VALUES (%s, %s)
    """, [
        ('C001', 690.00),
        ('C002', 610.00),
        ('C003', 730.00)
    ])    

    conn.commit()
    cursor.close()
    conn.close()
    print("Data inserted successfully.")

if __name__ == "__main__":
    insert_data()