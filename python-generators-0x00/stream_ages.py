#!/usr/bin/python3
"""
4-stream_ages.py

Generator to stream user ages and compute average age without loading
all data into memory.
"""

import seed  # your existing seed.py


def stream_user_ages():
    """Generator that yields ages of users one by one."""
    conn = seed.connect_to_prodev()
    if not conn:
        return

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT age FROM user_data")

    for row in cursor:  # loop 1
        yield row["age"]

    cursor.close()
    conn.close()


def calculate_average_age():
    """Calculate average age using the generator."""
    total = 0
    count = 0
    for age in stream_user_ages():  # loop 2
        total += age
        count += 1

    if count == 0:
        print("No users in database.")
        return

    average = total / count
    print(f"Average age of users: {average:.2f}")


if __name__ == "__main__":
    calculate_average_age()
