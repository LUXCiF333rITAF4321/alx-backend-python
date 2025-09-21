import asyncio
import aiosqlite
import time
import uuid


async def setup_database(db_name="airbnb_concurrent.db"):
    """
    Set up the database with sample data for testing based on Airbnb schema.
    
    Args:
        db_name (str): Name of the database file
    """
    async with aiosqlite.connect(db_name) as db:
        # Create users table based on Airbnb schema
        await db.execute('''
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
        
        # Create properties table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS properties (
                property_id TEXT PRIMARY KEY,
                host_id TEXT NOT NULL,
                name VARCHAR(100) NOT NULL,
                description TEXT NOT NULL,
                location VARCHAR(100) NOT NULL,
                pricepernight DECIMAL(10,2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (host_id) REFERENCES users (user_id)
            )
        ''')
        
        # Check if users table is empty and insert sample data
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        count = await cursor.fetchone()
        await cursor.close()
        
        if count[0] == 0:
            # Sample users data
            sample_users = [
                (str(uuid.uuid4()), 'Alice', 'Johnson', 'alice@example.com', 'hash123', '+1234567890', 'guest'),
                (str(uuid.uuid4()), 'Bob', 'Smith', 'bob@example.com', 'hash456', '+0987654321', 'host'),
                (str(uuid.uuid4()), 'Charlie', 'Brown', 'charlie@example.com', 'hash789', '+1122334455', 'guest'),
                (str(uuid.uuid4()), 'Diana', 'Prince', 'diana@example.com', 'hash101', '+5566778899', 'host'),
                (str(uuid.uuid4()), 'Eve', 'Wilson', 'eve@example.com', 'hash202', '+2233445566', 'guest'),
                (str(uuid.uuid4()), 'Frank', 'Miller', 'frank@example.com', 'hash303', '+3344556677', 'host'),
                (str(uuid.uuid4()), 'Grace', 'Lee', 'grace@example.com', 'hash404', '+4455667788', 'admin'),
                (str(uuid.uuid4()), 'Henry', 'Davis', 'henry@example.com', 'hash505', '+5566778800', 'host'),
                (str(uuid.uuid4()), 'Iris', 'Chen', 'iris@example.com', 'hash606', '+6677889900', 'host'),
                (str(uuid.uuid4()), 'Jack', 'Williams', 'jack@example.com', 'hash707', '+7788990011', 'guest'),
                (str(uuid.uuid4()), 'Kate', 'Brown', 'kate@example.com', 'hash808', '+8899001122', 'host'),
                (str(uuid.uuid4()), 'Liam', 'Johnson', 'liam@example.com', 'hash909', '+9900112233', 'guest'),
                (str(uuid.uuid4()), 'Maya', 'Patel', 'maya@example.com', 'hash111', '+1122330044', 'host'),
                (str(uuid.uuid4()), 'Noah', 'Garcia', 'noah@example.com', 'hash222', '+2233441155', 'admin'),
                (str(uuid.uuid4()), 'Olivia', 'Martinez', 'olivia@example.com', 'hash333', '+3344552266', 'guest')
            ]
            
            await db.executemany('''
                INSERT INTO users (user_id, first_name, last_name, email, password_hash, phone_number, role) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', sample_users)
            
            # Get host users for properties
            host_cursor = await db.execute("SELECT user_id FROM users WHERE role = 'host'")
            hosts = await host_cursor.fetchall()
            await host_cursor.close()
            
            # Sample properties data
            if hosts:
                sample_properties = [
                    (str(uuid.uuid4()), hosts[0][0], 'Cozy Downtown Apartment', 'Beautiful 2BR apartment in city center', 'New York, NY', 150.00),
                    (str(uuid.uuid4()), hosts[1][0], 'Beach House Paradise', 'Stunning oceanfront villa with private beach', 'Miami, FL', 300.00),
                    (str(uuid.uuid4()), hosts[2][0], 'Mountain Cabin Retreat', 'Peaceful cabin in the mountains', 'Denver, CO', 120.00),
                    (str(uuid.uuid4()), hosts[3][0], 'Luxury Penthouse Suite', 'High-end penthouse with city views', 'Los Angeles, CA', 500.00),
                    (str(uuid.uuid4()), hosts[4][0], 'Historic Brownstone', 'Charming historic home in quiet neighborhood', 'Boston, MA', 180.00)
                ]
                
                await db.executemany('''
                    INSERT INTO properties (property_id, host_id, name, description, location, pricepernight) 
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', sample_properties)
            
            await db.commit()
            print("Sample Airbnb data inserted into database")


async def async_fetch_users(db_name="airbnb_concurrent.db"):
    """
    Asynchronous function to fetch all users from the database.
    
    Args:
        db_name (str): Name of the database file
        
    Returns:
        list: All users from the database
    """
    print("🔍 Starting async_fetch_users...")
    start_time = time.time()
    
    async with aiosqlite.connect(db_name) as db:
        # Simulate some processing time
        await asyncio.sleep(0.1)
        
        cursor = await db.execute("SELECT user_id, first_name, last_name, email, role, COALESCE(age, 25) as age FROM users")
        users = await cursor.fetchall()
        await cursor.close()
        
        end_time = time.time()
        print(f"✅ async_fetch_users completed in {end_time - start_time:.2f} seconds")
        
        return users


async def async_fetch_older_users(db_name="airbnb_concurrent.db"):
    """
    Asynchronous function to fetch users older than 40 from the database.
    
    Args:
        db_name (str): Name of the database file
        
    Returns:
        list: Users older than 40
    """
    print("🔍 Starting async_fetch_older_users...")
    start_time = time.time()
    
    async with aiosqlite.connect(db_name) as db:
        # Simulate some processing time
        await asyncio.sleep(0.15)
        
        # Create age column and update users to have ages for demo
        try:
            await db.execute('ALTER TABLE users ADD COLUMN age INTEGER DEFAULT 25')
        except:
            pass  # Column might already exist
        
        # Update some users to be older than 40
        await db.execute("UPDATE users SET age = 45 WHERE role = 'host' AND age IS NULL")
        await db.execute("UPDATE users SET age = 42 WHERE role = 'admin' AND age IS NULL")
        await db.execute("UPDATE users SET age = 41 WHERE first_name = 'Olivia' AND age IS NULL")
        await db.execute("UPDATE users SET age = 48 WHERE first_name = 'Frank' AND age IS NULL")
        await db.execute("UPDATE users SET age = 43 WHERE first_name = 'Maya' AND age IS NULL")
        
        cursor = await db.execute("SELECT user_id, first_name, last_name, email, role, age FROM users WHERE age > 40")
        older_users = await cursor.fetchall()
        await cursor.close()
        
        end_time = time.time()
        print(f"✅ async_fetch_older_users completed in {end_time - start_time:.2f} seconds")
        
        return older_users


async def fetch_concurrently():
    """
    Execute both database queries concurrently using asyncio.gather().
    
    This function demonstrates concurrent execution of multiple database queries.
    """
    print("🏠 === Airbnb Concurrent Database Queries Demo ===\n")
    
    # Setup database with sample data
    await setup_database()
    
    print("\n🚀 Executing queries concurrently using asyncio.gather()...")
    start_time = time.time()
    
    # Execute both queries concurrently using asyncio.gather()
    all_users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"\n⚡ Both queries completed concurrently in {total_time:.2f} seconds")
    print("=" * 80)
    
    # Display results
    print(f"\n📊 RESULTS SUMMARY:")
    print(f"Total users found: {len(all_users)}")
    print(f"Users older than 40: {len(older_users)}")
    
    print(f"\n👥 ALL USERS:")
    print("-" * 85)
    print(f"{'User ID':<40} {'Name':<20} {'Email':<25} {'Age':<5}")
    print("-" * 85)
    
    for user in all_users:
        user_id, first_name, last_name, email, role, age = user
        full_name = f"{first_name} {last_name}"
        print(f"{user_id:<40} {full_name:<20} {email:<25} {age:<5}")
    
    print(f"\n👴 USERS OLDER THAN 40:")
    print("-" * 85)
    print(f"{'User ID':<40} {'Name':<20} {'Email':<25} {'Age':<5}")
    print("-" * 85)
    
    for user in older_users:
        user_id, first_name, last_name, email, role, age = user
        full_name = f"{first_name} {last_name}"
        print(f"{user_id:<40} {full_name:<20} {email:<25} {age:<5}")
    
    # Performance comparison
    print(f"\n⚡ PERFORMANCE ANALYSIS:")
    print(f"If queries were run sequentially: ~0.25 seconds")
    print(f"Concurrent execution time: {total_time:.2f} seconds")
    improvement = ((0.25 - total_time) / 0.25 * 100) if total_time < 0.25 else 0
    print(f"Performance improvement: ~{improvement:.1f}%")


async def demo_sequential_vs_concurrent():
    """
    Demonstrate the difference between sequential and concurrent execution.
    """
    print("\n" + "=" * 80)
    print("📈 SEQUENTIAL vs CONCURRENT COMPARISON")
    print("=" * 80)
    
    # Sequential execution
    print("\n🐌 Running queries SEQUENTIALLY...")
    seq_start = time.time()
    
    all_users_seq = await async_fetch_users()
    older_users_seq = await async_fetch_older_users()
    
    seq_end = time.time()
    sequential_time = seq_end - seq_start
    
    print(f"Sequential execution completed in {sequential_time:.2f} seconds")
    
    # Concurrent execution
    print(f"\n🚀 Running queries CONCURRENTLY...")
    conc_start = time.time()
    
    all_users_conc, older_users_conc = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    
    conc_end = time.time()
    concurrent_time = conc_end - conc_start
    
    print(f"Concurrent execution completed in {concurrent_time:.2f} seconds")
    
    # Performance comparison
    improvement = ((sequential_time - concurrent_time) / sequential_time) * 100
    print(f"\n📊 Performance improvement: {improvement:.1f}%")
    print(f"Time saved: {sequential_time - concurrent_time:.2f} seconds")


def main():
    """
    Main function to run the concurrent database operations demo.
    """
    try:
        # Run the main concurrent fetch demonstration
        asyncio.run(fetch_concurrently())
        
        # Run the comparison demo
        print("\n" + "=" * 80)
        asyncio.run(demo_sequential_vs_concurrent())
        
        print(f"\n✅ Airbnb Database Demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")


if __name__ == "__main__":
    main()
