"""Reset database and vector store."""
import sys
from database import db
from vector_store import vector_store


def reset_database():
    """Clear all entries and reset vector store."""
    print("WARNING: This will delete ALL captured data!")

    # If running interactively, ask for confirmation
    if sys.stdin.isatty():
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Reset cancelled.")
            return

    print("\nResetting database...")
    count = db.clear_all_entries()
    print(f"✓ Cleared {count} entries from database")

    print("Resetting vector store...")
    vector_store.reset()
    print("✓ Vector store reset complete")

    print(f"\n✓ Successfully reset database ({count} entries deleted)")


if __name__ == "__main__":
    reset_database()
