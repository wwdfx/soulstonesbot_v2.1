import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ConversationHandler, JobQueue
from handlers import *
from utils import check_missions
from datetime import timedelta
from database import connect_db, DB_DETAILS

# Connect to PostgreSQL Database
def connect_db():
    conn = psycopg2.connect(**DB_DETAILS)
    conn.autocommit = True
    return conn

# Set up basic logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the bot and add handlers
app = ApplicationBuilder().token("7175746196:AAHckVjmat7IBpqvzWfTxvUzvQR1_1FgLiw").build()

# Conversation handler for promoting a user to admin
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('promote', promote_command)],
    states={
        PROMOTE_USER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_user_id)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
app.add_handler(CommandHandler("balance", balance_command))
app.add_handler(CommandHandler("checkin", checkin_command))
app.add_handler(CommandHandler("reading", reading_command))
app.add_handler(CommandHandler("rockpaperscissors", rockpaperscissors_command))
app.add_handler(CommandHandler("addbalance", add_balance_command))
app.add_handler(CommandHandler("subbalance", sub_balance_command))
app.add_handler(CommandHandler("setbalance", set_balance_command))
app.add_handler(CommandHandler("missions", missions_command))
app.add_handler(CommandHandler("profile", profile_command))
app.add_handler(CommandHandler("startquiz", start_quiz_command))
app.add_handler(CommandHandler("reconnectdb", reconnect_db_command))
app.add_handler(conv_handler)
app.add_handler(CallbackQueryHandler(bet_callback, pattern='^bet_'))
app.add_handler(CallbackQueryHandler(play_callback, pattern='^play_'))
app.add_handler(CallbackQueryHandler(mission_callback, pattern='^mission_'))
app.add_handler(CallbackQueryHandler(balance_command, pattern='^balance$'))
app.add_handler(CallbackQueryHandler(reading_command, pattern='^reading$'))
app.add_handler(CallbackQueryHandler(checkin_command, pattern='^checkin$'))
app.add_handler(CallbackQueryHandler(rockpaperscissors_command, pattern='^rockpaperscissors$'))
app.add_handler(CallbackQueryHandler(missions_command, pattern='^missions$'))
app.add_handler(MessageHandler(filters.TEXT & filters.Chat(chat_id=-1001996636325), answer_handler), group=-1001996636325)

job_queue = app.job_queue
job_queue.run_repeating(check_missions, interval=6000, first=6000)
job_queue.run_repeating(send_question, interval=timedelta(hours=2), first=0)

app.run_polling()