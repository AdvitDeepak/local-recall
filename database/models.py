"""Database models for Local Recall."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class DataEntry(Base):
    """Model for stored text data."""

    __tablename__ = "data_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text, nullable=False)
    source = Column(String(255), nullable=True)  # Application source
    capture_method = Column(String(50), nullable=False)  # 'selected', 'screenshot', 'upload'
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    tags = Column(String(500), nullable=True)  # Comma-separated tags
    embedding_id = Column(Integer, nullable=True)  # Reference to FAISS index
    is_embedded = Column(Boolean, default=False)

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "source": self.source,
            "capture_method": self.capture_method,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "tags": self.tags.split(",") if self.tags else [],
            "is_embedded": self.is_embedded
        }


class Keybind(Base):
    """Model for user-defined keybinds."""

    __tablename__ = "keybinds"

    id = Column(Integer, primary_key=True, autoincrement=True)
    action = Column(String(50), nullable=False)  # 'capture_selected', 'capture_screenshot'
    key_sequence = Column(String(100), nullable=False)  # e.g., '<ctrl>+<alt>+r'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "action": self.action,
            "key_sequence": self.key_sequence,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class SystemState(Base):
    """Model for system state tracking."""

    __tablename__ = "system_state"

    id = Column(Integer, primary_key=True)
    is_capturing = Column(Boolean, default=False)
    last_started = Column(DateTime, nullable=True)
    last_stopped = Column(DateTime, nullable=True)
    total_entries = Column(Integer, default=0)
    total_embedded = Column(Integer, default=0)
