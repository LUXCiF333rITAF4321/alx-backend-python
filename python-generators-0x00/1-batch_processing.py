#!/usr/bin/python3
"""
1-batch_processing.py

Generators to fetch users in batches and process them.
"""

import seed  # your existing seed.py


def stream_users_in_batches(batch_size):
    """
    Generator that fetches users from the database in batches of size `batch_size`.
    Yields a list of user dictionaries per batch.
    """
    conn = seed.connect_to_prodev()
    if not conn:
        return

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_data")

    batch = []
    for row in cursor:  # loop 1
        batch.append(row)
        if len(batch) == batch_size:
            yield batch
            batch = []

    if batch:
        yield batch  # yield remaining rows

    cursor.close()
    conn.close()


def batch_processing(batch_size):
    """
    Processes each batch to filter users over the age of 25.
    Yields each user dictionary individually.
    """
    for batch in stream_users_in_batches(batch_size):  # loop 2
        for user in batch:  # loop 3
            if user["age"] > 25:
                print(user)
