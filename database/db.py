"""Database management for Local Recall."""
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pathlib import Path
from sqlalchemy import create_engine, desc, or_
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import logging

from database.models import Base, DataEntry, Keybind, SystemState, Notification
from config import settings


logger = logging.getLogger(__name__)


class Database:
    """Database manager for Local Recall."""

    def __init__(self, db_path: str = None):
        """Initialize database."""
        self.db_path = db_path or settings.DATABASE_PATH

        # Ensure database directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        self.engine = create_engine(f"sqlite:///{self.db_path}")
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)
        self._init_db()

    def _init_db(self):
        """Initialize database tables."""
        Base.metadata.create_all(self.engine)

        # Initialize system state if not exists
        with self.get_session() as session:
            if not session.query(SystemState).first():
                state = SystemState(id=1, is_capturing=False)
                session.add(state)
                session.commit()

    @contextmanager
    def get_session(self) -> Session:
        """Get database session context manager."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            session.close()

    # Data Entry Methods
    def add_entry(self, content: str, source: str = None,
                  capture_method: str = "manual", tags: List[str] = None) -> DataEntry:
        """Add a new data entry."""
        with self.get_session() as session:
            entry = DataEntry(
                content=content,
                source=source,
                capture_method=capture_method,
                tags=",".join(tags) if tags else None,
                timestamp=datetime.now(timezone.utc)
            )
            session.add(entry)
            session.flush()
            session.refresh(entry)

            # Update total entries count
            state = session.query(SystemState).first()
            if state:
                state.total_entries = session.query(DataEntry).count()

            return entry

    def get_entry(self, entry_id: int) -> Optional[DataEntry]:
        """Get entry by ID."""
        with self.get_session() as session:
            return session.query(DataEntry).filter(DataEntry.id == entry_id).first()

    def get_entries(self, filters: Dict[str, Any] = None, limit: int = 100) -> List[DataEntry]:
        """Get entries with optional filters."""
        with self.get_session() as session:
            query = session.query(DataEntry)

            if filters:
                if "id" in filters:
                    query = query.filter(DataEntry.id == filters["id"])
                if "tag" in filters:
                    query = query.filter(DataEntry.tags.like(f"%{filters['tag']}%"))
                if "time" in filters:
                    query = query.filter(DataEntry.timestamp >= filters["time"])
                if "source" in filters:
                    query = query.filter(DataEntry.source == filters["source"])

            return query.order_by(desc(DataEntry.timestamp)).limit(limit).all()

    def get_unembedded_entries(self, limit: int = 100) -> List[DataEntry]:
        """Get entries that haven't been embedded yet."""
        with self.get_session() as session:
            return session.query(DataEntry)\
                .filter(DataEntry.is_embedded == False)\
                .limit(limit).all()

    def mark_embedded(self, entry_id: int, embedding_id: int):
        """Mark an entry as embedded."""
        with self.get_session() as session:
            entry = session.query(DataEntry).filter(DataEntry.id == entry_id).first()
            if entry:
                entry.is_embedded = True
                entry.embedding_id = embedding_id

                # Update total embedded count
                state = session.query(SystemState).first()
                if state:
                    state.total_embedded = session.query(DataEntry)\
                        .filter(DataEntry.is_embedded == True).count()

    def delete_entry(self, entry_id: int) -> bool:
        """Delete an entry."""
        with self.get_session() as session:
            entry = session.query(DataEntry).filter(DataEntry.id == entry_id).first()
            if entry:
                session.delete(entry)

                # Update total entries count
                state = session.query(SystemState).first()
                if state:
                    state.total_entries = session.query(DataEntry).count()
                    state.total_embedded = session.query(DataEntry)\
                        .filter(DataEntry.is_embedded == True).count()
                return True
            return False

    def clear_all_entries(self) -> int:
        """Clear all data entries from the database."""
        with self.get_session() as session:
            count = session.query(DataEntry).count()
            session.query(DataEntry).delete()

            # Reset system state counts
            state = session.query(SystemState).first()
            if state:
                state.total_entries = 0
                state.total_embedded = 0

            logger.info(f"Cleared {count} entries from database")
            return count

    # Keybind Methods
    def add_keybind(self, action: str, key_sequence: str) -> Keybind:
        """Add a keybind."""
        with self.get_session() as session:
            keybind = Keybind(action=action, key_sequence=key_sequence)
            session.add(keybind)
            session.flush()
            session.refresh(keybind)
            return keybind

    def get_keybinds(self) -> List[Keybind]:
        """Get all active keybinds."""
        with self.get_session() as session:
            return session.query(Keybind).filter(Keybind.is_active == True).all()

    def clear_keybinds(self):
        """Clear all keybinds."""
        with self.get_session() as session:
            session.query(Keybind).delete()
            logger.info("Cleared all keybinds")

    # System State Methods
    def get_system_state(self) -> SystemState:
        """Get system state."""
        with self.get_session() as session:
            return session.query(SystemState).first()

    def set_capturing(self, is_capturing: bool):
        """Set capturing state."""
        with self.get_session() as session:
            state = session.query(SystemState).first()
            if state:
                state.is_capturing = is_capturing
                if is_capturing:
                    state.last_started = datetime.now(timezone.utc)
                else:
                    state.last_stopped = datetime.now(timezone.utc)

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        with self.get_session() as session:
            state = session.query(SystemState).first()
            total = session.query(DataEntry).count()
            embedded = session.query(DataEntry).filter(DataEntry.is_embedded == True).count()

            return {
                "total_entries": total,
                "embedded_entries": embedded,
                "pending_embeddings": total - embedded,
                "is_capturing": state.is_capturing if state else False,
                "last_started": state.last_started.isoformat() if state and state.last_started else None,
                "last_stopped": state.last_stopped.isoformat() if state and state.last_stopped else None
            }

    # Notification Methods (persistent across processes)
    def add_notification(self, type: str, title: str, message: str, status: str = "info") -> Notification:
        """Add a notification to the database."""
        print(f"    [DB DEBUG] add_notification called: type={type}, title={title}, status={status}")
        with self.get_session() as session:
            notification = Notification(
                type=type,
                title=title,
                message=message,
                status=status,
                timestamp=datetime.now(timezone.utc)
            )
            session.add(notification)
            session.flush()
            session.refresh(notification)
            print(f"    [DB DEBUG] Notification created with ID: {notification.id}")
            logger.debug(f"Added notification: {title}")
            return notification

    def get_notifications(self, since_id: int = None, unread_only: bool = False, limit: int = 10) -> List[Notification]:
        """Get notifications with optional filters."""
        with self.get_session() as session:
            query = session.query(Notification)

            if since_id:
                query = query.filter(Notification.id > since_id)

            if unread_only:
                query = query.filter(Notification.is_read == False)

            results = query.order_by(desc(Notification.id)).limit(limit).all()
            print(f"    [DB DEBUG] get_notifications: since_id={since_id}, unread_only={unread_only}, limit={limit} -> {len(results)} results")
            for n in results:
                print(f"        [DB DEBUG] Notification {n.id}: {n.title} ({n.status}, read={n.is_read})")
            return results

    def mark_notification_read(self, notification_id: int) -> bool:
        """Mark a notification as read."""
        with self.get_session() as session:
            notification = session.query(Notification).filter(Notification.id == notification_id).first()
            if notification:
                notification.is_read = True
                return True
            return False

    def mark_all_notifications_read(self) -> int:
        """Mark all notifications as read."""
        with self.get_session() as session:
            count = session.query(Notification).filter(Notification.is_read == False).update({"is_read": True})
            return count

    def clear_notifications(self):
        """Clear all notifications."""
        with self.get_session() as session:
            session.query(Notification).delete()
            logger.info("Cleared all notifications")


# Global database instance
db = Database()
