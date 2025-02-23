import sqlite3

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('chatbot.db')

# Create a cursor object
cursor = conn.cursor()

# Create users table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password_hash TEXT
    )
''')
print("Created 'users' table.")

# Create themes table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS themes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        theme_name TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
''')
print("Created 'themes' table.")

# Create chat_records table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        theme INTEGER,
        user_message TEXT,
        bot_reply TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(theme) REFERENCES themes(id)
    )
''')
print("Created 'chat_records' table.")

# Commit changes and close the connection
conn.commit()
cursor.close()
conn.close()
print("Database initialized.")