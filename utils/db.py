import os
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3
from dotenv import load_dotenv

# 1. FORCE LOAD .ENV IMMEDIATELY
load_dotenv()

# 2. NOW GET THE KEY
DATABASE_URL = os.getenv("DATABASE_URL")
USE_SQLITE = False

# Debugging Check
if not DATABASE_URL:
    print("DATABASE_URL is missing! Using local SQLite database (dev_db.sqlite).")
    USE_SQLITE = True
else:
    print("Database URL found.")
    USE_SQLITE = False

def get_db_connection():
    global USE_SQLITE
    if USE_SQLITE:
        conn = sqlite3.connect("dev_db.sqlite")
        conn.row_factory = sqlite3.Row
        return conn
    
    try:
        conn = psycopg2.connect(DATABASE_URL, connect_timeout=5)
        return conn
    except Exception as e:
        print(f"PostgreSQL Connection Error: {e}. Falling back to SQLite.")
        USE_SQLITE = True
        conn = sqlite3.connect("dev_db.sqlite")
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    """
    Initializes the SaaS database schema.
    Supports both PostgreSQL and SQLite.
    """
    conn = get_db_connection()
    if not conn: return
    
    cur = conn.cursor()
    
    if USE_SQLITE:
        # SQLite Syntax
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                username TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                credits INTEGER DEFAULT 5,
                plan_tier TEXT DEFAULT 'free',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS audit_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id),
                url TEXT NOT NULL,
                score INTEGER,
                report_data TEXT, -- SQLite stores JSON as TEXT
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
    else:
        # PostgreSQL Syntax
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                username TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                credits INTEGER DEFAULT 5,
                plan_tier TEXT DEFAULT 'free',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS audit_reports (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                url TEXT NOT NULL,
                score INTEGER,
                report_data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
    
    conn.commit()
    cur.close()
    conn.close()
    print(f"{'SQLite' if USE_SQLITE else 'PostgreSQL'} Database Infrastructure Initialized")

# --- USER MANAGEMENT FUNCTIONS ---

def get_user_by_email(email):
    """Fetch a user's full profile by email."""
    conn = get_db_connection()
    if not conn: return None
    
    if USE_SQLITE:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cur.fetchone()
        user = dict(row) if row else None
    else:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
    
    conn.close()
    return user

def create_user(email, username, hashed_pw):
    """Registers a new user in the SaaS system."""
    conn = get_db_connection()
    if not conn: return False
    cur = conn.cursor()
    try:
        placeholder = "?" if USE_SQLITE else "%s"
        cur.execute(
            f"INSERT INTO users (email, username, password_hash) VALUES ({placeholder}, {placeholder}, {placeholder})",
            (email, username, hashed_pw)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Signup Error: {e}")
        return False
    finally:
        conn.close()

# --- CREDIT SYSTEM FUNCTIONS ---

def deduct_credit(user_id):
    """
    Deducts 1 credit from the user's balance.
    Returns True if successful, False if insufficient credits.
    """
    conn = get_db_connection()
    if not conn: return False
    cur = conn.cursor()
    placeholder = "?" if USE_SQLITE else "%s"
    cur.execute(f"UPDATE users SET credits = credits - 1 WHERE id = {placeholder} AND credits > 0", (user_id,))
    success = cur.rowcount > 0
    conn.commit()
    conn.close()
    return success

def add_credits_to_user(user_id, amount):
    """Used by Stripe Webhooks to add credits after payment."""
    conn = get_db_connection()
    if not conn: return False
    cur = conn.cursor()
    placeholder = "?" if USE_SQLITE else "%s"
    cur.execute(f"UPDATE users SET credits = credits + {placeholder} WHERE id = {placeholder}", (amount, user_id))
    conn.commit()
    conn.close()
    return True