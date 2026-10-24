"""
Database Manager (PostgreSQL/Supabase)
Saves audits and retrieves history.
"""
import os
import psycopg2
import sqlite3
import json
from datetime import datetime

USE_SQLITE = False

def get_db_connection():
    global USE_SQLITE
    url = os.getenv("DATABASE_URL")
    
    if not url:
        print("DATABASE_URL is missing! Using local SQLite database (dev_db.sqlite).")
        USE_SQLITE = True
    else:
        print("Database URL found.")
        USE_SQLITE = False

    if USE_SQLITE:
        conn = sqlite3.connect("seo_audits.sqlite")
        return conn

    try:
        return psycopg2.connect(url, connect_timeout=5)
    except Exception as e:
        print(f"DB Connection Error: {e}. Falling back to SQLite.")
        USE_SQLITE = True
        conn = sqlite3.connect("seo_audits.sqlite")
        return conn

def init_db():
    """Creates the necessary table if it doesn't exist."""
    conn = get_db_connection()
    if not conn: return
    
    try:
        cur = conn.cursor()
        if USE_SQLITE:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS seo_audits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    score INTEGER,
                    meta_data TEXT, -- SQLite stores JSON as TEXT
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        else:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS seo_audits (
                    id SERIAL PRIMARY KEY,
                    url TEXT NOT NULL,
                    score INTEGER,
                    meta_data JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        conn.commit()
        cur.close()
        conn.close()
        print(f"Audit Database Verified ({'SQLite' if USE_SQLITE else 'PostgreSQL'})")
    except Exception as e:
        print(f"DB Init Error: {e}")

def save_audit_to_db(url, score, full_data):
    """Saves a JSON report to Database."""
    conn = get_db_connection()
    if not conn: return
    
    try:
        cur = conn.cursor()
        # Convert dict to JSON string
        json_data = json.dumps(full_data)
        
        placeholder = "?" if USE_SQLITE else "%s"
        cur.execute(
            f"INSERT INTO seo_audits (url, score, meta_data) VALUES ({placeholder}, {placeholder}, {placeholder})",
            (url, score, json_data)
        )
        conn.commit()
        cur.close()
        conn.close()
        print(f"   Saved audit for {url} to Database.")
    except Exception as e:
        print(f"   Save Error: {e}")