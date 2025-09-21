import sqlite3
import uuid


class DatabaseConnection:
    """
    A context manager class to handle database connections automatically.
    
    This class manages opening and closing database connections using
    the __enter__ and __exit__ methods to ensure proper resource cleanup.
    """
    
    def __init__(self, db_name="airbnb_clone.db"):
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
            
            # Create users table based on the schema
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    first_name VARCHAR(50) NOT NULL,
                    last_name VARCHAR(50) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    phone_number VARCHAR(20),
                    role TEXT CHECK(role IN ('guest', 'host', 'admin')) NOT NULL DEFAULT 'guest',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert sample data if table is empty
            self.cursor.execute("SELECT COUNT(*) FROM users")
            if self.cursor.fetchone()[0] == 0:
                sample_users = [
                    (str(uuid.uuid4()), 'Alice', 'Johnson', 'alice@example.com', 'hash123', '+1234567890', 'guest'),
                    (str(uuid.uuid4()), 'Bob', 'Smith', 'bob@example.com', 'hash456', '+0987654321', 'host'),
                    (str(uuid.uuid4()), 'Charlie', 'Brown', 'charlie@example.com', 'hash789', '+1122334455', 'guest'),
                    (str(uuid.uuid4()), 'Diana', 'Prince', 'diana@example.com', 'hash101', '+5566778899', 'admin')
                ]
                self.cursor.executemany('''
                    INSERT INTO users (user_id, first_name, last_name, email, password_hash, phone_number, role) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', sample_users)
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
    print("=== Airbnb Database Context Manager Demo ===\n")
    
    # Use the context manager with 'with' statement
    try:
        with DatabaseConnection("airbnb_clone.db") as cursor:
            # Perform the required query
            print("Executing query: SELECT * FROM users")
            cursor.execute("SELECT * FROM users")
            
            # Fetch and print results
            results = cursor.fetchall()
            
            if results:
                print("\nQuery Results:")
                print("-" * 80)
                print(f"{'User ID':<40} {'Name':<20} {'Email':<25} {'Role':<10}")
                print("-" * 80)
                
                for row in results:
                    user_id, first_name, last_name, email, _, phone, role, created_at = row
                    full_name = f"{first_name} {last_name}"
                    print(f"{user_id:<40} {full_name:<20} {email:<25} {role:<10}")
            else:
                print("No users found in the database.")
                
    except Exception as e:
        print(f"Error occurred: {e}")
    
    print(f"\n=== Demo completed ===")


if __name__ == "__main__":
    main()
