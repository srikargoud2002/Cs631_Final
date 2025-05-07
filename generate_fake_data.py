import mysql.connector
from faker import Faker
import random
from datetime import date
from dotenv import load_dotenv
import os

load_dotenv()
fake = Faker()

DB_NAME = 'srikar_final'
STATUSES = ['bronze', 'silver', 'gold', 'platinum']

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=DB_NAME
    )

def generate_customer_id(index):
    return f"C{index:03d}"

def generate_basket_id():
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=7))

def generate_card_number():
    return ''.join(random.choices('1234567890', k=random.randint(13, 16)))

def insert_dummy_card(cursor):
    cursor.execute("""
        INSERT IGNORE INTO CREDIT_CARD (CCNumber, SecNumber, OwnerName, CCType, BillingAddress, ExpDate)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, ('4111111111111111', '123', 'Default Card', 'Visa', 'N/A', '2030-01-01'))

def generate_data(num_customers=50):
    conn = get_connection()
    cursor = conn.cursor()

    # Insert dummy card for bronze users
    insert_dummy_card(cursor)

    for i in range(6, num_customers + 6):  # Start from C006
        cid = generate_customer_id(i)
        fname = fake.first_name()
        lname = fake.last_name()
        email = fake.unique.email()
        address = fake.address().replace("\n", ", ")
        phone = fake.msisdn()[:10]
        status = random.choices(STATUSES, weights=[1, 2, 3, 2])[0]

        cursor.execute("""
            INSERT INTO CUSTOMER (CID, FName, LName, Email, Address, Phone, Status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (cid, fname, lname, email, address, phone, status))

        # Silver and above get credit lines
        if status in ['silver', 'gold', 'platinum']:
            creditline = {
                'silver': random.uniform(600, 700),
                'gold': random.uniform(700, 800),
                'platinum': random.uniform(750, 900)
            }[status]
            cursor.execute("INSERT INTO SILVER_AND_ABOVE (CID, CreditLine) VALUES (%s, %s)", (cid, round(creditline, 2)))

        # Credit Card
        cc_number = generate_card_number()
        if status != 'bronze':
            cursor.execute("""
                INSERT INTO CREDIT_CARD (CCNumber, SecNumber, OwnerName, CCType, BillingAddress, ExpDate, StoredCardCID)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (cc_number, str(random.randint(100, 999)), f"{fname} {lname}", random.choice(['Visa', 'MasterCard', 'Amex']),
                  address, fake.date_between(start_date='+1y', end_date='+3y'), cid))
        else:
            cc_number = '4111111111111111'  # Default card

        # Shipping Address
        cursor.execute("""
            INSERT INTO SHIPPING_ADDRESS (CID, SAName, RecipientName, SNumber, Street, City, State, Country, Zip)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (cid, 'Home', f"{fname} {lname}", fake.building_number(), fake.street_name(), fake.city(),
              fake.state_abbr(), 'USA', fake.zipcode()))

        # Basket
        bid = generate_basket_id()
        cursor.execute("INSERT INTO BASKET (BID, CID) VALUES (%s, %s)", (bid, cid))

        # Product selection
        cursor.execute("SELECT PID, PPrice FROM PRODUCT ORDER BY RAND() LIMIT %s", (random.randint(1, 3),))
        products = cursor.fetchall()
        total = 0

        for pid, base_price in products:
            qty = random.randint(1, 2)
            price = round(float(base_price) * random.uniform(0.9, 1.1), 2)
            total += qty * price
            cursor.execute("""
                INSERT INTO APPEARS_IN (BID, PID, Quantity, PriceSold)
                VALUES (%s, %s, %s, %s)
            """, (bid, pid, qty, price))

        # Transaction
        cursor.execute("""
            INSERT INTO TRANSACTIONS (BID, CID, SAName, TDate, CCNumber, TTag, TotalAmount)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (bid, cid, 'Home', fake.date_between(start_date='-60d', end_date='today'),
              cc_number, 'Completed', round(total, 2)))

    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ Inserted {num_customers} fake customers and associated data.")

if __name__ == "__main__":
    generate_data()
