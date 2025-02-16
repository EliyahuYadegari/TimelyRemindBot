import sqlite3
import os

if not os.path.exists('tasks'):
    os.makedirs('tasks')

def create_db(user_id):
    db_name = f'tasks/tasks_{user_id}.db'
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''  
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            time TEXT,
            name TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_task_to_db(user_id, date, time, name):
    db_name = f'tasks/tasks_{user_id}.db' 
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''  
        INSERT INTO tasks (date, time, name)
        VALUES (?, ?, ?)
    ''', (date, time, name))
    conn.commit()
    conn.close()

def get_all_tasks(user_id):
    db_name = f'tasks/tasks_{user_id}.db'
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('SELECT date, time, name FROM tasks ORDER BY date, time')
    tasks = c.fetchall()
    conn.close()
    return tasks

def delete_task(user_id, date, time, name):
    db_name = f'tasks/tasks_{user_id}.db'
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''DELETE FROM tasks WHERE date = ? AND time = ? AND name = ?''', (date, time, name))
    conn.commit()
    conn.close()
