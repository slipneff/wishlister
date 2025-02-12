from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from database.db import Database
from utils.keyboards import get_main_keyboard, get_subscriptions_keyboard

async def show_user_wishlist(update: Update, context: ContextTypes.DEFAULT_TYPE, target_username: str):
    with Database() as cursor:
        cursor.execute('SELECT user_id FROM users WHERE username = ?', (target_username,))
        result = cursor.fetchone()
        
        if not result:
            message = update.callback_query.message if update.callback_query else update.message
            await message.reply_text(
                f"Пользователь @{target_username} не найден",
                reply_markup=get_main_keyboard()
            )
            return
        
        target_user_id = result[0]
        viewer_id = update.effective_user.id
        
        cursor.execute(
            '''SELECT 1 FROM subscriptions 
               WHERE subscriber_id = ? AND target_user_id = ?''', 
            (viewer_id, target_user_id)
        )
        is_subscribed = bool(cursor.fetchone())
        
        cursor.execute(
            '''SELECT id, title, price, link, photo_id, status 
               FROM wishes 
               WHERE user_id = ? AND status != 'completed'
               ORDER BY date_added DESC''', (target_user_id,)
        )
        wishes = cursor.fetchall()
    
    message = update.callback_query.message if update.callback_query else update.message
    
    if not wishes:
        subscribe_button = [] if is_subscribed else [[InlineKeyboardButton("➕ Подписаться", callback_data=f'subscribe_{target_username}')]]
        reply_markup = InlineKeyboardMarkup(subscribe_button) if subscribe_button else None
        
        await message.reply_text(
            f"Список желаний @{target_username} пуст",
            reply_markup=reply_markup
        )
        return
    
    subscribe_button = [] if is_subscribed else [[InlineKeyboardButton("➕ Подписаться", callback_data=f'subscribe_{target_username}')]]
    await message.reply_text(
        f"Список желаний пользователя @{target_username}:",
        reply_markup=InlineKeyboardMarkup(subscribe_button) if subscribe_button else None
    )
    
    for wish in wishes:
        wish_id, title, price, link, photo_id, status = wish
        status_text = "🔒 Забронировано" if status == 'booked' else ""
        keyboard = [[InlineKeyboardButton("🎁 Забронировать", callback_data=f'book_{wish_id}')]] if status == 'active' else []
        text = f"🎁 {title}\n💰 Цена: {price}\n🔗 {link}\n{status_text}"
        
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        
        if photo_id:
            await message.reply_photo(photo_id, caption=text, reply_markup=reply_markup)
        else:
            await message.reply_text(text, reply_markup=reply_markup)

async def book_wish(update: Update, context: ContextTypes.DEFAULT_TYPE, wish_id: int):
    query = update.callback_query
    booker_id = update.effective_user.id
    
    with Database() as cursor:
        cursor.execute('SELECT user_id, status FROM wishes WHERE id = ?', (wish_id,))
        result = cursor.fetchone()
        
        if not result:
            await query.answer("Желание не найдено")
            return
        
        wish_owner_id, status = result
        
        if status != 'active':
            await query.answer("Это желание уже забронировано или исполнено")
            return
        
        cursor.execute(
            '''UPDATE wishes 
               SET status = 'booked', booked_by = ? 
               WHERE id = ?''', (booker_id, wish_id)
        )
        
        await context.bot.send_message(
            chat_id=wish_owner_id,
            text="Одно из ваших желаний было анонимно забронировано! 🎉"
        )
    
    await query.answer("Желание успешно забронировано!")
    await query.edit_message_reply_markup(reply_markup=None)

async def show_subscriptions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    with Database() as cursor:
        cursor.execute(
            '''SELECT users.username FROM subscriptions 
               JOIN users ON subscriptions.target_user_id = users.user_id 
               WHERE subscriber_id = ?''', (user_id,)
        )
        subscriptions = [row[0] for row in cursor.fetchall()]
    
    keyboard = get_subscriptions_keyboard(subscriptions)
    
    if subscriptions:
        await update.message.reply_text(
            "Управление подписками:\n\n"
            "• Нажмите 🔍, чтобы найти пользователя\n"
            "• Нажмите на имя пользователя, чтобы увидеть его список желаний\n"
            "• Нажмите ❌, чтобы отписаться",
            reply_markup=keyboard
        )
    else:
        await update.message.reply_text(
            "У вас пока нет подписок.\n"
            "Нажмите кнопку ниже, чтобы найти пользователя:",
            reply_markup=keyboard
        )

async def show_followers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    with Database() as cursor:
        cursor.execute(
            '''SELECT users.username FROM subscriptions 
               JOIN users ON subscriptions.subscriber_id = users.user_id 
               WHERE target_user_id = ?''', (user_id,)
        )
        followers = cursor.fetchall()
    
    if not followers:
        await update.message.reply_text(
            "У вас пока нет подписчиков.",
            reply_markup=get_main_keyboard()
        )
        return
    
    text = "Ваши подписчики:\n\n" + "\n".join(f"• @{follower[0]}" for follower in followers)
    await update.message.reply_text(text, reply_markup=get_main_keyboard())

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    if query.data == 'none':
        await query.answer()
        return
    
    await query.answer()
    
    if query.data == 'search_user':
        await search_user(update, context)
    elif query.data.startswith('unsubscribe_'):
        username = query.data.split('_')[1]
        context.args = [username]
        await unsubscribe(update, context)
        await show_subscriptions(update, context)
    elif query.data.startswith('subscribe_'):
        username = query.data.split('_')[1]
        context.args = [username]
        await subscribe(update, context)
        await show_user_wishlist(update, context, username)
    elif query.data.startswith('view_'):
        username = query.data.split('_')[1]
        await show_user_wishlist(update, context, username)
    elif query.data.startswith('book_'):
        wish_id = int(query.data.split('_')[1])
        await book_wish(update, context, wish_id)
    elif query.data.startswith('complete_'):
        from handlers.wishes import complete_wish
        wish_id = int(query.data.split('_')[1])
        await complete_wish(update, context, wish_id)

async def search_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.callback_query.message if update.callback_query else update.message
    await message.reply_text(
        "Отправьте username пользователя (например: @username)",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🔙 Назад")]], resize_keyboard=True)
    )

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Укажите username пользователя: /subscribe @username")
        return
    
    target_username = context.args[0].replace('@', '')
    subscriber_id = update.effective_user.id
    
    with Database() as cursor:
        cursor.execute('SELECT user_id FROM users WHERE username = ?', (target_username,))
        result = cursor.fetchone()
        
        if not result:
            await _handle_subscription_response(update, f"Пользователь @{target_username} не найден")
            return
        
        target_user_id = result[0]
        
        cursor.execute(
            '''SELECT 1 FROM subscriptions 
               WHERE subscriber_id = ? AND target_user_id = ?''',
            (subscriber_id, target_user_id)
        )
        
        if cursor.fetchone():
            await _handle_subscription_response(update, f"Вы уже подписаны на @{target_username}")
            return
        
        cursor.execute(
            '''INSERT INTO subscriptions (subscriber_id, target_user_id)
               VALUES (?, ?)''', (subscriber_id, target_user_id)
        )
    
    await _handle_subscription_response(update, f"Вы успешно подписались на @{target_username}")

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Укажите username пользователя: /unsubscribe @username")
        return
    
    target_username = context.args[0].replace('@', '')
    subscriber_id = update.effective_user.id
    
    with Database() as cursor:
        cursor.execute('SELECT user_id FROM users WHERE username = ?', (target_username,))
        result = cursor.fetchone()
        
        if not result:
            await _handle_subscription_response(update, f"Пользователь @{target_username} не найден")
            return
        
        target_user_id = result[0]
        
        cursor.execute(
            '''DELETE FROM subscriptions 
               WHERE subscriber_id = ? AND target_user_id = ?''',
            (subscriber_id, target_user_id)
        )
    
    await _handle_subscription_response(update, f"Вы отписались от @{target_username}")

async def _handle_subscription_response(update: Update, message: str):
    if update.callback_query:
        await update.callback_query.message.edit_text(message)
    else:
        await update.message.reply_text(message)
