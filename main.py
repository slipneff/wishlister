import logging
import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ConversationHandler
from telegram import Update
from telegram.ext import ContextTypes

from database.db import Database
from handlers.menu import handle_menu_choice
from handlers.wishes import add_wish, handle_title, handle_price, handle_link, handle_photo
from handlers.subscriptions import handle_callback
from utils.states import State
from utils.keyboards import get_main_keyboard

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    with Database() as cursor:
        cursor.execute('INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)',
                      (user.id, user.username))
    
    await update.message.reply_text(
        "Добро пожаловать! Выберите действие:",
        reply_markup=get_main_keyboard()
    )
    return State.CHOOSING

def main():
    db = Database()
    db.init_db()
    
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        raise ValueError("BOT_TOKEN not found in environment variables")
    
    application = Application.builder().token(bot_token).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            State.CHOOSING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_choice)
            ],
            State.ADDING_TITLE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_title)
            ],
            State.ADDING_PRICE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_price)
            ],
            State.ADDING_LINK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link)
            ],
            State.ADDING_PHOTO: [
                MessageHandler(filters.PHOTO | filters.TEXT & ~filters.COMMAND, handle_photo)
            ]
        },
        fallbacks=[MessageHandler(filters.TEXT & ~filters.COMMAND, start)]
    )
    
    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    application.run_polling()

if __name__ == '__main__':
    main()
