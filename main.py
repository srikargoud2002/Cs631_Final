import streamlit as st
import mysql.connector
from dotenv import load_dotenv
import os
import random
import string
import re
from datetime import date

load_dotenv()

# Database connection
def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )

# Utility to generate unique customer ID
def generate_customer_id():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT CID FROM CUSTOMER ORDER BY LENGTH(CID) DESC, CID DESC LIMIT 1")
    last = cursor.fetchone()
    if last:
        last_cid = last[0]  
        number_part = int(last_cid[1:]) 
        new_number = number_part + 1
    else:
        new_number = 1  
    new_cid = f"C{new_number:03d}"
    cursor.close()
    conn.close()
    return new_cid

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# Phone format check
def is_valid_phone(phone):
    return re.match(r"^\d{10}$", phone)
# Register new customer
def insert_customer(cid, fname, lname, email, address, phone, status, creditline):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM CUSTOMER WHERE Email = %s", (email,))
        if cursor.fetchone():
            st.error("This email is already registered.")
            return

        cursor.execute("SELECT 1 FROM CUSTOMER WHERE Phone = %s", (phone,))
        if cursor.fetchone():
            st.error("This phone number is already registered.")
            return

        cursor.execute("""
            INSERT INTO CUSTOMER (CID, FName, LName, Email, Address, Phone, Status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (cid, fname, lname, email, address, phone, status))

        if status in ('silver', 'gold', 'platinum'):
            cursor.execute("INSERT INTO SILVER_AND_ABOVE (CID, CreditLine) VALUES (%s, %s)", (cid, creditline))

        conn.commit()
        st.success(f"Customer registered successfully with ID: {cid}")
    except mysql.connector.Error as err:
        st.error(f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()

# Validate login
def validate_customer(cid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT FName, LName FROM CUSTOMER WHERE CID = %s", (cid,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result
def is_valid_cc(ccnum):
    return re.match(r"^\d{13,19}$", ccnum)

def is_valid_secnum(secnum):
    return re.match(r"^\d{3,4}$", secnum)
def is_valid_zip(zipc):
    return re.match(r"^\d{5}$", zipc)
# Add credit card
def add_credit_card(ccnum, secnum, owner, cctype, billing, expdate, cid):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO CREDIT_CARD (CCNumber, SecNumber, OwnerName, CCType, BillingAddress, ExpDate, StoredCardCID)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (ccnum, secnum, owner, cctype, billing, expdate, cid))
        conn.commit()
        st.success("Credit card added successfully.")
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

# Add shipping address
def add_shipping_address(cid, saname, recipient, snum, street, city, state, country, zipc):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO SHIPPING_ADDRESS (CID, SAName, RecipientName, SNumber, Street, City, State, Country, Zip)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (cid, saname, recipient, snum, street, city, state, country, zipc))
        conn.commit()
        st.success("Shipping address added successfully.")
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

# Streamlit UI
st.title("Online Store Interface")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.cid = None
    st.session_state.user_name = ""

menu = st.sidebar.selectbox("Select Option", [
    "Register Customer",
    "Login and Manage Account",
    "Online Shopping",
    "Sale Statistics",
    "Full Customer View"
])

if menu == "Register Customer":
    st.header("Customer Registration")
    generated_cid = generate_customer_id()
    st.text("\u26A0\ufe0f Remember your Customer ID for future login purposes")
    st.text(f"Your generated Customer ID: {generated_cid}")

    fname = st.text_input("First Name")
    lname = st.text_input("Last Name")
    email = st.text_input("Email")
    address = st.text_area("Address")
    phone = st.text_input("Phone")
    status = st.selectbox("Status", ["bronze","silver","gold","platinum"])

    creditline = None
    if status in ["platinum", "gold", "silver"]:
        creditline = st.number_input("Credit Line", min_value=0.0, format="%.2f")

    if st.button("Register"):
        if not all([fname.strip(), lname.strip(), email.strip(), address.strip(), phone.strip(), status.strip()]):
            st.error("All fields are required. Please fill out every field.")
        elif not is_valid_email(email):
            st.error("Invalid email format.")
        elif not is_valid_phone(phone):
            st.error("Phone number must be 10 digits.")
        elif status in ["platinum", "gold", "silver"]:
            if creditline is None or creditline <= 0.0:
                st.error("Credit line must be greater than 0 for Silver and above customers.")
            elif status == "platinum" and not (750 <= creditline <= 800):
                st.error("Platinum customers must have a credit line between 750 and 800.")
            elif status == "gold" and not (680 <= creditline < 750):
                st.error("Gold customers must have a credit line between 680 and 749.99.")
            elif status == "silver" and not (600 <= creditline < 680):
                st.error("Silver customers must have a credit line between 600 and 679.99.")
            else:
                insert_customer(generated_cid, fname, lname, email, address, phone, status, creditline)
        else:
            insert_customer(generated_cid, fname, lname, email, address, phone, status, creditline)

elif menu == "Login and Manage Account":
    if not st.session_state.logged_in:
        st.header("Customer Login")
        cid = st.text_input("Enter your Customer ID")
        if st.button("Login"):
            user = validate_customer(cid)
            if user:
                st.session_state.logged_in = True
                st.session_state.cid = cid
                st.session_state.user_name = f"{user[0]} {user[1]}"
                st.experimental_rerun()
            else:
                st.error("Customer ID not found.")

    if st.session_state.logged_in:
        st.success(f"Welcome, {st.session_state.user_name}!")
        action = st.selectbox("What would you like to do?", ["Add Credit Card", "Add Shipping Address"])

        if action == "Add Credit Card":
            ccnum = st.text_input("Card Number")
            secnum = st.text_input("Security Code")
            owner = st.text_input("Owner Name")
            cctype = st.selectbox("Card Type", ["Visa", "MasterCard", "RuPay"])
            billing = st.text_input("Billing Address")
            expdate = st.date_input("Expiration Date")

            if st.button("Save Credit Card"):
                if not all([ccnum.strip(), secnum.strip(), owner.strip(), cctype.strip(), billing.strip(), expdate]):
                    st.error("All credit card fields are required.")
                elif not is_valid_cc(ccnum):
                    st.error("Invalid credit card number format It Should be between 13-19.")
                elif not is_valid_secnum(secnum):
                    st.error("Security code must be 3 or 4 digits.")
                elif expdate <= date.today():
                    st.error("Expiration date must be in the future.")
                else:
                    add_credit_card(ccnum, secnum, owner, cctype, billing, expdate, st.session_state.cid)

        elif action == "Add Shipping Address":
            saname = st.text_input("Address Nickname")
            recipient = st.text_input("Recipient Name")
            snum = st.text_input("Street Number")
            street = st.text_input("Street Name")
            city = st.text_input("City")
            state = st.text_input("State")
            country = st.text_input("Country")
            zipc = st.text_input("Zip Code")
            if st.button("Save Shipping Address"):
                if not all([saname.strip(), recipient.strip(), snum.strip(), street.strip(), city.strip(), state.strip(), country.strip(), zipc.strip()]):
                    st.error("All shipping address fields are required.")
                elif not is_valid_zip(zipc):
                    st.error("Invalid zip code. Must be 5 digits.")
                else:
                    add_shipping_address(st.session_state.cid, saname, recipient, snum, street, city, state, country, zipc)

        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.cid = None
            st.session_state.user_name = ""
            st.experimental_rerun()

from datetime import date

# Generate new basket ID for every checkout
def generate_basket_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))

def get_products(filter_type=None):
    conn = get_connection()
    cursor = conn.cursor()
    if filter_type and filter_type.lower() != "all":
        cursor.execute("SELECT * FROM PRODUCT WHERE PType = %s", (filter_type.lower(),))
    else:
        cursor.execute("SELECT * FROM PRODUCT")
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return products

def add_to_basket(bid, cid, pid, qty, price):
    conn = get_connection()
    cursor = conn.cursor()

    # Ensure BASKET is created once for this BID
    cursor.execute("SELECT 1 FROM BASKET WHERE BID = %s", (bid,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO BASKET (BID, CID) VALUES (%s, %s)", (bid, cid))

    cursor.execute("""
        INSERT INTO APPEARS_IN (BID, PID, Quantity, PriceSold)
        VALUES (%s, %s, %s, %s)
    """, (bid, pid, qty, price))

    conn.commit()
    cursor.close()
    conn.close()

def get_product_details(pid, ptype):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if ptype == 'laptops':
        cursor.execute("""
            SELECT  BType, Weight
            FROM LAPTOP 
            WHERE PID = %s
        """, (pid,))
    elif ptype == 'computers':
        cursor.execute("""
            SELECT CPUType
            FROM COMPUTER
            WHERE PID = %s
        """, (pid,))
    elif ptype == 'printers':
        cursor.execute("""
            SELECT PrinterType, Resolution
            FROM PRINTER
            WHERE PID = %s
        """, (pid,))
    else:
        cursor.close()
        conn.close()
        return None

    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result

def place_transaction(bid, cid, saname, ccnumber):
    conn = get_connection()
    cursor = conn.cursor()

    # Insert into TRANSACTIONS table
    cursor.execute("""
        INSERT INTO TRANSACTIONS (BID, CID, SAName, TDate, CCNumber, TTag)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (bid, cid, saname, date.today(), ccnumber, "Pending"))

    # Deduct quantities from PRODUCT table
    cursor.execute("SELECT PID, Quantity FROM APPEARS_IN WHERE BID = %s", (bid,))
    items = cursor.fetchall()

    for pid, qty in items:
        cursor.execute("""
            UPDATE PRODUCT
            SET PQuantity = PQuantity - %s
            WHERE PID = %s AND PQuantity >= %s
        """, (qty, pid, qty))

    conn.commit()
    cursor.close()
    conn.close()

def get_shipping_addresses(cid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SAName FROM SHIPPING_ADDRESS WHERE CID = %s", (cid,))
    result = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return result

def get_credit_cards(cid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT CCNumber FROM CREDIT_CARD WHERE StoredCardCID = %s", (cid,))
    result = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return result

# Shopping UI
if menu == "Online Shopping":
    if "shopping_logged_in" not in st.session_state:
        st.session_state.shopping_logged_in = False
        st.session_state.shopping_cid = ""

    if not st.session_state.shopping_logged_in:
        st.header("Customer Login")
        cid = st.text_input("Enter Customer ID")
        if st.button("Login"):
            user = validate_customer(cid)
            if user:
                st.session_state.shopping_logged_in = True
                st.session_state.shopping_cid = cid
                st.session_state.shopping_name = f"{user[0]} {user[1]}"
                st.experimental_rerun()
            else:
                st.error("Invalid Customer ID")

    if st.session_state.shopping_logged_in:
        st.success(f"Welcome, {st.session_state.shopping_name}!")

        filter_option = st.selectbox("Filter Products By Type", ["ALL", "laptops", "printers", "computers"])
        products = get_products(filter_option)

        # Temporary in-session basket
        if "basket" not in st.session_state:
            st.session_state.basket = []

        st.subheader("Available Products")
        for product in products:
            pid, pname, ptype, price, qty, desc = product
            specs = get_product_details(pid, ptype)

            with st.expander(f"{pname} (${price})"):
                st.markdown(f"**Description:** {desc}")
                st.markdown(f"**In Stock:** {qty}")
                
                if specs:
                    st.markdown("**🔧 Specifications:**")
                    if ptype == 'laptops':
                        st.markdown(f"- Body Type: {specs.get('BType', 'N/A')}")
                        st.markdown(f"- Weight: {specs.get('Weight', 'N/A')} kg")
                    elif ptype == 'computers':
                        st.markdown(f"- CPU: {specs.get('CPUType', 'N/A')}")
                    elif ptype == 'printers':
                        st.markdown(f"- Type: {specs.get('PrinterType', 'N/A')}")
                        st.markdown(f"- Resolution: {specs.get('Resolution', 'N/A')}")

                quantity = st.number_input(f"Quantity for {pid}", min_value=1, max_value=qty, key=pid)
                if st.button(f"Add {pname} to Basket", key=f"add_{pid}"):
                    st.session_state.basket.append((pid, quantity, price))
                    st.success(f"Added {quantity} of {pname} to basket.")

        st.subheader("Checkout")
        selected_address = st.selectbox("Select Shipping Address", get_shipping_addresses(st.session_state.shopping_cid))
        selected_card = st.selectbox("Select Credit Card", get_credit_cards(st.session_state.shopping_cid))

        if st.button("Place Order"):
            new_bid = generate_basket_id()
            for pid, qty, price in st.session_state.basket:
                add_to_basket(new_bid, st.session_state.shopping_cid, pid, qty, price)
            place_transaction(new_bid, st.session_state.shopping_cid, selected_address, selected_card)
            st.session_state.basket = []  # Clear after order
            st.success(f"Order placed successfully! Transaction ID created.")

        if st.button("Logout"):
            st.session_state.shopping_logged_in = False
            st.session_state.shopping_cid = ""
            st.session_state.basket = []
            st.experimental_rerun()

        st.subheader("📜 Order History")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT T.TransactionID, T.TDate, T.TTag, P.PName, A.Quantity, A.PriceSold
            FROM TRANSACTIONS T
            JOIN APPEARS_IN A ON T.BID = A.BID
            JOIN PRODUCT P ON A.PID = P.PID
            WHERE T.CID = %s
            ORDER BY T.TDate DESC
        """, (st.session_state.shopping_cid,))
        history = cursor.fetchall()
        cursor.close()
        conn.close()

        if history:
            for t_id, t_date, t_tag, pname, qty, price in history:
                st.markdown(f"**Transaction ID**: {t_id}  |  **Date**: {t_date}  |  **Status**: {t_tag}")
                st.markdown(f"Product: {pname} | Quantity: {qty} | Price: ${price:.2f}")
                st.markdown("---")
        else:
            st.info("No transactions found.")

if menu == "Sale Statistics":
    st.header("📊 Sales & Customer Analytics")
    stat_option = st.selectbox("Select a statistic to view:", [
        "1. Total Amount Charged Per Credit Card",
        "2. Top 10 Customers by Spending",
        "3. Most Frequently Sold Products (Date Range)",
        "4. Products Sold to Most Distinct Customers (Date Range)",
        "5. Max Basket Total Per Credit Card (Date Range)",
        "6. Avg Selling Price per Product Type (Date Range)"
    ])

    conn = get_connection()
    cursor = conn.cursor()

    if stat_option == "1. Total Amount Charged Per Credit Card":
        st.subheader("Total Amount Per Credit Card")
        cursor.execute("""
            SELECT CCNumber, SUM(A.Quantity * A.PriceSold) AS TotalCharged
            FROM TRANSACTIONS T
            JOIN APPEARS_IN A ON T.BID = A.BID
            GROUP BY CCNumber
            ORDER BY TotalCharged DESC;
        """)
        rows = cursor.fetchall()
        st.dataframe(rows, use_container_width=True)

    elif stat_option == "2. Top 10 Customers by Spending":
        st.subheader("Top 10 Customers by Spending")
        cursor.execute("""
            SELECT C.CID, C.FName, C.LName, SUM(A.Quantity * A.PriceSold) AS TotalSpent
            FROM CUSTOMER C
            JOIN TRANSACTIONS T ON C.CID = T.CID
            JOIN APPEARS_IN A ON T.BID = A.BID
            GROUP BY C.CID
            ORDER BY TotalSpent DESC
            LIMIT 10;
        """)
        rows = cursor.fetchall()
        st.dataframe(rows, use_container_width=True)

    elif stat_option.startswith("3") or stat_option.startswith("4") or stat_option.startswith("5") or stat_option.startswith("6"):
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")

        if st.button("Run Analysis"):
            if stat_option.startswith("3"):
                cursor.execute("""
                    SELECT P.PName, SUM(A.Quantity) AS UnitsSold
                    FROM TRANSACTIONS T
                    JOIN APPEARS_IN A ON T.BID = A.BID
                    JOIN PRODUCT P ON A.PID = P.PID
                    WHERE T.TDate BETWEEN %s AND %s
                    GROUP BY P.PID
                    ORDER BY UnitsSold DESC;
                """, (start_date, end_date))

            elif stat_option.startswith("4"):
                cursor.execute("""
                    SELECT P.PName, COUNT(DISTINCT T.CID) AS UniqueBuyers
                    FROM TRANSACTIONS T
                    JOIN APPEARS_IN A ON T.BID = A.BID
                    JOIN PRODUCT P ON A.PID = P.PID
                    WHERE T.TDate BETWEEN %s AND %s
                    GROUP BY P.PID
                    ORDER BY UniqueBuyers DESC;
                """, (start_date, end_date))

            elif stat_option.startswith("5"):
                cursor.execute("""
                                SELECT CCNumber, MAX(BasketTotal) AS MaxBasketTotal
                                FROM (
                                    SELECT T.CCNumber, T.BID, SUM(A.Quantity * A.PriceSold) AS BasketTotal
                                    FROM TRANSACTIONS T
                                    JOIN APPEARS_IN A ON T.BID = A.BID
                                    WHERE T.TDate BETWEEN %s AND %s
                                    GROUP BY T.CCNumber, T.BID
                                ) AS BasketSums
                                GROUP BY CCNumber;
                """, (start_date, end_date))

            elif stat_option.startswith("6"):
                cursor.execute("""
                    SELECT P.PType, AVG(A.PriceSold) AS AvgSoldPrice
                    FROM TRANSACTIONS T
                    JOIN APPEARS_IN A ON T.BID = A.BID
                    JOIN PRODUCT P ON A.PID = P.PID
                    WHERE T.TDate BETWEEN %s AND %s
                    GROUP BY P.PType;
                """, (start_date, end_date))

            result = cursor.fetchall()
            st.dataframe(result, use_container_width=True)

    cursor.close()
    conn.close()

elif menu == "Full Customer View":
    st.header("🔍 View Full Customer Details")
    input_cid = st.text_input("Enter Customer ID")

    if st.button("Show Details"):
        if input_cid.strip():
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            # CUSTOMER
            cursor.execute("SELECT * FROM CUSTOMER WHERE CID = %s", (input_cid,))
            customer = cursor.fetchone()
            if not customer:
                st.error("Customer not found.")
            else:
                st.subheader("🧍 Customer Profile")
                st.json(customer)

                # CREDIT LINE
                cursor.execute("SELECT CreditLine FROM SILVER_AND_ABOVE WHERE CID = %s", (input_cid,))
                credit = cursor.fetchone()
                st.subheader("💳 Credit Line")
                if credit:
                    st.success(f"Credit Line: ${credit['CreditLine']:.2f}")
                else:
                    st.info("No credit line (Bronze tier customer).")

                # CREDIT CARDS
                cursor.execute("SELECT CCType, CCNumber, ExpDate FROM CREDIT_CARD WHERE StoredCardCID = %s", (input_cid,))
                cards = cursor.fetchall()
                st.subheader("💳 Saved Credit Cards")
                if cards:
                    for card in cards:
                        st.write(f"{card['CCType']} ending in {card['CCNumber'][-4:]}, Exp: {card['ExpDate']}")
                else:
                    st.info("No credit cards saved.")

                # SHIPPING ADDRESSES
                cursor.execute("SELECT * FROM SHIPPING_ADDRESS WHERE CID = %s", (input_cid,))
                addresses = cursor.fetchall()
                st.subheader("🏠 Shipping Addresses")
                if addresses:
                    for addr in addresses:
                        st.write(f"{addr['SAName']} ({addr['RecipientName']}): {addr['Street']}, {addr['City']}, {addr['State']} {addr['Zip']}")
                else:
                    st.info("No shipping addresses.")

                # BASKETS
                cursor.execute("SELECT BID FROM BASKET WHERE CID = %s", (input_cid,))
                baskets = cursor.fetchall()
                st.subheader("🧺 Baskets")
                if baskets:
                    for b in baskets:
                        st.write(f"Basket ID: {b['BID']}")
                else:
                    st.info("No baskets found.")

                # TRANSACTIONS
                cursor.execute("""
                    SELECT T.TransactionID, T.TDate, T.TTag, T.CCNumber, T.SAName
                    FROM TRANSACTIONS T
                    WHERE T.CID = %s
                    ORDER BY T.TDate DESC
                """, (input_cid,))
                transactions = cursor.fetchall()
                st.subheader("🧾 Transactions")
                if transactions:
                    for tx in transactions:
                        st.markdown(f"- **ID:** {tx['TransactionID']}, **Date:** {tx['TDate']}, **Status:** {tx['TTag']}, **Card:** ending {tx['CCNumber'][-4:]}, **Shipping:** {tx['SAName']}")
                else:
                    st.info("No transactions found.")

                # PRODUCTS PURCHASED
                cursor.execute("""
                    SELECT A.BID, P.PName, A.Quantity, A.PriceSold
                    FROM APPEARS_IN A
                    JOIN PRODUCT P ON A.PID = P.PID
                    JOIN BASKET B ON A.BID = B.BID
                    WHERE B.CID = %s
                """, (input_cid,))
                items = cursor.fetchall()
                st.subheader("📦 Products in Baskets")
                if items:
                    for item in items:
                        st.write(f"Basket {item['BID']}: {item['PName']} × {item['Quantity']} @ ${item['PriceSold']:.2f}")
                else:
                    st.info("No products purchased.")

            cursor.close()
            conn.close()
        else:
            st.warning("Please enter a valid Customer ID.")
