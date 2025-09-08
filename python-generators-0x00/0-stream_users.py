#!/usr/bin/python3
"""
0-stream_users.py

Generator function to fetch rows from user_data table one by one.
"""

import seed  # use your existing seed.py for DB connection


def stream_users():
    """Generator that yields each user as a dictionary."""
    conn = seed.connect_to_prodev()
    if not conn:
        return  # exit if connection failed

    cursor = conn.cursor(dictionary=True)  # fetch rows as dict
    cursor.execute("SELECT * FROM user_data")

    for row in cursor:  # only 1 loop allowed
        yield row

    cursor.close()
    conn.close()
