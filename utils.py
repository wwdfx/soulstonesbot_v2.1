from database import cur, conn, reconnect_db
import random
from datetime import datetime, timedelta
from telegram.ext import ContextTypes

from models import update_balance

# Ranking system thresholds
RANKS = [
    ("👦🏻 Смертный", 0, 5000, 5),
    ("😎 Новичок", 5000, 20000, 15),
    ("😼 Новоприбывший Охотник", 20000, 50000, 30),
    ("🧐 Опытный охотник", 50000, 100000, 50),
    ("🫡 Лидер миссий Института", 100000, 250000, 85),
    ("🧑🏻‍✈️ Лидер Института", 250000, 400000, 135),
    ("🧑🏻‍⚖️ Кандидат в Инквизиторы", 400000, 750000, 200),
    ("🤴🏻 Инквизитор", 750000, float('inf'), 300)
]

@reconnect_db
async def generate_missions():
    missions = []
    cur.execute('SELECT * FROM missions')
    mission_data = cur.fetchall()
    for mission in mission_data:
        if random.randint(1, 100) <= mission['appearing_rate']:
            missions.append(mission)
        if len(missions) >= 5:
            break
    return missions

@reconnect_db
async def can_request_reading(user_id):
    cur.execute('SELECT last_request FROM last_reading WHERE user_id = %s', (user_id,))
    result = cur.fetchone()
    if result:
        last_request_time = result['last_request']
        if datetime.now() - last_request_time < timedelta(days=1):
            return False
    cur.execute('INSERT INTO last_reading (user_id, last_request) VALUES (%s, %s) ON CONFLICT (user_id) DO UPDATE SET last_request = %s', (user_id, datetime.now(), datetime.now()))
    conn.commit()
    return True

@reconnect_db
async def check_missions(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    cur.execute('SELECT user_id, mission_id FROM user_missions WHERE completed = FALSE AND end_time <= %s', (now,))
    completed_missions = cur.fetchall()

    for mission in completed_missions:
        user_id, mission_id = mission['user_id'], mission['mission_id']
        cur.execute('SELECT reward FROM missions WHERE id = %s', (mission_id,))
        reward = cur.fetchone()['reward']
        await update_balance(user_id, reward)
        cur.execute('UPDATE user_missions SET completed = TRUE WHERE user_id = %s AND mission_id = %s', (user_id, mission_id))
        await context.bot.send_message(chat_id=user_id, text=f"✅ Ваша миссия завершена! ✅ Вы получили {reward} 💎 Камней душ.")
    conn.commit()

@reconnect_db
async def get_user_rank(user_id):
    symbols_count = await get_user_symbols(user_id)
    for rank, lower_bound, upper_bound, _ in RANKS:
        if lower_bound <= symbols_count < upper_bound:
            return rank
    return "Unknown"

@reconnect_db
async def get_user_symbols(user_id):
    cur.execute('SELECT symbols_count FROM user_symbols WHERE user_id = %s', (user_id,))
    result = cur.fetchone()
    return result['symbols_count'] if result else 0