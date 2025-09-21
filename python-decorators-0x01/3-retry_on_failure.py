import time
import sqlite3
import functools

# Reuse the with_db_connection decorator
def with_db_connection(func):
    """Decorator to handle opening and closing the database connection"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect("users.db")  # open connection
        try:
            result = func(conn, *args, **kwargs)  # pass connection into function
        finally:
            conn.close()  # always close connection
        return result
    return wrapper


# Retry decorator
def retry_on_failure(retries=3, delay=2):
    """Retry function execution if it fails, with delay between retries"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    print(f"Attempt {attempts} failed: {e}")
                    if attempts >= retries:
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator


@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()


# Example usage
users = fetch_users_with_retry()
print(users)
