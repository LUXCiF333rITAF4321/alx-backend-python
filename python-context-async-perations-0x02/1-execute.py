import sqlite3
import os


class ExecuteQuery:
    """
    A reusable context manager class that handles database connections 
    and executes queries automatically.
    
    This class manages opening/closing database connections and 
    executing queries with parameters using __enter__ and __exit__ methods.
    """
    
    def __init__(self, db_name="example.db", query=None, params=None):
        """
        Initialize the ExecuteQuery context manager.
        
        Args:
            db_name (str): Name of the database file
            query (str): SQL query to execute
            params (tuple): Parameters for the query
        """
        self.db_name = db_name
        self.query = query
        self.params = params if params is not None else ()
        self.connection = None
        self.cursor = None
        self.results = None
    
    def __enter__(self):
        """
        Enter the context manager - open connection and execute query.
        
        Returns:
            list: Query results
        """
        try:
            # Establish database connection
            self.connection = sqlite3.connect(self.db_name)
            self.cursor = self.connection.cursor()
            
            # Setup database with sample data if needed
            self._setup_database()
            
            # Execute the query if provided
            if self.query:
                print(f"Executing query: {self.query}")
                if self.params:
                    print(f"With parameters: {self.params}")
                    self.cursor.execute(self.query, self.params)
                else:
                    self.cursor.execute(self.query)
                
                # Fetch results
                self.results = self.cursor.fetchall()
                
            print(f"Database connection established to {self.db_name}")
            return self.results
            
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
                print("Query executed successfully, connection closed")
            else:
                # Exception occurred, rollback any pending transactions
                self.connection.rollback()
                print(f"Connection closed due to error: {exc_val}")
            
            self.connection.close()
        
        # Return False to propagate any exceptions
        return False
    
    def _setup_database(self):
        """
        Helper method to set up the database with sample data.
        This ensures the demo works even with a fresh database.
        """
        # Create users table if it doesn't exist
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
                ('Diana Prince', 'diana@example.com', 30),
                ('Eve Wilson', 'eve@example.com', 19),
                ('Frank Miller', 'frank@example.com', 45),
                ('Grace Lee', 'grace@example.com', 26),
                ('Henry Davis', 'henry@example.com', 31)
            ]
            self.cursor.executemany(
                "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
                sample_users
            )
            self.connection.commit()


def main():
    """
    Demonstration of using the ExecuteQuery context manager.
    """
    print("=== ExecuteQuery Context Manager Demo ===\n")
    
    # The required query and parameter
    query = "SELECT * FROM users WHERE age > ?"
    age_threshold = 25
    
    try:
        # Use the context manager with the specified query and parameter
        with ExecuteQuery("example.db", query, (age_threshold,)) as results:
            
            if results:
                print(f"\nUsers with age > {age_threshold}:")
                print("-" * 55)
                print(f"{'ID':<5} {'Name':<15} {'Email':<20} {'Age':<5}")
                print("-" * 55)
                
                for row in results:
                    print(f"{row[0]:<5} {row[1]:<15} {row[2]:<20} {row[3]:<5}")
                
                print(f"\nFound {len(results)} users older than {age_threshold}")
            else:
                print(f"No users found with age > {age_threshold}")
    
    except Exception as e:
        print(f"Error occurred: {e}")
    
    print("\n=== Additional Demo: Different Query ===")
    
    # Demo with a different query
    try:
        with ExecuteQuery("example.db", "SELECT name, age FROM users WHERE age BETWEEN ? AND ?", (25, 35)) as results:
            if results:
                print(f"\nUsers between ages 25-35:")
                print("-" * 25)
                print(f"{'Name':<15} {'Age':<5}")
                print("-" * 25)
                
                for row in results:
                    print(f"{row[0]:<15} {row[1]:<5}")
    
    except Exception as e:
        print(f"Error occurred: {e}")
    
    print(f"\n=== Demo completed ===")


if __name__ == "__main__":
    main()
