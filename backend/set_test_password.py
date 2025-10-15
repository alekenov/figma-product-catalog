#!/usr/bin/env python3
"""Set test password for user in shop_id=8"""
import bcrypt
import sqlite3

# Password to set
TEST_PASSWORD = "test1234"

# Hash the password
password_hash = bcrypt.hashpw(TEST_PASSWORD.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Connect to database
conn = sqlite3.connect('figma_catalog.db')
cursor = conn.cursor()

# Update first user in shop_id=8
cursor.execute("""
    UPDATE user
    SET password_hash = ?
    WHERE shop_id = 8
    AND id = (SELECT MIN(id) FROM user WHERE shop_id = 8)
""", (password_hash,))

conn.commit()

# Verify
cursor.execute("SELECT id, phone, name, role FROM user WHERE shop_id = 8 AND id = (SELECT MIN(id) FROM user WHERE shop_id = 8)")
user = cursor.fetchone()

conn.close()

print(f"✅ Password set to '{TEST_PASSWORD}' for user:")
print(f"   ID: {user[0]}")
print(f"   Phone: {user[1]}")
print(f"   Name: {user[2]}")
print(f"   Role: {user[3]}")
