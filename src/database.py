"""
This module initializes the SQLite database for the bot, creating all required tables:
- users
- tasks
- goals
- reminders
- countdowns
- quotes
- weekly_schedule

Each table is created with all fields and constraints as per the architecture specification.
"""

import sqlite3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
from datetime import datetime

# Database file name
DATABASE_FILE = os.getenv('DB_PATH', 'data/bot.db')

def get_db_connection():
    """
    Returns a connection object to the SQLite database.
    Enables foreign key support and sets a row factory for dict-like access.
    """
    # Ensure the directory exists
    os.makedirs(os.path.dirname(DATABASE_FILE), exist_ok=True)

    conn = sqlite3.connect(
        DATABASE_FILE,
        detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
    )
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """
    Initializes the database.
    Creates tables if they do not exist:
      - users
      - tasks
      - goals
      - reminders
      - countdowns
      - quotes
      - weekly_schedule
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create table: users
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            language TEXT NOT NULL DEFAULT 'en',
            timezone TEXT NOT NULL,
            summary_schedule TEXT NOT NULL DEFAULT 'disabled',
            summary_time TEXT,
            random_checkin_max INTEGER NOT NULL DEFAULT 0
        );
    ''')
    
    # Create table: tasks
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            due_date DATETIME,
            status TEXT NOT NULL CHECK (status IN ('pending', 'done')) DEFAULT 'pending',
            created_at DATETIME NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
        );
    ''')
    
    # Create table: goals
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            frequency TEXT NOT NULL CHECK (frequency IN ('daily', 'weekly', 'monthly', 'seasonal', 'yearly')),
            next_check_date DATETIME,
            status TEXT NOT NULL CHECK (status IN ('in_progress', 'done')) DEFAULT 'in_progress',
            created_at DATETIME NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
        );
    ''')
    
    # Create table: reminders
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            next_trigger_time DATETIME NOT NULL,
            repeat_type TEXT NOT NULL,
            repeat_value INTEGER,
            created_at DATETIME NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
        );
    ''')
    
    # Create table: countdowns
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS countdowns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            event_datetime DATETIME NOT NULL,
            notify_schedule TEXT NOT NULL,
            created_at DATETIME NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
        );
    ''')
    
    # Create table: quotes
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            quote_text TEXT NOT NULL,
            created_at DATETIME NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
        );
    ''')
    
    # Create table: weekly_schedule
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS weekly_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            day_of_week TEXT NOT NULL,  -- e.g., "Monday", "Tuesday", etc.
            time_of_day TEXT NOT NULL,  -- stored as "HH:MM"
            created_at DATETIME NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
        );
    ''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    # When running this file directly, initialize the database.
    init_db()
    print("Database initialized successfully at", DATABASE_FILE)
