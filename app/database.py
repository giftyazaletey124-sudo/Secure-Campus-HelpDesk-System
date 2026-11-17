
import os
import sqlite3
from flask import current_app

def get_database_path():
    database_path = current_app.config["DATABASE"]

    if not os.path.isabs(database_path):
        project_folder = os.path.dirname(current_app.root_path)
        database_path = os.path.join(project_folder, database_path)

    os.makedirs(os.path.dirname(database_path), exist_ok=True)

    return database_path

def get_db_connection():
    connection = sqlite3.connect(get_database_path())
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection

def create_tables():
    connection = get_db_connection()

    try:
        # Create users table if it does not exist
        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK (
                    role IN ('student', 'staff', 'technician', 'admin')
                )
            )
        """)

        # Create tickets table if it does not exist
        connection.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending' CHECK (
                    status IN (
                        'Pending',
                        'In Progress',
                        'Resolved',
                        'Closed'
                    )
                ),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                assigned_to INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (assigned_to) REFERENCES users(user_id)
            )
        """)

        # Check existing users table columns
        columns = connection.execute(
            "PRAGMA table_info(users)"
        ).fetchall()

        column_names = [column["name"] for column in columns]

        # Add OTP secret column if missing
        if "otp_secret" not in column_names:
            connection.execute("""
                ALTER TABLE users
                ADD COLUMN otp_secret TEXT
            """)

        # Add OTP enabled column if missing
        if "otp_enabled" not in column_names:
            connection.execute("""
                ALTER TABLE users
                ADD COLUMN otp_enabled INTEGER NOT NULL DEFAULT 0
            """)

        connection.commit()

    finally:
        connection.close()