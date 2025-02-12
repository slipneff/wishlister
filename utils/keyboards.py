from typing import Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([
        [KeyboardButton("➕ Добавить желание"), KeyboardButton("📋 Мой список")],
        [KeyboardButton("👥 Мои подписки"), KeyboardButton("👤 Мои подписчики")]
    ], resize_keyboard=True)

def get_subscriptions_keyboard(subscriptions: list) -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton("🔍 Найти пользователя", callback_data='search_user')]]
    
    if subscriptions:
        keyboard.append([InlineKeyboardButton("── Мои подписки ──", callback_data='none')])
        keyboard.extend([
            [InlineKeyboardButton(f"📋 @{username}", callback_data=f'view_{username}'),
             InlineKeyboardButton("❌", callback_data=f'unsubscribe_{username}')]
            for username in subscriptions
        ])
    
    return InlineKeyboardMarkup(keyboard)

def get_wish_keyboard(wish_id: int, status: str) -> Optional[InlineKeyboardMarkup]:
    if status == 'active':
        return InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Исполнено", callback_data=f'complete_{wish_id}')
        ]])
    return None
