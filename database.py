import sqlite3

def setupSQL():
    """Initializes the SQLite database and creates the users table."""
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    try:
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                tgID TEXT PRIMARY KEY,
                name TEXT,
                phone TEXT,
                city TEXT
            )
        ''')
        conn.commit()
    finally:
        cur.close()
        conn.close()

def saveUserData(tgID, name, phoneNum, city):
    """Saves or updates user profile information in the database."""
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    try:
        cur.execute(
            'INSERT OR REPLACE INTO users (tgID, name, phone, city) VALUES (?, ?, ?, ?)',
            (tgID, name, phoneNum, city)
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()

def getUserData(tgID):
    """Retrieves user profile from the database by Telegram ID."""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT tgID, name, phone, city FROM users WHERE tgID = ?', (tgID,))
        row = cursor.fetchone()
        return {"tgID": row[0], "name": row[1], "phone": row[2], "city": row[3]} if row else None
    finally:
        cursor.close()
        conn.close()
