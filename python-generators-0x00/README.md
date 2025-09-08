# Seed script and row-streaming generator

This folder contains `seed.py` which:
- creates database `ALX_prodev`
- creates table `user_data`
- inserts rows from `user_data.csv`
- provides a generator `stream_user_data(connection)` to stream rows one-by-one

## Usage (locally)
1. Ensure MySQL server is running.
2. Optionally set env vars:
   - MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD
3. Upload `user_data.csv` in this folder (or provide a path).
4. Run example runner `0-main.py` or call functions from Python.

Example generator usage:
```python
import seed
conn = seed.connect_to_prodev()
for row in seed.stream_user_data(conn):
    print(row)
conn.close()
