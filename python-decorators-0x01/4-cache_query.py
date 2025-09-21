import time
import sqlite3
import functools

# cache storage
query_cache = {}

def with_db_connection(func):
    """Decorator to handle opening and closing the DB connection."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect("users.db")
        try:
            result = func(conn, *args, **kwargs)
        finally:
            conn.close()
        return result
    return wrapper

def cache_query(func):
    """Decorator to cache query results."""
    @functools.wraps(func)
    def wrapper(conn, query, *args, **kwargs):
        if query in query_cache:
            print("Fetching from cache...")
            return query_cache[query]
        result = func(conn, query, *args, **kwargs)
        query_cache[query] = result
        return result
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

# First call → runs query and caches
users = fetch_users_with_cache(query="SELECT * FROM users")
print(users)

# Second call → fetches from cache
users_again = fetch_users_with_cache(query="SELECT * FROM users")
print(users_again)
