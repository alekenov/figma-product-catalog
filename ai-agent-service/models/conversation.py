"""SQLAlchemy models for conversation history."""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Conversation(Base):
    """Conversation history model for SQLite."""

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False, index=True)
    channel = Column(String(50), nullable=False)  # telegram, whatsapp, web
    messages = Column(JSON, nullable=False)  # List of message dicts
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Conversation user_id={self.user_id} channel={self.channel} messages={len(self.messages)}>"
