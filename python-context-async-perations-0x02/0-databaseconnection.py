import sqlite3
import os


class DatabaseConnection:
    """
    A context manager class to handle database connections automatically.
    
    This class manages opening and closing database connections using
    the __enter__ and __exit__ methods to ensure proper resource cleanup.
    """
    
    def __init__(self, db_name="example.db"):
        """
        Initialize the DatabaseConnection with a database name.
        
        Args:
            db_name (str): Name of the database file
        """
        self.db_name = db_name
        self.connection = None
        self.cursor = None
    
    def __enter__(self):
        """
        Enter the context manager - open database connection.
        
        Returns:
            sqlite3.Cursor: Database cursor for executing queries
        """
        try:
            # Create connection to database
            self.connection = sqlite3.connect(self.db_name)
            self.cursor = self.connection.cursor()
            
            # Create users table if it doesn't exist (for demonstration)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    age INTEGER
                )
            ''')
            
            # Insert sample data if table is empty
            self.cursor.execute("SELECT COUNT(*) FROM users")
            if self.cursor.fetchone()[0] == 0:
                sample_users = [
                    ('Alice Johnson', 'alice@example.com', 28),
                    ('Bob Smith', 'bob@example.com', 34),
                    ('Charlie Brown', 'charlie@example.com', 22),
                    ('Diana Prince', 'diana@example.com', 30)
                ]
                self.cursor.executemany(
                    "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
                    sample_users
                )
                self.connection.commit()
            
            print(f"Database connection established to {self.db_name}")
            return self.cursor
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            if self.connection:
                self.connection.close()
            raise
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager - close database connection.
        
        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred  
            exc_tb: Exception traceback if an exception occurred
        """
        if self.cursor:
            self.cursor.close()
        
        if self.connection:
            if exc_type is None:
                # No exception occurred, commit any pending transactions
                self.connection.commit()
                print("Database connection closed successfully")
            else:
                # Exception occurred, rollback any pending transactions
                self.connection.rollback()
                print(f"Database connection closed due to error: {exc_val}")
            
            self.connection.close()
        
        # Return False to propagate any exceptions
        return False


def main():
    """
    Demonstration of using the DatabaseConnection context manager.
    """
    print("=== Database Context Manager Demo ===\n")
    
    # Use the context manager with 'with' statement
    try:
        with DatabaseConnection("example.db") as cursor:
            # Perform the required query
            print("Executing query: SELECT * FROM users")
            cursor.execute("SELECT * FROM users")
            
            # Fetch and print results
            results = cursor.fetchall()
            
            if results:
                print("\nQuery Results:")
                print("-" * 50)
                print(f"{'ID':<5} {'Name':<15} {'Email':<20} {'Age':<5}")
                print("-" * 50)
                
                for row in results:
                    print(f"{row[0]:<5} {row[1]:<15} {row[2]:<20} {row[3]:<5}")
            else:
                print("No users found in the database.")
                
    except Exception as e:
        print(f"Error occurred: {e}")
    
    print(f"\n=== Demo completed ===")


if __name__ == "__main__":
    main()
