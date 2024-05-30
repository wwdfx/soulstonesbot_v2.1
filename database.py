import psycopg2
from psycopg2.extras import DictCursor

# Database connection details
DB_DETAILS = {
    "dbname": "koyebdb",
    "user": "koyeb-adm",
    "password": "WCAFr1R0muaZ",
    "host": "ep-shy-pine-a2e1ouuw.eu-central-1.pg.koyeb.app",
    "port": 5432
}

# Connect to PostgreSQL Database
def connect_db():
    conn = psycopg2.connect(**DB_DETAILS)
    conn.autocommit = True
    return conn

conn = connect_db()
cur = conn.cursor(cursor_factory=DictCursor)

# Function to handle reconnection
def reconnect_db(func):
    async def wrapper(*args, **kwargs):
        global conn, cur
        try:
            return await func(*args, **kwargs)
        except (psycopg2.OperationalError, psycopg2.InterfaceError):
            conn.close()
            conn = connect_db()
            cur = conn.cursor(cursor_factory=DictCursor)
            return await func(*args, **kwargs)
    return wrapper

# Ensure message_counts table exists
cur.execute('''
    CREATE TABLE IF NOT EXISTS message_counts (
        user_id BIGINT PRIMARY KEY,
        message_count INTEGER NOT NULL DEFAULT 0
    )
''')

@reconnect_db
async def get_message_count(user_id):
    cur.execute('SELECT message_count FROM message_counts WHERE user_id = %s', (user_id,))
    result = cur.fetchone()
    return result['message_count'] if result else 0

@reconnect_db
async def increment_message_count(user_id, count=1):
    current_count = await get_message_count(user_id)
    new_count = current_count + count
    cur.execute('INSERT INTO message_counts (user_id, message_count) VALUES (%s, %s) ON CONFLICT (user_id) DO UPDATE SET message_count = %s', (user_id, new_count, new_count))
    conn.commit()
    return new_count

@reconnect_db
async def reset_message_count(user_id):
    cur.execute('UPDATE message_counts SET message_count = 0 WHERE user_id = %s', (user_id,))
    conn.commit()

# Create tables if they do not exist
cur.execute('''
    CREATE TABLE IF NOT EXISTS balances (
        user_id BIGINT PRIMARY KEY,
        balance INTEGER NOT NULL DEFAULT 0
    )
''')

cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id BIGINT PRIMARY KEY,
        role TEXT NOT NULL DEFAULT 'user'
    )
''')

cur.execute('''
    CREATE TABLE IF NOT EXISTS last_reading (
        user_id BIGINT PRIMARY KEY,
        last_request TIMESTAMP
    )
''')

cur.execute('''
    CREATE TABLE IF NOT EXISTS checkin_streak (
        user_id BIGINT PRIMARY KEY,
        streak INTEGER NOT NULL DEFAULT 0,
        last_checkin TIMESTAMP
    )
''')

cur.execute('''
    CREATE TABLE IF NOT EXISTS last_game (
        user_id BIGINT PRIMARY KEY,
        last_play TIMESTAMP
    )
''')

cur.execute('''
    CREATE TABLE IF NOT EXISTS missions (
        id SERIAL PRIMARY KEY,
        name TEXT,
        rarity TEXT,
        appearing_rate INTEGER,
        length INTEGER,
        reward INTEGER
    )
''')

cur.execute('''
    CREATE TABLE IF NOT EXISTS user_missions (
        user_id BIGINT,
        mission_id INTEGER,
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        completed BOOLEAN DEFAULT FALSE,
        PRIMARY KEY (user_id, mission_id, start_time)
    )
''')

cur.execute('''
    CREATE TABLE IF NOT EXISTS mission_attempts (
        user_id BIGINT,
        date DATE,
        attempts INTEGER DEFAULT 0,
        PRIMARY KEY (user_id, date)
    )
''')

cur.execute('''
    CREATE TABLE IF NOT EXISTS user_symbols (
        user_id BIGINT PRIMARY KEY,
        symbols_count INTEGER NOT NULL DEFAULT 0
    )
''')

