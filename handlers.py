from asyncio.log import logger
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
import random
import asyncio
from database import *
from models import get_balance, get_user_messages, get_user_role, get_user_symbols, reduce_balance, set_balance, update_balance
from utils import can_request_reading, generate_missions, get_user_rank, reconnect_db, RANKS
from datetime import datetime, timedelta

questions = [
    {
        "question": "Как зовут ангела, создавшего Сумеречных охотников?",
        "answers": ["Разиэль", "Ангел Разиель"]
    },
    {
        "question": "Как называется оружие, используемое Сумеречными Охотниками?",
        "answers": ["Клинки Серафима", "Клинки Ангела"]
    },
    {
        "question": "Как зовут главного героя сериала 'Орудия смерти?'",
        "answers": ["Клэри Фрэй", "Кларисса Фэйрчайлд", "Клэри", "Кларисса"]
    },
    {
        "question": "Кто является лидером Нью-Йоркского института в начале «Орудий смерти»?",
        "answers": ["Мариз Лайтвуд", "Мариз"]
    },
    {
        "question": "Как называется руна, дающая Сумеречным охотникам возможность исцеляться?",
        "answers": ["Иратце"]
    },
    {
        "question": "Кто биологический отец Джейса Эрондейла?",
        "answers": ["Стивен Эрондейл", "Стивен"]
    },
    {
        "question": "Как зовут Сумеречного Охотника, который также является оборотнем?",
        "answers": ["Люк Гэрроуей", "Люк"]
    },
    {
        "question": "Как зовут Верховного Мага Бруклина?",
        "answers": ["Магнус Бейн", "Магнус", "Магнус Бэйн"]
    },
    {
        "question": "Как Сумеречные Охотники называют обычных людей?",
        "answers": ["Смертные", "Мундэйны", "Обычные"]
    },
    {
        "question": "Как еще называют Меч Смерти?",
        "answers": ["Меллартах"]
    },
    {
        "question": "Как зовут парабатая Алека Лайтвуда?",
        "answers": ["Джейс Эрондейл","Джейс", "Блондинчик"]
    },
    {
        "question": "Как называется первая книга из серии 'Орудия смерти'?",
        "answers": ["Город костей", "Город Костей"]
    },
    {
        "question": "Как зовут лучшего друга Клэри, ставшего вампиром?",
        "answers": ["Саймон Льюис", "Саймон"]
    },
    {
        "question": "Как называется болезнь, поражающая колдунов и заставляющая их быстро стареть?",
        "answers": ["Демоническая оспа", "Оспа"]
    },
    {
        "question": "Как называется место, куда Сумеречные охотники ходят учиться и тренироваться?",
        "answers": ["Институт"]
    },
    {
        "question": "Кто является Консулом Конклава во время событий «Адских механизмов»?",
        "answers": ["Шарлотта Бранвелл","Шарлотта"]
    },
    {
        "question": "Как зовут фэйри, который помогает Клэри и ее друзьям?",
        "answers": ["Мелиорн"]
    },
    {
        "question": "Как называется измерение, откуда приходят демоны?",
        "answers": ["Эдом","Дом кошатника"]
    },
    {
        "question": "Кто создал Орудия Смерти?",
        "answers": ["Разиэль", "Ангел Разиель"]
    },
    {
        "question": "Как зовут мать Клэри?",
        "answers": ["Джоселин Фэйрчайлд", "Джоселин"]
    },
    {
        "question": "Как зовут Безмолвного Брата, который помогает Клэри и её друзьям?",
        "answers": ["Брат Захария","Захария"]
    },
    {
        "question": "Как называется оружие, которое использовала Изабель Лайтвуд?",
        "answers": ["Электрумный кнут","Кнут"]
    },
    {
        "question": "Как зовут демона, которого вызывал Валентин Моргенштерн?",
        "answers": ["Великий Демон Азазель","Азазель"]
    },
    {
        "question": "Какая последняя книга из серии 'Орудия смерти'?",
        "answers": ["Город Небесного Огня"]
    },
    {
        "question": "Кто в семье Блэкторнов приходится всем младшим братом?",
        "answers": ["Тавви Блэкторн","Тавви", "Тав"]
    },
    {
        "question": "Как зовут Сумеречного Охотника, известного изобретением новых рун?",
        "answers": ["Клэри Фрэй", "Кларисса Фэйрчайлд", "Клэри", "Кларисса"]
    },
    {
        "question": "Как называется ангельское ожерелье Тессы Грей?",
        "answers": ["Заводной ангел","Заводной Ангел"]
    },
    {
        "question": "Кто главный герой серии «Адские механизмы»?",
        "answers": ["Тесса Грей","Тесса"]
    },
    {
        "question": "Как зовут домашнего кота Магнуса Бейна?",
        "answers": ["Председатель Мяу","Председатель", "Мяу", "Черч", "Чёрч"]
    },
    {
        "question": "Как называется руна, которая связывает двух Сумеречных Охотников?",
        "answers": ["Парабатай","Руна Парабатай", "парабатай"]
    },
    {
        "question": "Как зовут инквизитора, пытавшего Джейса в «Городе Стекла»?",
        "answers": ["Имоджен Эрондейл","Имоджен"]
    },
    {
        "question": "Как называется волшебная книга, содержащая мощные заклинания?",
        "answers": ["Книга Белого","Белая книга"]
    },
    {
        "question": "Как зовут демона, убивший мать Клэри?",
        "answers": ["Абаддон"]
    },
    {
        "question": "Где базируется клан вампиров в Нью-Йорке?",
        "answers": ["Отель Дюморт","Отель","Дюморт"]
    },
    {
        "question": "Кто главный герой серии «Последние часы»?",
        "answers": ["Корделия Карстерс","Корделия"]
    },
    {
        "question": "Как называется организация, которая управляет Сумеречными охотниками?",
        "answers": ["Конклав","Клэйв"]
    },
    {
        "question": "Кто является главой Института в «Тёмных искусствах»?",
        "answers": ["Диана Рэйберн","Диана"]
    },
    {
        "question": "Какая фамилия у представителей приёмной семьи Джейса?",
        "answers": ["Лайтвуд","Лайтвуды"]
    },
    {
        "question": "Кто главный антагонист в «Адских механизмах»?",
        "answers": ["Мортмейн"]
    },
    {
        "question": "Как зовут оборотня, который становится вожаком нью-йоркской стаи?",
        "answers": ["Люк Гэрроуей", "Люк"]
    },
    {
        "question": "Кто главный антагонист в «Орудиях смерти»?",
        "answers": ["Валентин Моргенштерн","Валентин","Валя"]
    },
    {
        "question": "Как называется книга заклинаний, которую Клэри использует для создания новых рун?",
        "answers": ["Серая книга","Книга Серого"]
    },
    {
        "question": "Как зовут фэйри-рыцаря, который стал Сумеречным охотником?",
        "answers": ["Марк Блэкторн","Марк"]
    },
    {
        "question": "Кто является лидером клана вампиров Нью-Йорка?",
        "answers": ["Рафаэль Сантьяго","Рафаэль"]
    },
    {
        "question": "Для чего нужна Чаша Смерти?",
        "answers": ["Создание Сумеречных Охотников","Создание новых Сумеречных Охотников", "Для создания Сумеречных Охотников", "Для создания новых Сумеречных охотников"]
    },
    {
        "question": "Кто был первым Сумеречным Охотником?",
        "answers": ["Джонатан Шадоухантер","Джонатан","Джонатан Шэдоухантер","Джонатан Шедоухантер"]
    },
    {
        "question": "Каков девиз Сумеречных Охотников?",
        "answers": ["Закон суров, но это Закон","Sed lex dura lex"]
    },
    {
        "question": "Как называется руна, дарующая невидимость?",
        "answers": ["Руна Сокрытия","Сокрытие"]
    },
    {
        "question": "Как называется город, в котором расположена Академия Сумеречных Охотников?",
        "answers": ["Аликанте"]
    },
    {
        "question": "Кого называют Королевой Воздуха и Тьмы?",
        "answers": ["Аннабель Блэкторн","Аннабель"]
    },
    {
        "question": "Кто является лидером Железных сестер?",
        "answers": ["Сестра Клеофа","Клеофа"]
    },
    {
        "question": "Кто муж Тессы Грей? Можно одного из.",
        "answers": ["Уилл Эрондейл","Уилл","Джем Карстерс","Джем"]
    },
    {
        "question": "Как называется родина Сумеречных Охотников?",
        "answers": ["Идрис"]
    },
    {
        "question": "Как зовут мать Джейса Эрондейла?",
        "answers": ["Селин Эрондейл","Селин", "Селина Эрондейл", "Селина"]
    },
    # Add more questions and answers here
]

active_question = None

async def reconnect_db_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Close existing connection
        conn.close()
        # Reconnect
        conn = connect_db()
        cur = conn.cursor(cursor_factory=DictCursor)
        await update.message.reply_text("✅ Successfully reconnected to the database.")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to reconnect to the database: {str(e)}")

@reconnect_db
async def send_question(context: ContextTypes.DEFAULT_TYPE):
    global active_question
    chat_id = -1001996636325  # Second chat ID
    active_question = random.choice(questions)
    await context.bot.send_message(chat_id=chat_id, text=f"❓ Викторина! Ответьте на вопрос и получите 200 💎 Камней душ! Вопрос: {active_question['question']}")

    # Schedule repeating the question if not answered
    context.job_queue.run_once(repeat_question, 3600, context=chat_id)

@reconnect_db
async def repeat_question(context: ContextTypes.DEFAULT_TYPE):
    global active_question
    chat_id = context.job.context
    if active_question is not None:
        await context.bot.send_message(chat_id=chat_id, text=f"😢 Время вышло! Правильный ответ был: {active_question['answers'][0]}\n\nСледующий вопрос через 2 часа!")
        active_question = None  # Reset the active question
        context.job_queue.run_once(send_question, 7200, context=chat_id)

@reconnect_db
async def start_quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Schedule the job to send a question immediately
    await send_question(context)
    context.job_queue.run_once(repeat_question, when=7200, context=-1001996636325)  # 2 hours from now

@reconnect_db
async def answer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global active_question
    if active_question is None:
        return

    user_answer = update.message.text.strip().lower()
    correct_answers = [answer.lower() for answer in active_question['answers']]

    if user_answer in correct_answers:
        user_id = update.message.from_user.id
        user_mention = update.message.from_user.username or update.message.from_user.first_name
        mention_text = f"@{user_mention}" if update.message.from_user.username else user_mention

        new_balance = await update_balance(user_id, 200)
        await update.message.reply_text(f"💎 {mention_text}, верный ответ! Щедро сыплю тебе 200 💎 Камней душ! Текущий баланс: {new_balance}💎.")
        active_question = None  # Reset the active question

        # Schedule the next question in 2 hours
        context.job_queue.run_once(send_question, 7200, context=-1001996636325)

@reconnect_db
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        message_text = update.message.text
        target_group_id_1 = -1002142915618  # Adjust this ID to your target group
        target_group_id_2 = -1001996636325  # Other active users chat ID

        logger.info(f"Received message in group {update.message.chat_id}: {message_text[:50]}")
        
        user_id = update.message.from_user.id

        if update.message.chat_id == target_group_id_1 and len(message_text) >= 500:
            user_mention = update.message.from_user.username or update.message.from_user.first_name
            mention_text = f"@{user_mention}" if update.message.from_user.username else user_mention

            user_rank = await get_user_rank(user_id)
            rank_rewards = {
                "👦🏻 Смертный": 5,
                "😎 Новичок": 15,
                "😼 Новоприбывший Охотник": 30,
                "🧐 Опытный охотник": 50,
                "🫡 Лидер миссий Института": 85,
                "🧑🏻‍✈️ Лидер Института": 135,
                "🧑🏻‍⚖️ Кандидат в Инквизиторы": 200,
                "🤴🏻 Инквизитор": 300
            }

            reward = rank_rewards.get(user_rank, 5)
            new_balance = await update_balance(user_id, reward)
            await update.message.reply_text(f"💎 {mention_text}, ваш пост зачтён. Вам начислено +{reward} к камням душ. Текущий баланс: {new_balance}💎.")

        if update.message.chat_id == target_group_id_2:
            message_count = await increment_message_count(user_id)
            if message_count % 200 == 0:
                await update_balance(user_id, 150)
                await update.message.reply_text(f"🎉 Вы отправили {message_count} сообщений и получили 150 Камней душ! Текущий баланс: {await get_balance(user_id)}💎.")

@reconnect_db
async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_mention = update.message.from_user.username or update.message.from_user.first_name
    mention_text = f"@{user_mention}" if update.message.from_user.username else user_mention
    balance = await get_balance(user_id)
    await update.message.reply_text(f"💎 {mention_text}, ваш текущий баланс: {balance}💎.")

# handlers.py

@reconnect_db
async def get_message_count(user_id, chat_id):
    cur.execute('SELECT message_count FROM user_messages WHERE user_id = %s AND chat_id = %s', (user_id, chat_id))
    result = cur.fetchone()
    return result['message_count'] if result else 0

@reconnect_db
async def checkin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    today = datetime.now()
    cur.execute('SELECT streak, last_checkin FROM checkin_streak WHERE user_id = %s', (user_id,))
    result = cur.fetchone()

    if result:
        streak, last_checkin = result['streak'], result['last_checkin']

        # Check if the user has already checked in today
        if today.date() == last_checkin.date():
            await update.message.reply_text("⚠️ Вы уже получали награду за вход сегодня. Повторите попытку завтра. ✨")
            return

        # Check if the streak is broken
        if today - last_checkin > timedelta(days=1):
            streak = 1
            reward = 25
            image_path = 'img/lossStreak.png'
            await update.message.reply_photo(photo=open(image_path, 'rb'), caption="😔 К сожалению, вы прервали череду ежедневных входов и получили только 25 💎 Камней душ.")
        else:
            streak += 1
            if streak > 7:
                streak = 7  # Cap streak at 7
            reward = 25 * streak
            image_path = f'img/check{streak}.png'
            await update.message.reply_photo(photo=open(image_path, 'rb'), caption=f"✅ Вы выполнили ежедневный вход {streak} дней подряд и получили {reward} 💎 Камней душ!")
    else:
        streak = 1
        reward = 25
        image_path = 'img/check1.png'
        await update.message.reply_photo(photo=open(image_path, 'rb'), caption=f"✅ Вы выполнили ежедневный вход 1 день подряд и получили 25 💎 Камней душ!")

    # Update the last check-in date and streak
    cur.execute('INSERT INTO checkin_streak (user_id, streak, last_checkin) VALUES (%s, %s, %s) ON CONFLICT (user_id) DO UPDATE SET streak = %s, last_checkin = %s', (user_id, streak, today, streak, today))
    conn.commit()

    new_balance = await update_balance(user_id, reward)

    user_mention = update.message.from_user.username or update.message.from_user.first_name
    mention_text = f"@{user_mention}" if update.message.from_user.username else user_mention

    await update.message.reply_text(f"💎 {mention_text}, ваш текущий баланс: {new_balance}💎.")

readings = [
    "Сегодня ангельская сила будет направлять тебя.",
    "Новая руна откроет тебе свою истинную цель.",
    "Остерегайся демонов, прячущихся в неожиданных местах.",
    "Союзник из Нижнего мира окажет важную помощь.",
    "Твой серфимский клинок будет сегодня сиять ярче в твоих руках.",
    "Институт хранит секрет, который изменит твой путь.",
    "Связь парабатай укрепит твою решимость.",
    "Сообщение из Идриса принесет важные новости.",
    "Мудрость Безмолвных братьев поможет в твоем приключении.",
    "Новое задание проверит твои способности Сумеречного охотника.",
    "Решение Конклава повлияет на твое будущее.",
    "Маг откроет тебе портал в значимое место.",
    "Твой стеле создаст руну огромной силы.",
    "Древняя книга заклинаний откроет забытое временем проклятие.",
    "Загадка фейри приведет тебя к скрытой истине.",
    "Твоя связь с ангельским миром станет сильнее.",
    "Лояльность вампира окажется неоценимой.",
    "Заклинание колдуна принесет ясность в запутанную ситуацию.",
    "Демонические миры необычайно активны; будь на чеку.",
    "Сон даст тебе представление о будущем.",
    "Скрытая руна откроет новую способность.",
    "Ищи ответы в Кодексе. Он знает что тебе подсказать",
    "Смертный удивит тебя своей храбростью.",
    "Потерянная семейная реликвия обретет новое значение.",
    "Теневой рынок содержит предмет, важный для твоего задания.",
    "Столкновение с мятежным Сумеречным охотником неизбежно.",
    "Церемония рун приблизит тебя к твоему истинному потенциалу.",
    "Посещение Зала Согласия очень необходимо.",
    "Неожиданный союз сформируется с обитателем Нижнего мира.",
    "Твой серфимский клинок поможет уничтожить скрытого демона.",
    "Запретное заклинание будет искушать тебя великой силой.",
    "Сообщение из Благого Двора прибудет с настоятельностью.",
    "Призрак прошлого Сумеречного охотника предложит мудрость.",
    "Зачарованный артефакт усилит твои способности.",
    "Твоя лояльность Конклаву будет испытана.",
    "Пророчество из Молчаливого Города выйдет на свет.",
    "Редкий демон потребует твоего немедленного внимания.",
    "Старый друг вернется с удивительными новостями.",
    "Видение от ангела Разиэля направит твой путь.",
    "Сила Смертной Чаши будет ощущаться особенно сильно сегодня.",
    "Путешествие в Город Костей раскроет скрытые знания.",
    "Звук рога Сумеречных охотников сигнализирует важное событие.",
    "Таинственная руна появится в твоих снах.",
    "Встреча с Двором Сумерек изменит твою судьбу.",
    "Тайна Инквизитора будет раскрыта.",
    "Скрытый вход в Институт приведет к новому открытию.",
    "Неожиданный подарок от мага удивит тебя.",
    "Тайное послание от фейри будет обнаружено.",
    "Орудие смерти раскроет свою истинную силу.",
    "Восстание Сумеречных охотников на горизонте.",
    "Мудрость Безмолвных братьев защитит тебя.",
    "Старый дневник Сумеречного охотника содержат ключ к разгадке.",
    "Ожерелье Ангела исполнит свою магию.",
    "Ожидай неожиданного гостя из Нижнего мира.",
    "Древнее проклятие будет снято.",
    "Посещение библиотеки Института обнаружит важную подсказку.",
    "Твоя связь с парабатай обеспечит силу и ясность."
]

@reconnect_db
async def reading_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not await can_request_reading(user_id):
        await update.message.reply_text("⚠️ Вы уже запросили гадание сегодня. Повторите попытку завтра.")
        return

    if await reduce_balance(user_id, 50) is None:
        await update.message.reply_text("⚠️ Недостаточно Камней Душ для запроса гадания.")
        return

    await update.message.reply_text("💎 Камни душ с лёгким треском осыпались на стол. Магнус вскинул на них свой взор, улыбнулся и положил руку на хрустальный шар... 🔮")
    await asyncio.sleep(2)

    reading = random.choice(readings)
    await update.message.reply_photo(photo=open('img/reading.png', 'rb'), caption=f"🔮 Ваше гадание на сегодня: 🔮\n\n{reading} 🔮")

@reconnect_db
async def rockpaperscissors_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    cur.execute('SELECT last_play FROM last_game WHERE user_id = %s', (user_id,))
    result = cur.fetchone()
    now = datetime.now()

    if result:
        last_play = result['last_play']
        if now - last_play < timedelta(minutes=10):
            await update.message.reply_text("⚠️ Вы можете играть только раз в 10 минут. Попробуйте позже.")
            return

    buttons = [
        InlineKeyboardButton("25", callback_data="bet_25"),
        InlineKeyboardButton("50", callback_data="bet_50"),
        InlineKeyboardButton("100", callback_data="bet_100"),
        InlineKeyboardButton("200", callback_data="bet_200"),
        InlineKeyboardButton("500", callback_data="bet_500")
    ]
    keyboard = InlineKeyboardMarkup.from_column(buttons)
    await update.message.reply_text("📤 Выберите количество Камней душ, которые вы хотите поставить:", reply_markup=keyboard)

@reconnect_db
async def bet_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    bet = int(query.data.split('_')[1])
    balance = await get_balance(user_id)

    if balance < bet:
        await query.edit_message_text("⚠️ У вас недостаточно Камней душ для этой ставки.")
        return

    buttons = [
        InlineKeyboardButton("🪨", callback_data=f"play_{bet}_rock"),
        InlineKeyboardButton("📄", callback_data=f"play_{bet}_paper"),
        InlineKeyboardButton("✂️", callback_data=f"play_{bet}_scissors")
    ]
    keyboard = InlineKeyboardMarkup.from_row(buttons)
    await query.edit_message_text("✊ Выберите, что вы хотите выбросить:", reply_markup=keyboard)

@reconnect_db
async def play_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    bet, user_choice = query.data.split('_')[1:]
    bet = int(bet)
    choices = ['rock', 'paper', 'scissors']
    bot_choice = random.choice(choices)

    outcomes = {
        ('rock', 'scissors'): "win",
        ('rock', 'paper'): "lose",
        ('paper', 'rock'): "win",
        ('paper', 'scissors'): "lose",
        ('scissors', 'paper'): "win",
        ('scissors', 'rock'): "lose"
    }

    if user_choice == bot_choice:
        result = "draw"
    else:
        result = outcomes.get((user_choice, bot_choice))

    if result == "win":
        new_balance = await update_balance(user_id, bet)
        await query.edit_message_text(f"🥳 Поздравляем! Вы выиграли {bet} 💎 Камней душ. Ваш текущий баланс: {new_balance}💎.")
    elif result == "lose":
        new_balance = await update_balance(user_id, -bet)
        await query.edit_message_text(f"🥴 Вы проиграли {bet} 💎 Камней душ. Ваш текущий баланс: {new_balance}💎.")
    else:
        await query.edit_message_text(f"🤝 Ничья! Ваш баланс остался прежним: {await get_balance(user_id)}💎.")

    # Update the last play time
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cur.execute('INSERT INTO last_game (user_id, last_play) VALUES (%s, %s) ON CONFLICT (user_id) DO UPDATE SET last_play = %s', (user_id, now, now))
    conn.commit()

@reconnect_db
async def add_balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if await get_user_role(user_id) != 'admin':
        await update.message.reply_text("⚠️ У вас нет прав для выполнения этой команды.")
        return

    if len(context.args) != 2:
        await update.message.reply_text("⚠️ Использование: /addbalance <user_id> <amount>")
        return

    target_user_id, amount = context.args
    try:
        amount = int(amount)
    except ValueError:
        await update.message.reply_text("⚠️ Пожалуйста, введите корректное число.")
        return

    new_balance = await update_balance(int(target_user_id), amount)
    await update.message.reply_text(f"⚠️ Баланс пользователя {target_user_id} увеличен на {amount} 💎 Камней душ. Новый баланс: {new_balance}💎.")

@reconnect_db
async def sub_balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if await get_user_role(user_id) != 'admin':
        await update.message.reply_text("⚠️ У вас нет прав для выполнения этой команды.")
        return

    if len(context.args) != 2:
        await update.message.reply_text("⚠️ Использование: /subbalance <user_id> <amount>")
        return

    target_user_id, amount = context.args
    try:
        amount = int(amount)
    except ValueError:
        await update.message.reply_text("⚠️ Пожалуйста, введите корректное число.")
        return

    new_balance = await reduce_balance(int(target_user_id), amount)
    if new_balance is None:
        await update.message.reply_text("⚠️ Недостаточно Камней душ для выполнения операции.")
        return

    await update.message.reply_text(f"⚠️ Баланс пользователя {target_user_id} уменьшен на {amount} 💎 Камней душ. Новый баланс: {new_balance}💎.")

@reconnect_db
async def set_balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if await get_user_role(user_id) != 'admin':
        await update.message.reply_text("⚠️ У вас нет прав для выполнения этой команды.")
        return

    if len(context.args) != 2:
        await update.message.reply_text("⚠️ Использование: /setbalance <user_id> <amount>")
        return

    target_user_id, amount = context.args
    try:
        amount = int(amount)
    except ValueError:
        await update.message.reply_text("⚠️ Пожалуйста, введите корректное число.")
        return

    new_balance = await set_balance(int(target_user_id), amount)
    await update.message.reply_text(f"⚠️ Баланс пользователя {target_user_id} установлен на {amount} 💎 Камней душ. Новый баланс: {new_balance}💎.")

PROMOTE_USER_ID = range(1)

@reconnect_db
async def promote_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    super_admin_id = 6505061807  # Replace with your actual super admin ID
    user_id = update.message.from_user.id

    if user_id != super_admin_id:
        await update.message.reply_text("⚠️ У вас нет прав для выполнения этой команды.")
        return ConversationHandler.END

    await update.message.reply_text("⚠️ Пожалуйста, введите user_id аккаунта, который вы хотите повысить до администратора.")
    return PROMOTE_USER_ID

@reconnect_db
async def receive_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        target_user_id = int(update.message.text)
    except ValueError:
        await update.message.reply_text("⚠️ Пожалуйста, введите корректное число.")
        return PROMOTE_USER_ID

    await get_user_role(target_user_id, 'admin')
    await update.message.reply_text(f"❗️ Пользователь {target_user_id} повышен до администратора.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚠️ Отменено.")
    return ConversationHandler.END

@reconnect_db
async def missions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    today = datetime.datetime.now().date()

    # Check if user has already attempted 3 missions today
    cur.execute('SELECT attempts FROM mission_attempts WHERE user_id = %s AND date = %s', (user_id, today))
    result = cur.fetchone()
    attempts = result['attempts'] if result else 0

    if attempts >= 3:
        await update.message.reply_text("✨ Вы уже отправили 3 отряда на миссии сегодня. ⌛️ Повторите попытку завтра. ")
        return

    # Generate 5 random missions based on appearance rates
    missions = await generate_missions()

    # Create buttons for each mission
    buttons = [
        InlineKeyboardButton(
            f"{mission['name']} ({mission['reward']} 💎 камней душ)",
            callback_data=f"mission_{mission['id']}"
        )
        for mission in missions
    ]
    keyboard = InlineKeyboardMarkup.from_column(buttons)
    await update.message.reply_text("⚔️ Выберите миссию для отправки отряда:", reply_markup=keyboard)

@reconnect_db
async def mission_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    mission_id = int(query.data.split('_')[1])

    # Fetch mission details using mission_id
    cur.execute('SELECT * FROM missions WHERE id = %s', (mission_id,))
    mission = cur.fetchone()

    if not mission:
        await query.edit_message_text("⚠️ Ошибка: миссия не найдена.")
        return

    # Check if user has already attempted 3 missions today
    today = datetime.datetime.now().date()
    cur.execute('SELECT attempts FROM mission_attempts WHERE user_id = %s AND date = %s', (user_id, today))
    result = cur.fetchone()
    attempts = result['attempts'] if result else 0

    if attempts >= 3:
        await query.edit_message_text("✨ Вы уже отправили 3 отряда на миссии сегодня. ⌛️ Повторите попытку завтра. ")
        return

    # Increment the number of attempts for today
    if result:
        cur.execute('UPDATE mission_attempts SET attempts = attempts + 1 WHERE user_id = %s AND date = %s', (user_id, today))
    else:
        cur.execute('INSERT INTO mission_attempts (user_id, date, attempts) VALUES (%s, %s, 1)', (user_id, today))
    conn.commit()

    # Calculate mission end time
    start_time = datetime.datetime.now()
    end_time = start_time + datetime.timedelta(hours=mission['length'])

    # Insert mission into user_missions table
    cur.execute('INSERT INTO user_missions (user_id, mission_id, start_time, end_time) VALUES (%s, %s, %s, %s)', (user_id, mission_id, start_time, end_time))
    conn.commit()

    await query.edit_message_text(f"💼 Вы отправили отряд на миссию: ✨{mission['name']}✨.  🌒 Время завершения: ⌛️ {end_time.strftime('%Y-%m-%d %H:%M:%S')} ⌛️.")

@reconnect_db
async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_mention = update.message.from_user.username or update.message.from_user.first_name
    mention_text = f"@{user_mention}" if update.message.from_user.username else user_mention

    user_rank = await get_user_rank(user_id)
    user_balance = await get_balance(user_id)
    symbols_count = await get_user_symbols(user_id)
    second_chat_message_count = await get_user_messages(user_id, -1001996636325)

    profile_text = (
        f"Профиль {mention_text}:\n"
        f"🏅 Ранк: {user_rank}\n"
        f"💎 Баланс Камней душ: {user_balance}\n"
        f"🔣 Символов в рп-чате: {symbols_count}\n"
        f"✉️ Сообщений в флуд-чате: {second_chat_message_count}"
    )

    buttons = [
        [InlineKeyboardButton("Баланс", callback_data="balance")],
        [InlineKeyboardButton("Предсказание от Магнуса", callback_data="reading")],
        [InlineKeyboardButton("Ежедневная награда", callback_data="checkin")],
        [InlineKeyboardButton("Камень-ножницы-бумага", callback_data="rockpaperscissors")],
        [InlineKeyboardButton("Миссии", callback_data="missions")]
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(profile_text, reply_markup=keyboard)