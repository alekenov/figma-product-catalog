"""
Manually run migration to expand device_token column
"""
from database import create_db_and_tables

print("Running migration...")
create_db_and_tables()
print("Migration complete!")
