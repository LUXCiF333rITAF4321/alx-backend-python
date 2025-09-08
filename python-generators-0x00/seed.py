#!/usr/bin/python3
"""
seed.py

Prototypes:
- connect_db()
- create_database(connection)
- connect_to_prodev()
- create_table(connection)
- insert_data(connection, data)
- stream_user_data(connection)  -> generator
"""
import os
import csv
import uuid
import mysql.connector

MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "root")
PRODEV_DB = "ALX_prodev"
TABLE_NAME = "user_data"


def connect_db():
    """Connect to MySQL server (no specific DB)."""
    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL server: {err}")
        return None


def create_database(connection):
    """Create ALX_prodev database if it does not exist."""
    try:
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {PRODEV_DB};")
        connection.commit()
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error creating database {PRODEV_DB}: {err}")


def connect_to_prodev():
    """Connect to the ALX_prodev database and return the connection."""
    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=PRODEV_DB
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to database {PRODEV_DB}: {err}")
        return None


def create_table(connection):
    """Create user_data table if it doesn't exist."""
    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        user_id CHAR(36) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        age DECIMAL(5,0) NOT NULL,
        UNIQUE KEY unique_email (email)
    );
    """
    try:
        cursor = connection.cursor()
        cursor.execute(create_table_sql)
        connection.commit()
        print("Table user_data created successfully")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error creating table {TABLE_NAME}: {err}")


def insert_data(connection, csv_path):
    """
    Insert data from a CSV to the user_data table.
    CSV expected columns: either (user_id,name,email,age) or (name,email,age)
    Will not duplicate rows by user_id or email.
    """
    if not os.path.isfile(csv_path):
        print(f"CSV file not found: {csv_path}")
        return

    try:
        cursor = connection.cursor()
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            inserted = 0
            for row in reader:
                user_id = row.get("user_id") or str(uuid.uuid4())
                name = row.get("name", "").strip()
                email = row.get("email", "").strip()
                age_raw = row.get("age", "").strip()
                if age_raw == "":
                    print(f"Skipping row with missing age: {row}")
                    continue
                try:
                    age = int(float(age_raw))
                except ValueError:
                    print(f"Skipping row with invalid age: {row}")
                    continue

                cursor.execute(
                    f"SELECT 1 FROM {TABLE_NAME} WHERE user_id = %s OR email = %s LIMIT 1",
                    (user_id, email)
                )
                if cursor.fetchone():
                    continue

                cursor.execute(
                    f"INSERT INTO {TABLE_NAME} (user_id, name, email, age) VALUES (%s, %s, %s, %s)",
                    (user_id, name, email, age)
                )
                inserted += 1

        connection.commit()
        cursor.close()
        if inserted:
            print(f"Inserted {inserted} rows into {TABLE_NAME}")
        else:
            print("No new rows inserted (all rows exist or CSV empty).")
    except Exception as e:
        print(f"Error inserting data: {e}")


def stream_user_data(connection):
    """
    Generator that streams rows from user_data one by one.
    Yields tuples: (user_id, name, email, age)
    """
    cursor = connection.cursor()
    try:
        cursor.execute(f"SELECT user_id, name, email, age FROM {TABLE_NAME}")
        for row in cursor:
            yield row
    finally:
        cursor.close()
