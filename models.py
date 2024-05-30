from database import cur, conn, reconnect_db

@reconnect_db
async def get_user_role(user_id):
    cur.execute('SELECT role FROM users WHERE user_id = %s', (user_id,))
    result = cur.fetchone()
    return result['role'] if result else 'user'

@reconnect_db
async def set_balance(user_id, amount):
    cur.execute('INSERT INTO balances (user_id, balance) VALUES (%s, %s) ON CONFLICT (user_id) DO UPDATE SET balance = %s', (user_id, amount, amount))
    conn.commit()
    return amount

@reconnect_db
async def get_balance(user_id):
    cur.execute('SELECT balance FROM balances WHERE user_id = %s', (user_id,))
    result = cur.fetchone()
    return result['balance'] if result else 0

@reconnect_db
async def update_balance(user_id, amount):
    current_balance = await get_balance(user_id)
    new_balance = current_balance + amount
    cur.execute('INSERT INTO balances (user_id, balance) VALUES (%s, %s) ON CONFLICT (user_id) DO UPDATE SET balance = %s', (user_id, new_balance, new_balance))
    conn.commit()
    return new_balance

@reconnect_db
async def reduce_balance(user_id, amount):
    current_balance = await get_balance(user_id)
    if current_balance < amount:
        return None  # Not enough balance
    new_balance = current_balance - amount
    cur.execute('INSERT INTO balances (user_id, balance) VALUES (%s, %s) ON CONFLICT (user_id) DO UPDATE SET balance = %s', (user_id, new_balance, new_balance))
    conn.commit()
    return new_balance

@reconnect_db
async def get_user_symbols(user_id):
    cur.execute('SELECT symbols_count FROM user_symbols WHERE user_id = %s', (user_id,))
    result = cur.fetchone()
    return result['symbols_count'] if result else 0

@reconnect_db
async def update_user_symbols(user_id, symbols_count):
    cur.execute('INSERT INTO user_symbols (user_id, symbols_count) VALUES (%s, %s) ON CONFLICT (user_id) DO UPDATE SET symbols_count = user_symbols.symbols_count + EXCLUDED.symbols_count', (user_id, symbols_count))
    conn.commit()

@reconnect_db
async def get_user_messages(user_id, chat_id):
    cur.execute('SELECT message_count FROM user_messages WHERE user_id = %s AND chat_id = %s', (user_id, chat_id))
    result = cur.fetchone()
    return result['message_count'] if result else 0

@reconnect_db
async def get_user_rank(user_id):
    symbols_count = await get_user_symbols(user_id)
    if symbols_count < 5000:
        return "👦🏻 Смертный"
    elif symbols_count < 20000:
        return "😎 Новичок"
    elif symbols_count < 50000:
        return "😼 Новоприбывший Охотник"
    elif symbols_count < 100000:
        return "🧐 Опытный Охотник"
    elif symbols_count < 250000:
        return "🫡 Лидер миссий Института"
    elif symbols_count < 400000:
        return "🧑🏻‍✈️ Лидер Института"
    elif symbols_count < 750000:
        return "🧑🏻‍⚖️ Кандидат в Инквизиторы"
    else:
        return "🤴🏻 Инквизитор"