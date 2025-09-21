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
                age INTEGER DEFAULT 25,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Check if users table is empty and insert sample data
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        count = await cursor.fetchone()
        await cursor.close()
        
        if count[0] == 0:
            # Sample users data with ages
            sample_users = [
                (str(uuid.uuid4()), 'Alice', 'Johnson', 'alice@example.com', 'hash123', '+1234567890', 'guest', 28),
                (str(uuid.uuid4()), 'Bob', 'Smith', 'bob@example.com', 'hash456', '+0987654321', 'host', 45),
                (str(uuid.uuid4()), 'Charlie', 'Brown', 'charlie@example.com', 'hash789', '+1122334455', 'guest', 22),
                (str(uuid.uuid4()), 'Diana', 'Prince', 'diana@example.com', 'hash101', '+5566778899', 'host', 42),
                (str(uuid.uuid4()), 'Eve', 'Wilson', 'eve@example.com', 'hash202', '+2233445566', 'guest', 19),
                (str(uuid.uuid4()), 'Frank', 'Miller', 'frank@example.com', 'hash303', '+3344556677', 'host', 48),
                (str(uuid.uuid4()), 'Grace', 'Lee', 'grace@example.com', 'hash404', '+4455667788', 'admin', 35),
                (str(uuid.uuid4()), 'Henry', 'Davis', 'henry@example.com', 'hash505', '+5566778800', 'host', 31),
                (str(uuid.uuid4()), 'Iris', 'Chen', 'iris@example.com', 'hash606', '+6677889900', 'host', 43),
                (str(uuid.uuid4()), 'Jack', 'Williams', 'jack@example.com', 'hash707', '+7788990011', 'guest', 38),
                (str(uuid.uuid4()), 'Kate', 'Brown', 'kate@example.com', 'hash808', '+8899001122', 'host', 47),
                (str(uuid.uuid4()), 'Liam', 'Johnson', 'liam@example.com', 'hash909', '+9900112233', 'guest', 25),
                (str(uuid.uuid4()), 'Maya', 'Patel', 'maya@example.com', 'hash111', '+1122330044', 'host', 51),
                (str(uuid.uuid4()), 'Noah', 'Garcia', 'noah@example.com', 'hash222', '+2233441155', 'admin', 44),
                (str(uuid.uuid4()), 'Olivia', 'Martinez', 'olivia@example.com', 'hash333', '+3344552266', 'guest', 41)
            ]
            
            await db.executemany('''
                INSERT INTO users (user_id, first_name, last_name, email, password_hash, phone_number, role, age) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', sample_users)
            
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
        
        cursor = await db.execute("SELECT user_id, first_name, last_name, email, role, age FROM users")
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
    print("=" * 85)
    
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
    print("\n" + "=" * 85)
    print("📈 SEQUENTIAL vs CONCURRENT COMPARISON")
    print("=" * 85)
    
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
        print("\n" + "=" * 85)
        asyncio.run(demo_sequential_vs_concurrent())
        
        print(f"\n✅ Airbnb Database Demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")


if __name__ == "__main__":
    main()
