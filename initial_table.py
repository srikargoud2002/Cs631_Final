import mysql.connector
from mysql.connector import errorcode
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
            raise_on_warnings=True
        )
    except mysql.connector.Error as err:
        print(f"Connection error: {err}")
        return None

# Table definitions
TABLES = {
    'CUSTOMER': """
        CREATE TABLE CUSTOMER (
            CID VARCHAR(5) NOT NULL,
            FName VARCHAR(20) NOT NULL,
            LName VARCHAR(20) NOT NULL,
            Email VARCHAR(50) NOT NULL UNIQUE,
            Address VARCHAR(250) ,
            Phone VARCHAR(12) UNIQUE,
            Status VARCHAR(10) CHECK (Status IN ('platinum', 'gold', 'silver', 'bronze')),
            PRIMARY KEY (CID)
        )
    """,
    'SILVER_AND_ABOVE': """
        CREATE TABLE SILVER_AND_ABOVE (
            CID VARCHAR(5) NOT NULL,
            CreditLine DECIMAL(10,2),
            PRIMARY KEY (CID),
            FOREIGN KEY (CID) REFERENCES CUSTOMER(CID) ON DELETE CASCADE
        )
    """,
    'CREDIT_CARD': """
        CREATE TABLE CREDIT_CARD (
            CCNumber VARCHAR(20) NOT NULL,
            SecNumber VARCHAR(4) NOT NULL,
            OwnerName VARCHAR(50) NOT NULL,
            CCType VARCHAR(15),
            BillingAddress VARCHAR(250),
            ExpDate DATE,
            StoredCardCID VARCHAR(5),
            PRIMARY KEY (CCNumber,StoredCardCID),
            FOREIGN KEY (StoredCardCID) REFERENCES CUSTOMER(CID) ON DELETE CASCADE
        )
    """,
    'SHIPPING_ADDRESS': """
        CREATE TABLE SHIPPING_ADDRESS (
            CID VARCHAR(5) NOT NULL,
            SAName VARCHAR(30) NOT NULL,
            RecipientName VARCHAR(50),
            SNumber VARCHAR(10),
            Street VARCHAR(50),
            City VARCHAR(25),
            State VARCHAR(25),
            Country VARCHAR(25),
            Zip VARCHAR(10),
            PRIMARY KEY (CID, SAName),
            FOREIGN KEY (CID) REFERENCES CUSTOMER(CID) ON DELETE CASCADE
        )
    """,
    'BASKET': """
        CREATE TABLE BASKET (
            BID VARCHAR(7) NOT NULL,
            CID VARCHAR(5),
            PRIMARY KEY (BID),
            FOREIGN KEY (CID) REFERENCES CUSTOMER(CID) ON DELETE CASCADE
        )
    """,
    'TRANSACTIONS': """
        CREATE TABLE TRANSACTIONS (
            TransactionID INT AUTO_INCREMENT PRIMARY KEY,
            BID VARCHAR(7) NOT NULL,
            CID VARCHAR(5) NOT NULL,
            SAName VARCHAR(30) NOT NULL,
            TDate DATE,
            CCNumber VARCHAR(20) NOT NULL,
            TTag VARCHAR(20) DEFAULT 'Pending',
            FOREIGN KEY (CID, SAName) REFERENCES SHIPPING_ADDRESS(CID, SAName) ON DELETE CASCADE,
            FOREIGN KEY (CCNumber) REFERENCES CREDIT_CARD(CCNumber) ON DELETE CASCADE,
            FOREIGN KEY (BID) REFERENCES BASKET(BID) ON DELETE CASCADE
        )
    """,
    'PRODUCT': """
        CREATE TABLE PRODUCT (
            PID VARCHAR(4) NOT NULL,
            PName VARCHAR(50) NOT NULL UNIQUE,
            PType VARCHAR(30),
            PPrice DECIMAL(10,2),
            PQuantity INT DEFAULT 0,
            Description VARCHAR(255),
            PRIMARY KEY (PID)
        )
    """,
    'APPEARS_IN': """
        CREATE TABLE APPEARS_IN (
            BID VARCHAR(7) NOT NULL,
            PID VARCHAR(4) NOT NULL,
            Quantity INT,
            PriceSold DECIMAL(10,2),
            PRIMARY KEY (BID, PID),
            FOREIGN KEY (BID) REFERENCES BASKET(BID) ON DELETE CASCADE,
            FOREIGN KEY (PID) REFERENCES PRODUCT(PID) ON DELETE CASCADE
        )
    """,
    'OFFER_PRODUCT': """
        CREATE TABLE OFFER_PRODUCT (
            PID VARCHAR(4) NOT NULL,
            OfferPrice DECIMAL(10,2) NOT NULL,
            PRIMARY KEY (PID),
            FOREIGN KEY (PID) REFERENCES PRODUCT(PID) ON DELETE CASCADE
        )
    """,
    'COMPUTER': """
        CREATE TABLE COMPUTER (
            PID VARCHAR(4) NOT NULL,
            CPUType VARCHAR(30),
            PRIMARY KEY (PID),
            FOREIGN KEY (PID) REFERENCES PRODUCT(PID) ON DELETE CASCADE
        )
    """,
    'PRINTER': """
        CREATE TABLE PRINTER (
            PID VARCHAR(4) NOT NULL,
            PrinterType VARCHAR(25),
            Resolution VARCHAR(10),
            PRIMARY KEY (PID),
            FOREIGN KEY (PID) REFERENCES PRODUCT(PID) ON DELETE CASCADE
        )
    """,
    'LAPTOP': """
        CREATE TABLE LAPTOP (
            PID VARCHAR(4) NOT NULL,
            BType VARCHAR(25),
            Weight DECIMAL(4,2),
            PRIMARY KEY (PID),
            FOREIGN KEY (PID) REFERENCES PRODUCT(PID) ON DELETE CASCADE
        )
    """
}

def drop_database(cursor):
    try:
        cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
        print(f"Dropped existing database `{DB_NAME}`.")
    except mysql.connector.Error as err:
        print(f"Error dropping database: {err}")
        exit(1)

def create_database(cursor):
    try:
        cursor.execute(f"CREATE DATABASE {DB_NAME}")
        print(f"Created new database `{DB_NAME}`.")
    except mysql.connector.Error as err:
        print(f"Error creating database: {err}")
        exit(1)

def create_tables(connection):
    cursor = connection.cursor()
    for name, ddl in TABLES.items():
        try:
            print(f"Creating table `{name}`...")
            cursor.execute(ddl)
            print(f"Table `{name}` created successfully.")
        except mysql.connector.Error as err:
            print(f"Error creating table `{name}`: {err}")
    cursor.close()

def main():
    conn = get_connection()
    if not conn:
        return

    cursor = conn.cursor()
    drop_database(cursor)
    create_database(cursor)
    cursor.execute(f"USE {DB_NAME}")
    create_tables(conn)
    conn.commit()
    conn.close()
    print("All tables created successfully.")

if __name__ == "__main__":
    main()
