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


# New transactional decorator
def transactional(func):
    """Decorator to manage database transactions"""
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()  # commit if no error
            return result
        except Exception as e:
            conn.rollback()  # rollback if error
            raise e
    return wrapper


@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))


# Example usage
update_user_email(user_id=1, new_email="Crawford_Cartwright@hotmail.com")
print("User email updated successfully!")
