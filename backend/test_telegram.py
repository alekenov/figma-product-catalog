#!/usr/bin/env python3
"""Quick test for telegram endpoints"""
import sys
sys.path.insert(0, "/Users/alekenov/figma-product-catalog/backend")

from sqlmodel import Session, select
from database import engine
from models.users import Client

telegram_user_id = "123456789"
shop_id = 8

# Test database query
with Session(engine) as session:
    try:
        statement = select(Client).where(
            Client.telegram_user_id == telegram_user_id,
            Client.shop_id == shop_id
        )
        client = session.exec(statement).first()
        print(f"Query executed successfully")
        print(f"Result: {client}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
