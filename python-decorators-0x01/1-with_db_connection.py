import sqlite3
import functools

def with_db_connection(func):
    """Decorator to handle opening and closing the database connection"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect("users.db")  # open connection
        try:
            result = func(conn, *args, **kwargs)  # pass conn into function
        finally:
            conn.close()  # close connection always
        return result
    return wrapper

@with_db_connection
def get_user_by_id(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()

# Example usage
user = get_user_by_id(user_id=1)
print(user)

