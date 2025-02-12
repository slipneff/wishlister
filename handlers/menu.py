from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from utils.states import State
from utils.keyboards import get_main_keyboard

async def handle_menu_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "➕ Добавить желание":
        from handlers.wishes import add_wish
        return await add_wish(update, context)
    elif text == "📋 Мой список":
        from handlers.wishes import show_wishlist
        return await show_wishlist(update, context)
    elif text == "👥 Мои подписки":
        from handlers.subscriptions import show_subscriptions
        return await show_subscriptions(update, context)
    elif text == "👤 Мои подписчики":
        from handlers.subscriptions import show_followers
        return await show_followers(update, context)
    elif text == "🔙 Назад":
        return await back_to_menu(update, context)
    elif text.startswith("@"):
        from handlers.subscriptions import show_user_wishlist
        return await show_user_wishlist(update, context, text[1:])
    
    return State.CHOOSING

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Вы вернулись в главное меню",
        reply_markup=get_main_keyboard()
    )
    return State.CHOOSING
