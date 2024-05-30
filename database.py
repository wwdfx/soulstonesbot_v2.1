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