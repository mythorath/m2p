#!/usr/bin/env python3
"""
Database initialization script for M2P Wallet Verification System
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, inspect
from server.models import Base, Player, VerificationLog
from server.config import DATABASE_URL

def init_database():
    """Initialize the database with all tables"""
    print("M2P Database Initialization")
    print("=" * 50)
    print(f"Database URL: {DATABASE_URL}")
    print()

    # Create engine
    engine = create_engine(DATABASE_URL, echo=True)

    # Check if tables already exist
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    if existing_tables:
        print(f"Found existing tables: {existing_tables}")
        response = input("Tables already exist. Drop and recreate? (yes/no): ")
        if response.lower() == 'yes':
            print("Dropping all tables...")
            Base.metadata.drop_all(engine)
            print("Tables dropped.")
        else:
            print("Keeping existing tables.")
            return

    # Create all tables
    print("\nCreating tables...")
    Base.metadata.create_all(engine)
    print("Tables created successfully!")

    # List created tables
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"\nCreated tables: {tables}")

    # Show table schemas
    for table_name in tables:
        print(f"\n{table_name} columns:")
        columns = inspector.get_columns(table_name)
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")

    print("\n" + "=" * 50)
    print("Database initialization complete!")


if __name__ == '__main__':
    try:
        init_database()
    except Exception as e:
        print(f"Error initializing database: {e}", file=sys.stderr)
        sys.exit(1)
