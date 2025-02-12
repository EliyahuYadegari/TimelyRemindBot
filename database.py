import sqlite3

# Connect to SQLite database
conn = sqlite3.connect("deadlines.db", check_same_thread=False)
cursor = conn.cursor()

# Create table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS deadlines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    date TEXT,
    time TEXT,
    description TEXT,
    category TEXT
)
""")
conn.commit()

def add_deadline(user_id, date, time, description, category):
    """Insert a new deadline into the database."""
    cursor.execute("INSERT INTO deadlines (user_id, date, time, description, category) VALUES (?, ?, ?, ?, ?)",
                   (user_id, date, time, description, category))
    conn.commit()

def get_deadlines(user_id, category=None):
    """Retrieve deadlines for a user, optionally filtering by category."""
    if category:
        cursor.execute("SELECT date, time, description FROM deadlines WHERE user_id = ? AND category = ?", 
                       (user_id, category))
    else:
        cursor.execute("SELECT date, time, description FROM deadlines WHERE user_id = ?", (user_id,))
    
    return cursor.fetchall()
