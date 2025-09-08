#!/usr/bin/python3
"""
2-lazy_paginate.py

Generator to lazily fetch pages from the user_data table.
"""

import seed  # your existing seed.py


def paginate_users(page_size, offset):
    """Fetch a page of users from the database."""
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
    rows = cursor.fetchall()
    connection.close()
    return rows


def lazy_pagination(page_size):
    """Generator that yields one page at a time, lazily."""
    offset = 0
    while True:  # single loop
        page = paginate_users(page_size, offset)
        if not page:
            break
        yield page
        offset += page_size
